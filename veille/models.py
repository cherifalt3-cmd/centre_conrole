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
    title = models.CharField(max_length=500)
    link = models.URLField(unique=True)
    summary = models.TextField(blank=True)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    fetched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-published_at']

    def __str__(self):
        return self.title
