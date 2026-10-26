from urllib.parse import urlsplit, urlunsplit

from django.db import migrations


def _normalize(value):
    # Copie figee de recon.models.normalize_address : une migration ne doit pas
    # changer de comportement si la fonction du modele evolue plus tard.
    value = value.strip()
    if '://' in value:
        parts = urlsplit(value)
        userinfo, at, hostport = parts.netloc.rpartition('@')
        netloc = f'{userinfo}{at}{hostport.lower()}'
        return urlunsplit((parts.scheme.lower(), netloc, parts.path, parts.query, parts.fragment))
    host, separator, rest = value.partition('/')
    return f'{host.lower()}{separator}{rest}'


def normalize_existing_targets(apps, schema_editor):
    """Normalise les cibles enregistrees avant la regle, et fusionne celles qui
    deviennent identiques une fois normalisees.

    Les doublons sont supprimes AVANT de renommer la cible conservee : renommer
    d'abord heurterait la contrainte d'unicite deja en place.
    """
    Target = apps.get_model('recon', 'Target')

    groups = {}
    for target in Target.objects.order_by('date_added', 'id'):
        groups.setdefault(_normalize(target.address), []).append(target)

    for normalized, targets in groups.items():
        keeper, duplicates = targets[0], targets[1:]

        extra_notes = [d.notes for d in duplicates if d.notes and d.notes != keeper.notes]
        for duplicate in duplicates:
            duplicate.delete()

        if extra_notes:
            keeper.notes = '\n\n'.join([keeper.notes, *extra_notes]).strip()
        if keeper.address != normalized or extra_notes:
            keeper.address = normalized
            keeper.save(update_fields=['address', 'notes'])


class Migration(migrations.Migration):

    dependencies = [
        ('recon', '0011_alter_commandpreset_template_alter_target_address'),
    ]

    operations = [
        migrations.RunPython(normalize_existing_targets, migrations.RunPython.noop),
    ]
