from django.db import models


class Target(models.Model):
    name = models.CharField(max_length=255, blank=True, help_text="Nom donné à la cible (facultatif)")
    address = models.CharField(max_length=255, help_text="Adresse IP ou domaine")
    date_added = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.name or self.address
