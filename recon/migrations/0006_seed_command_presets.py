from django.db import migrations

PRESETS = [
    # Général
    ("Général", "Découverte d'hôtes actifs (ping scan)", "nmap -sn {address}"),
    ("Général", "Découverte rapide des ports ouverts", "nmap -p- --min-rate=1000 -T4 {address}"),
    ("Général", "Version + scripts par défaut sur tous les ports", "nmap -sC -sV -p- {address}"),
    ("Général", "Scan agressif complet (OS + version + scripts + traceroute)", "nmap -A -p- {address}"),
    ("Général", "Scan furtif SYN", "nmap -sS {address}"),
    ("Général", "Scan UDP des ports les plus courants", "nmap -sU --top-ports 20 {address}"),
    ("Général", "Scan sans ping (ignorer la découverte d'hôte)", "nmap -Pn {address}"),
    ("Général", "Détection du système d'exploitation", "nmap -O {address}"),
    ("Général", "Scan rapide (ports les plus courants)", "nmap -F {address}"),
    ("Général", "Scan avec raison de l'état des ports", "nmap --reason -F {address}"),

    # SMB
    ("SMB", "Détection du service et version", "nmap -p 445 -sV {address}"),
    ("SMB", "Énumération des partages", "nmap -p 445 --script smb-enum-shares {address}"),
    ("SMB", "Énumération des utilisateurs", "nmap -p 445 --script smb-enum-users {address}"),
    ("SMB", "Découverte de l'OS via SMB", "nmap -p 445 --script smb-os-discovery {address}"),
    ("SMB", "Vérification de la signature SMB", "nmap -p 445 --script smb-security-mode {address}"),
    ("SMB", "Recherche de vulnérabilités connues", "nmap -p 445 --script smb-vuln* {address}"),
    ("SMB", "Test EternalBlue (MS17-010)", "nmap -p 445 --script smb-vuln-ms17-010 {address}"),
    ("SMB", "Énumération des sessions", "nmap -p 445 --script smb-enum-sessions {address}"),
    ("SMB", "Énumération des groupes", "nmap -p 445 --script smb-enum-groups {address}"),
    ("SMB", "Scan complet (ports 139 et 445)", "nmap -p 139,445 -sV --script smb-enum-shares,smb-enum-users,smb-os-discovery,smb-vuln* {address}"),

    # FTP
    ("FTP", "Détection du service et version", "nmap -p 21 -sV {address}"),
    ("FTP", "Test d'accès anonyme", "nmap -p 21 --script ftp-anon {address}"),
    ("FTP", "Bannière et infos système", "nmap -p 21 --script ftp-syst {address}"),
    ("FTP", "Vulnérabilité connue (ProFTPD CVE-2010-4221)", "nmap -p 21 --script ftp-vuln-cve2010-4221 {address}"),
    ("FTP", "Test de rebond FTP (bounce attack)", "nmap -p 21 --script ftp-bounce {address}"),
    ("FTP", "Brute force des identifiants", "nmap -p 21 --script ftp-brute {address}"),
    ("FTP", "Faille OPIE si applicable", "nmap -p 21 --script ftp-libopie {address}"),
    ("FTP", "Récupération de la bannière", "nmap -p 21 --script banner {address}"),
    ("FTP", "Scan complet (ports data + contrôle)", "nmap -p 20,21 -sV -sC {address}"),
    ("FTP", "Scan combiné (anonyme + système + vulnérabilités)", "nmap -p 21 --script ftp-anon,ftp-syst,ftp-vuln* {address}"),

    # SSH
    ("SSH", "Détection du service et version", "nmap -p 22 -sV {address}"),
    ("SSH", "Algorithmes supportés", "nmap -p 22 --script ssh2-enum-algos {address}"),
    ("SSH", "Clé d'hôte SSH", "nmap -p 22 --script ssh-hostkey {address}"),
    ("SSH", "Méthodes d'authentification acceptées", "nmap -p 22 --script ssh-auth-methods {address}"),
    ("SSH", "Brute force des identifiants", "nmap -p 22 --script ssh-brute {address}"),
    ("SSH", "Détection du support SSHv1 (obsolète)", "nmap -p 22 --script sshv1 {address}"),
    ("SSH", "Test d'acceptation de clé publique", "nmap -p 22 --script ssh-publickey-acceptance {address}"),
    ("SSH", "Récupération de la bannière", "nmap -p 22 --script banner {address}"),
    ("SSH", "Scripts par défaut + version", "nmap -p 22 -sC -sV {address}"),
    ("SSH", "Scan combiné (algos + clé + auth)", "nmap -p 22 --script ssh2-enum-algos,ssh-hostkey,ssh-auth-methods {address}"),

    # HTTP
    ("HTTP", "Détection du service et version", "nmap -p 80,443 -sV {address}"),
    ("HTTP", "Titre de la page", "nmap -p 80,443 --script http-title {address}"),
    ("HTTP", "En-têtes HTTP", "nmap -p 80,443 --script http-headers {address}"),
    ("HTTP", "Énumération de répertoires/fichiers courants", "nmap -p 80,443 --script http-enum {address}"),
    ("HTTP", "Méthodes HTTP autorisées", "nmap -p 80,443 --script http-methods {address}"),
    ("HTTP", "Contenu du robots.txt", "nmap -p 80,443 --script http-robots.txt {address}"),
    ("HTTP", "En-tête serveur (technologie)", "nmap -p 80,443 --script http-server-header {address}"),
    ("HTTP", "Certificat SSL et chiffrements", "nmap -p 443 --script ssl-cert,ssl-enum-ciphers {address}"),
    ("HTTP", "Recherche de vulnérabilités connues", "nmap -p 80,443 --script http-vuln* {address}"),
    ("HTTP", "Scripts par défaut + version", "nmap -p 80,443 -sC -sV {address}"),

    # SMTP
    ("SMTP", "Détection du service et version", "nmap -p 25 -sV {address}"),
    ("SMTP", "Commandes SMTP supportées", "nmap -p 25 --script smtp-commands {address}"),
    ("SMTP", "Énumération des utilisateurs (VRFY/EXPN)", "nmap -p 25 --script smtp-enum-users {address}"),
    ("SMTP", "Test de relais ouvert", "nmap -p 25 --script smtp-open-relay {address}"),
    ("SMTP", "Recherche de vulnérabilités connues", "nmap -p 25 --script smtp-vuln* {address}"),
    ("SMTP", "Récupération de la bannière", "nmap -p 25 --script banner {address}"),
    ("SMTP", "Scan des ports courants (dont soumission/SSL)", "nmap -p 25,465,587 -sV {address}"),
    ("SMTP", "Certificat SSL sur SMTPS", "nmap -p 465 --script ssl-cert {address}"),
    ("SMTP", "Infos NTLM (serveurs Exchange)", "nmap -p 25 --script smtp-ntlm-info {address}"),
    ("SMTP", "Scan combiné (commandes + utilisateurs + relais)", "nmap -p 25 --script smtp-commands,smtp-enum-users,smtp-open-relay {address}"),

    # SQL
    ("SQL", "Détection MySQL et version", "nmap -p 3306 -sV {address}"),
    ("SQL", "Infos serveur MySQL", "nmap -p 3306 --script mysql-info {address}"),
    ("SQL", "Test de mot de passe vide MySQL", "nmap -p 3306 --script mysql-empty-password {address}"),
    ("SQL", "Énumération des utilisateurs MySQL", "nmap -p 3306 --script mysql-enum {address}"),
    ("SQL", "Recherche de vulnérabilités MySQL connues", "nmap -p 3306 --script mysql-vuln* {address}"),
    ("SQL", "Détection MSSQL et infos serveur", "nmap -p 1433 -sV --script ms-sql-info {address}"),
    ("SQL", "Test de mot de passe vide MSSQL", "nmap -p 1433 --script ms-sql-empty-password {address}"),
    ("SQL", "Infos NTLM MSSQL", "nmap -p 1433 --script ms-sql-ntlm-info {address}"),
    ("SQL", "Détection PostgreSQL + brute force", "nmap -p 5432 -sV --script pgsql-brute {address}"),
    ("SQL", "Détection Oracle + brute force des SID", "nmap -p 1521 -sV --script oracle-sid-brute {address}"),
]


def seed_presets(apps, schema_editor):
    CommandPreset = apps.get_model('recon', 'CommandPreset')
    CommandPreset.objects.all().delete()

    for i, (category, label, template) in enumerate(PRESETS):
        CommandPreset.objects.create(
            label=label, category=category, phase='active', template=template, order=i,
        )


def remove_presets(apps, schema_editor):
    CommandPreset = apps.get_model('recon', 'CommandPreset')
    CommandPreset.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('recon', '0005_commandpreset_category'),
    ]

    operations = [
        migrations.RunPython(seed_presets, remove_presets),
    ]
