from django.db import models


class Target(models.Model):
    name = models.CharField(max_length=255, blank=True, help_text="Nom donné à la cible (facultatif)")
    address = models.CharField(max_length=255, help_text="Adresse IP ou domaine")
    date_added = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.name or self.address


class Tool(models.Model):
    PHASE_CHOICES = [
        ('passive', 'Passive'),
        ('active', 'Active'),
    ]

    name = models.CharField(max_length=100)
    base_command = models.CharField(max_length=100, help_text="Ex : nmap")
    phase = models.CharField(max_length=10, choices=PHASE_CHOICES)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Catalog(models.Model):
    """Une liste cherchable réutilisable (ex : scripts NSE de nmap)."""
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class CatalogEntry(models.Model):
    catalog = models.ForeignKey(Catalog, related_name='entries', on_delete=models.CASCADE)
    value = models.CharField(max_length=200, help_text="Ex : snmp-info")
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.value


class ToolOption(models.Model):
    TYPE_CHOICES = [
        ('switch', 'Interrupteur (on/off)'),
        ('single_choice', 'Choix unique'),
        ('free_value', 'Valeur libre'),
        ('multi_choice', 'Choix multiple'),
    ]

    tool = models.ForeignKey(Tool, related_name='options', on_delete=models.CASCADE)
    label = models.CharField(max_length=100, help_text="Nom affiché, ex : Détection de version")
    flag = models.CharField(
        max_length=50, blank=True,
        help_text="Ex : -sV ou --script= (laisser vide si chaque choix a son propre flag)",
    )
    option_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    help_text = models.CharField(max_length=255, blank=True)
    catalog = models.ForeignKey(
        Catalog, null=True, blank=True, on_delete=models.SET_NULL,
        help_text="Catalogue cherchable à proposer (seulement utile pour le type 'valeur libre')",
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.tool.name} — {self.label}"


class ToolOptionChoice(models.Model):
    """Une valeur possible pour une option de type 'choix unique' ou 'choix multiple'."""
    option = models.ForeignKey(ToolOption, related_name='choices', on_delete=models.CASCADE)
    value = models.CharField(max_length=100, help_text="Ex : -sS")
    label = models.CharField(max_length=150, help_text="Ex : TCP SYN scan")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.label
