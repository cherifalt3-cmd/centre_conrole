import re
import socket
from datetime import datetime, timezone as dt_timezone

import feedparser
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Source, Article
from .serializers import SourceSerializer, ArticleSerializer


class SourceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Source.objects.all()
    serializer_class = SourceSerializer


class ArticleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer


def strip_html(text):
    return re.sub('<[^<]+?>', '', text).strip()


CVSS_PATTERN = re.compile(r'cvss(?:\s*v[\d.]+)?\s*score:?\s*([\d.]+)', re.IGNORECASE)


def detect_severity(text):
    """Repère le score CVSS le plus élevé mentionné dans le texte et en déduit une gravité."""
    scores = [float(m) for m in CVSS_PATTERN.findall(text)]
    if not scores:
        return ''

    top = max(scores)
    if top >= 9.0:
        return 'critical'
    if top >= 7.0:
        return 'high'
    if top >= 4.0:
        return 'medium'
    return 'low'


class RefreshFeedsView(APIView):
    """Va chercher les derniers articles de chaque source RSS et les enregistre."""

    def post(self, request):
        created_count = 0
        failed_sources = []

        # Empêche un flux lent/bloqué de faire attendre la requête indéfiniment
        previous_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(10)

        for source in Source.objects.all():
            try:
                parsed = feedparser.parse(source.url)
            except Exception:
                failed_sources.append(source.name)
                continue

            for entry in parsed.entries:
                link = entry.get('link')
                if not link:
                    continue

                published_at = None
                if entry.get('published_parsed'):
                    published_at = datetime(*entry.published_parsed[:6], tzinfo=dt_timezone.utc)

                title = strip_html(entry.get('title', ''))
                summary = strip_html(entry.get('summary', ''))

                _, created = Article.objects.get_or_create(
                    link=link,
                    defaults={
                        'source': source,
                        'title': title,
                        'summary': summary,
                        'severity': detect_severity(f'{title} {summary}'),
                        'published_at': published_at,
                    },
                )
                if created:
                    created_count += 1

        socket.setdefaulttimeout(previous_timeout)

        return Response({'created': created_count, 'failed_sources': failed_sources})
