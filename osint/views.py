import logging

from django.conf import settings
from rest_framework import viewsets
from rest_framework.response import Response
from scrapinghub import ScrapinghubClient

from .models import Search
from .serializers import SearchSerializer

logger = logging.getLogger(__name__)

DIAGNOSTIC_MESSAGES = {
    'robots_blocked': "Le site interdit l'exploration via robots.txt.",
    'unreachable': "Le site n'a pas répondu (injoignable ou trop lent).",
}


def get_project():
    client = ScrapinghubClient(settings.SCRAPY_CLOUD_API_KEY)
    return client.get_project(settings.SCRAPY_CLOUD_PROJECT_ID)


class SearchViewSet(viewsets.ModelViewSet):
    queryset = Search.objects.all()
    serializer_class = SearchSerializer

    def create(self, request, *args, **kwargs):
        query = request.data.get('query', '').strip()
        if not query:
            return Response({'error': 'query requis'}, status=400)

        search = Search.objects.create(query=query, query_type='domain', status='pending')

        try:
            project = get_project()
            job = project.jobs.run('osint', job_args={'target': query})
            search.job_key = job.key
            search.status = 'running'
            search.save()
        except Exception as e:
            logger.exception("Échec du lancement du job OSINT pour %r", query)
            search.status = 'failed'
            search.error_message = str(e)[:255]
            search.save()

        serializer = self.get_serializer(search)
        return Response(serializer.data, status=201)

    def retrieve(self, request, *args, **kwargs):
        search = self.get_object()

        if search.status == 'running' and search.job_key:
            try:
                project = get_project()
                job = project.jobs.get(search.job_key)
                state = job.metadata.get('state')

                if state == 'finished':
                    search.results = list(job.items.iter())

                    stats = job.metadata.get('scrapystats') or {}
                    if stats.get('robotstxt/forbidden'):
                        search.error_message = DIAGNOSTIC_MESSAGES['robots_blocked']
                    elif (
                        any(k.startswith('downloader/exception_type_count/') for k in stats)
                        and not stats.get('response_received_count')
                    ):
                        search.error_message = DIAGNOSTIC_MESSAGES['unreachable']

                    search.status = 'finished'
                    search.save()
                elif state == 'deleted':
                    search.status = 'failed'
                    search.error_message = "Le job a été supprimé sur Scrapy Cloud."
                    search.save()
            except Exception:
                logger.exception("Échec de la vérification du job OSINT %s", search.job_key)

        serializer = self.get_serializer(search)
        return Response(serializer.data)
