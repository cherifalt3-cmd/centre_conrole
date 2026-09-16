from django.db import migrations

NEW_PRESETS = [
    # Général
    ("Général", "Test de connectivité (ping)", "ping -c 4 {address}"),

    # SMB
    ("SMB", "Versions du protocole SMB supportées", "nmap -p445 --script smb-protocols {address}"),
    ("SMB", "Statistiques du serveur", "nmap -p445 --script smb-server-stats {address}"),
    ("SMB", "Énumération des domaines", "nmap -p445 --script smb-enum-domains {address}"),
    ("SMB", "Énumération RPC en session nulle (utilisateurs, groupes, partages)", 'rpcclient -U "" -N {address}'),
    ("SMB", "Énumération automatique complète (enum4linux)", "enum4linux -a {address}"),
    (
        "SMB",
        "Spray d'identifiants (crackmapexec)",
        "crackmapexec smb {address} -u /root/users.txt -p /usr/share/metasploit-framework/data/wordlists/unix_passwords.txt",
    ),

    # FTP
    ("FTP", "Connexion interactive (test anonyme manuel)", "ftp {address}"),

    # HTTP
    ("HTTP", "Fingerprinting des technologies (whatweb)", "whatweb {address}"),
    ("HTTP", "Vérification du robots.txt", "curl {address}/robots.txt"),
    ("HTTP", "Brute-force de répertoires (gobuster)", "gobuster dir -u {address} -w /usr/share/wordlists/dirb/common.txt"),
    ("HTTP", "Brute-force de répertoires récursif (dirb)", "dirb {address}"),
    (
        "HTTP",
        "Recherche de fichiers de sauvegarde oubliés",
        "gobuster dir -u {address} -w /usr/share/wordlists/dirb/common.txt -x bak,old,txt,zip,env",
    ),
    ("HTTP", "Aspiration complète du site (httrack)", "httrack {address} -O site_miroir"),

    # SMTP
    ("SMTP", "Récupération manuelle de la bannière (netcat)", "nc {address} 25"),
    (
        "SMTP",
        "Énumération d'utilisateurs (smtp-user-enum)",
        "smtp-user-enum -U /usr/share/commix/src/txt/usernames.txt -t {address}",
    ),

    # SQL
    ("SQL", "Connexion interactive MySQL", "mysql -h {address} -u root -p"),
]


def seed_more_presets(apps, schema_editor):
    CommandPreset = apps.get_model('recon', 'CommandPreset')
    start = CommandPreset.objects.count()

    for i, (category, label, template) in enumerate(NEW_PRESETS):
        CommandPreset.objects.create(
            label=label, category=category, phase='active', template=template, order=start + i,
        )


def remove_more_presets(apps, schema_editor):
    CommandPreset = apps.get_model('recon', 'CommandPreset')
    templates = [template for _, _, template in NEW_PRESETS]
    CommandPreset.objects.filter(template__in=templates).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('recon', '0006_seed_command_presets'),
    ]

    operations = [
        migrations.RunPython(seed_more_presets, remove_more_presets),
    ]
