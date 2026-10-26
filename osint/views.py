from rest_framework import viewsets
from rest_framework.response import Response

from .models import Search
from .serializers import SearchSerializer
from .sources import collect, normalize_domain


class SearchViewSet(viewsets.ModelViewSet):
    queryset = Search.objects.all()
    serializer_class = SearchSerializer

    def create(self, request, *args, **kwargs):
        domain = normalize_domain(request.data.get('query', ''))
        if not domain:
            return Response({'error': 'query requis'}, status=400)

        # Les sources passives repondent en quelques secondes : pas besoin de job
        # asynchrone ni de polling, tout tient dans la requete.
        findings, failed = collect(domain)

        search = Search.objects.create(
            query=domain,
            query_type='domain',
            # En echec seulement si rien n'a pu etre collecte : une source qui tombe
            # pendant que les autres repondent reste un resultat exploitable.
            status='failed' if not findings else 'finished',
            findings=findings,
            error_message=(
                'Sources indisponibles : ' + ', '.join(sorted(failed)) if failed else ''
            ),
        )

        return Response(self.get_serializer(search).data, status=201)
