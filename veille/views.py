import logging
import re
import socket
from datetime import datetime, timezone as dt_timezone

import feedparser
import requests
from django.conf import settings
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Source, Article
from .serializers import SourceSerializer, ArticleSerializer

logger = logging.getLogger(__name__)

NVIDIA_URL = 'https://integrate.api.nvidia.com/v1/chat/completions'

SUMMARY_PROMPT = (
    "Resume cet article de cybersecurite en 2 a 3 phrases, en francais, de maniere "
    "factuelle. Reponds uniquement par le resume, sans introduction ni commentaire.\n\n"
)

# Au-dela, on gaspille des tokens sur le pied de page et les menus du site
MAX_ARTICLE_CHARS = 6000


class SourceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Source.objects.all()
    serializer_class = SourceSerializer


def strip_html(text):
    return re.sub('<[^<]+?>', '', text).strip()


def extract_page_text(html):
    """Texte lisible d'une page. Les blocs script/style/noscript sont retires avec leur
    contenu : ne supprimer que les balises laisserait passer du code et des noms de
    fichiers (c'est exactement ce qui avait pollue l'extraction OSINT)."""
    without_code = re.sub(r'(?is)<(script|style|noscript)\b.*?</\1>', ' ', html)
    return re.sub(r'\s+', ' ', strip_html(without_code)).strip()


def fetch_article_text(url):
    """Recupere le texte de l'article. Chaine vide si la page est injoignable."""
    try:
        response = requests.get(
            url, timeout=10, headers={'User-Agent': 'Mozilla/5.0 (centre-controle)'}
        )
        response.raise_for_status()
    except requests.RequestException:
        logger.warning("Page d'article injoignable : %s", url)
        return ''
    return extract_page_text(response.text)


class ArticleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

    @action(detail=True, methods=['post'])
    def summarize(self, request, pk=None):
        """Genere un resume francais de l'article via un modele NVIDIA."""
        article = self.get_object()

        # Deja resume : on ne repaie pas un appel pour le meme article
        if article.ai_summary:
            return Response(self.get_serializer(article).data)

        if not settings.NVIDIA_API_KEY or not settings.NVIDIA_MODEL:
            return Response(
                {'error': "NVIDIA_API_KEY ou NVIDIA_MODEL absent du fichier .env."},
                status=503,
            )

        text = fetch_article_text(article.link) or article.summary
        if not text:
            return Response(
                {'error': "Aucun texte exploitable : page injoignable et extrait RSS vide."},
                status=422,
            )

        try:
            response = requests.post(
                NVIDIA_URL,
                headers={'Authorization': f'Bearer {settings.NVIDIA_API_KEY}'},
                json={
                    'model': settings.NVIDIA_MODEL,
                    'messages': [
                        {'role': 'user', 'content': SUMMARY_PROMPT + text[:MAX_ARTICLE_CHARS]}
                    ],
                    'temperature': 0.3,
                    'max_tokens': 400,
                    # Sans ca, ce modele emet ~3700 caracteres de raisonnement avant de
                    # repondre : 14x plus lent et 12x plus de tokens pour le meme resume.
                    'chat_template_kwargs': {'thinking': False},
                },
                timeout=60,
            )
            response.raise_for_status()
            summary = response.json()['choices'][0]['message']['content'].strip()
        except (requests.RequestException, KeyError, ValueError, IndexError):
            logger.exception("Echec du resume de l'article %s", article.pk)
            return Response(
                {'error': "Le service de resume n'a pas repondu correctement."},
                status=502,
            )

        if not summary:
            return Response({'error': "Le modele a renvoye un resume vide."}, status=502)

        article.ai_summary = summary
        article.save(update_fields=['ai_summary'])
        return Response(self.get_serializer(article).data)


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
