from django.db import models


class Search(models.Model):
    QUERY_TYPE_CHOICES = [
        ('domain', 'Domaine'),
    ]

    STATUS_CHOICES = [
        ('finished', 'Terminé'),
        ('failed', 'Échec'),
    ]

    query = models.CharField(max_length=255)
    query_type = models.CharField(max_length=20, choices=QUERY_TYPE_CHOICES, default='domain')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='finished')
    findings = models.JSONField(default=dict, blank=True, help_text="Resultats par source")
    error_message = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.query
