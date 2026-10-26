from datetime import datetime, timezone

from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase
from rest_framework.test import APIClient

from .models import Article, Source
from .views import detect_severity, extract_page_text


class DetectSeverityTests(SimpleTestCase):
    def test_seuils_de_l_echelle_cvss(self):
        self.assertEqual(detect_severity('CVSS score: 9.8'), 'critical')
        self.assertEqual(detect_severity('CVSS score: 9.0'), 'critical')
        self.assertEqual(detect_severity('CVSS score: 8.9'), 'high')
        self.assertEqual(detect_severity('CVSS score: 7.0'), 'high')
        self.assertEqual(detect_severity('CVSS score: 5.3'), 'medium')
        self.assertEqual(detect_severity('CVSS score: 2.1'), 'low')

    def test_retient_le_score_le_plus_eleve(self):
        # Un article qui cite plusieurs failles est classe selon la pire
        text = 'CVSS score: 4.3 pour la premiere, CVSS score: 9.1 pour la seconde'
        self.assertEqual(detect_severity(text), 'critical')

    def test_accepte_la_version_et_la_casse(self):
        self.assertEqual(detect_severity('cvss v3.1 score 8.1'), 'high')

    def test_sans_score_pas_de_gravite(self):
        self.assertEqual(detect_severity('Une faille sans score publie'), '')


class ExtractPageTextTests(SimpleTestCase):
    def test_retire_le_code_avec_son_contenu(self):
        # Retirer seulement les balises laisserait passer le code et les noms de
        # fichiers : c'est ce qui avait pollue l'extraction OSINT avec logo@2x.png
        html = (
            '<p>Texte utile.</p>'
            '<script>var secret = "ne-doit-pas-sortir";</script>'
            '<style>.x { color: red; }</style>'
            '<noscript><img src="logo@2x.png"></noscript>'
        )
        text = extract_page_text(html)
        self.assertEqual(text, 'Texte utile.')

    def test_compacte_les_espaces(self):
        self.assertEqual(extract_page_text('<p>a</p>\n\n   <p>b</p>'), 'a b')


class ArticleApiTests(TestCase):
    """L'interface depend de la forme exacte de ces reponses : pagination, filtres
    cote serveur et endpoint de statistiques du tableau de bord."""

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(User.objects.create_user('test', password='x'))

        cyber = Source.objects.create(name='Cyber', url='https://a.test/rss', category='cybersecurity')
        ai = Source.objects.create(name='IA', url='https://b.test/rss', category='ai')

        for index in range(35):
            Article.objects.create(
                source=cyber,
                title=f'Article {index}',
                link=f'https://a.test/{index}',
                severity='critical' if index < 3 else '',
                published_at=datetime(2026, 1, 1 + index % 28, tzinfo=timezone.utc),
            )
        Article.objects.create(
            source=ai, title='Le plus recent', link='https://b.test/1',
            published_at=datetime(2026, 6, 1, tzinfo=timezone.utc),
        )

    def test_la_liste_est_paginee(self):
        response = self.client.get('/api/veille/articles/')
        self.assertEqual(response.data['count'], 36)
        self.assertEqual(len(response.data['results']), 30)
        self.assertIsNotNone(response.data['next'])

    def test_les_filtres_s_appliquent_avant_la_pagination(self):
        # Filtrer une page deja chargee ne chercherait que dans ses 30 articles
        response = self.client.get('/api/veille/articles/?severity=critical')
        self.assertEqual(response.data['count'], 3)

        response = self.client.get('/api/veille/articles/?category=ai')
        self.assertEqual(response.data['count'], 1)

    def test_statistiques_du_tableau_de_bord(self):
        response = self.client.get('/api/veille/articles/stats/')
        self.assertEqual(response.data['total'], 36)
        self.assertEqual(response.data['critical'], 3)
        self.assertEqual(response.data['latest_title'], 'Le plus recent')

    def test_les_articles_sans_date_passent_en_dernier(self):
        Article.objects.create(
            source=Source.objects.first(), title='Sans date', link='https://a.test/nodate',
        )
        response = self.client.get('/api/veille/articles/stats/')
        self.assertEqual(response.data['latest_title'], 'Le plus recent')

    def test_authentification_requise(self):
        anonymous = APIClient()
        self.assertEqual(anonymous.get('/api/veille/articles/').status_code, 401)
