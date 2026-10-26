from django.db import models


class Source(models.Model):
    CATEGORY_CHOICES = [
        ('cybersecurity', 'Cybersécurité'),
        ('ai', 'IA'),
    ]

    name = models.CharField(max_length=150)
    url = models.URLField(help_text="Adresse du flux RSS/Atom")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)

    def __str__(self):
        return self.name


class Article(models.Model):
    SEVERITY_CHOICES = [
        ('critical', 'Critique'),
        ('high', 'Élevée'),
        ('medium', 'Moyenne'),
        ('low', 'Faible'),
    ]

    source = models.ForeignKey(Source, related_name='articles', on_delete=models.CASCADE)
    # TextField et non CharField : le titre vient d'un flux RSS externe dont rien ne
    # borne la longueur. SQLite tolere un depassement, PostgreSQL leve DataError
    # et ferait echouer toute l'actualisation.
    title = models.TextField()
    link = models.URLField(unique=True)
    summary = models.TextField(blank=True, help_text="Extrait fourni par le flux RSS")
    ai_summary = models.TextField(blank=True, help_text="Resume genere en francais, a la demande")
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    fetched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # nulls_last explicite : SQLite range les dates nulles en fin de tri
        # descendant, PostgreSQL au debut, ou elles passeraient devant tout le reste.
        # '-id' departage les ex aequo (meme date, ou pas de date) : sans cle unique,
        # la base peut les renvoyer dans un ordre different a chaque requete, et la
        # pagination affiche alors des doublons tout en sautant d'autres articles.
        ordering = [models.F('published_at').desc(nulls_last=True), '-id']
        indexes = [
            # Index simple et non fonctionnel : SQLite refuse NULLS LAST dans un
            # CREATE INDEX. Comme il range NULL en plus petite valeur, un parcours
            # a l'envers de cet index donne deja DESC NULLS LAST. A revoir en cas
            # de passage a PostgreSQL, dont le parcours inverse donne NULLS FIRST.
            models.Index(fields=['published_at'], name='article_published'),
            # Filtre de gravite, applique cote serveur depuis la pagination
            models.Index(fields=['severity'], name='article_severity'),
        ]

    def __str__(self):
        return self.title
