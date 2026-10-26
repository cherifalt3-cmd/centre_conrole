"""Sources OSINT passives.

Le principe : on interroge des tiers qui detiennent deja l'information publique sur
la cible, et jamais la cible elle-meme. Aucune de ces requetes n'apparait dans les
logs du domaine analyse.
"""

import logging
import re
import socket
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

logger = logging.getLogger(__name__)

TIMEOUT = 12
# crt.sh scanne un enorme jeu de donnees et depasse largement le timeout courant :
# il ne sert que de secours, avec sa propre marge.
CRTSH_TIMEOUT = 30
HEADERS = {'User-Agent': 'centre-controle/1.0'}

DOH_URL = 'https://cloudflare-dns.com/dns-query'
DNS_RECORD_TYPES = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'SOA']

WAYBACK_LIMIT = 80

# Team Cymru resout ASN et prefixe BGP pour plusieurs IP en une seule connexion
CYMRU_SERVER = 'whois.cymru.com'
MAX_IPS = 16

# bgp.he.net n'a pas d'API : on lit la table rendue cote serveur. Le site repond
# de facon irreguliere, d'ou les tentatives multiples, et il refuse les
# user-agents qui n'ont pas l'air d'un navigateur.
HE_AS_URL = 'https://bgp.he.net/AS{asn}'
HE_HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/141.0 Safari/537.36'
    )
}
HE_ATTEMPTS = 3
HE_BACKOFF = 1.5
MAX_ASNS = 4

# Registres qui ne publient pas de RDAP : on interroge leur WHOIS sur le port 43.
# Une ligne par extension suffit pour en ajouter d'autres.
WHOIS_SERVERS = {
    'dz': 'whois.nic.dz',
}

# Garde-fou : une reponse WHOIS legitime ne depasse jamais quelques kilo-octets
WHOIS_MAX_BYTES = 64 * 1024

# Correspondance entre les champs renvoyes par les WHOIS port 43 et nos cles
WHOIS_FIELD_MAP = {
    'registrar': 'registrar',
    'registrant': 'registrant',
    'admin name': 'admin_name',
    'admin email': 'admin_email',
    'tech name': 'tech_name',
    'tech email': 'tech_email',
    'creation date': 'created',
    'expiry date': 'expires',
    'name server': 'nameservers',
}


def normalize_domain(value):
    """exemple.com a partir de https://Exemple.com/page."""
    without_scheme = re.sub(r'^https?://', '', value.strip(), flags=re.IGNORECASE)
    return without_scheme.split('/')[0].strip().lower()


def _keep_subdomain(name, domain):
    cleaned = name.strip().lstrip('*.').lower()
    return cleaned if cleaned and cleaned.endswith(domain) else ''


def _subdomains_certspotter(domain):
    response = requests.get(
        'https://api.certspotter.com/v1/issuances',
        params={'domain': domain, 'include_subdomains': 'true', 'expand': 'dns_names'},
        headers=HEADERS,
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    return {
        kept
        for issuance in response.json()
        for name in issuance.get('dns_names', [])
        if (kept := _keep_subdomain(name, domain))
    }


def _subdomains_crtsh(domain):
    response = requests.get(
        'https://crt.sh/',
        params={'q': f'%.{domain}', 'output': 'json'},
        headers=HEADERS,
        timeout=CRTSH_TIMEOUT,
    )
    response.raise_for_status()
    return {
        kept
        for entry in response.json()
        # name_value peut contenir plusieurs noms separes par des retours a la ligne
        for name in entry.get('name_value', '').split('\n')
        if (kept := _keep_subdomain(name, domain))
    }


def fetch_subdomains(domain):
    """Sous-domaines via Certificate Transparency : tout certificat TLS emis est
    public, ce qui expose jusqu'aux sous-domaines qu'on croyait oublies (preprod,
    staging, admin...). certspotter repond en moins d'une seconde la ou crt.sh
    demande souvent plus de 12s, d'ou cet ordre."""
    try:
        return sorted(_subdomains_certspotter(domain))
    except (requests.RequestException, ValueError) as exc:
        logger.warning("certspotter indisponible (%s), repli sur crt.sh", exc)
        return sorted(_subdomains_crtsh(domain))


def _doh_query(name, record_type):
    response = requests.get(
        DOH_URL,
        params={'name': name, 'type': record_type},
        headers={**HEADERS, 'Accept': 'application/dns-json'},
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    return [answer['data'] for answer in response.json().get('Answer', [])]


def fetch_dns(domain):
    """Enregistrements DNS via le resolveur public de Cloudflare (DNS-over-HTTPS).
    MX revele l'hebergeur mail, TXT les services SaaS et la politique SPF."""
    records = {}

    for record_type in DNS_RECORD_TYPES:
        try:
            values = _doh_query(domain, record_type)
        except (requests.RequestException, ValueError, KeyError):
            continue
        if values:
            records[record_type] = values

    # DMARC ne vit pas sur le domaine mais sur un sous-domaine dedie
    try:
        dmarc = _doh_query(f'_dmarc.{domain}', 'TXT')
        if dmarc:
            records['DMARC'] = dmarc
    except (requests.RequestException, ValueError, KeyError):
        pass

    if not records:
        raise ValueError(f"Aucun enregistrement DNS pour {domain}")

    return records


def _vcard_value(entity, field):
    """Extrait un champ d'un vcardArray RDAP, dont la forme est
    ["vcard", [["version", {}, "text", "4.0"], ["fn", {}, "text", "Nom"]]]."""
    vcard = entity.get('vcardArray') or []
    if len(vcard) < 2 or not isinstance(vcard[1], list):
        return ''
    for item in vcard[1]:
        if isinstance(item, list) and len(item) >= 4 and item[0] == field:
            return item[3] if isinstance(item[3], str) else ''
    return ''


def _whois_query(server, payload):
    """Dialogue avec un serveur WHOIS historique (protocole texte, port 43)."""
    with socket.create_connection((server, 43), timeout=TIMEOUT) as connection:
        connection.sendall(payload.encode())
        chunks = []
        received = 0
        while received < WHOIS_MAX_BYTES:
            chunk = connection.recv(4096)
            if not chunk:
                break
            chunks.append(chunk)
            received += len(chunk)
    return b''.join(chunks).decode('utf-8', 'replace')


def _parse_whois_text(raw):
    """Transforme les lignes 'Cle: Valeur' en dictionnaire, en ignorant les
    commentaires (%) et les valeurs vides ou marquees N/A."""
    parsed = {}

    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith(('%', '#')) or ':' not in line:
            continue

        label, _, value = line.partition(':')
        key = WHOIS_FIELD_MAP.get(label.strip().lower())
        value = value.strip()
        if not key or not value or value.upper() in ('N/A', 'NONE', '-'):
            continue

        # Un registre peut lister plusieurs serveurs de noms sur des lignes separees
        if key == 'nameservers':
            parsed.setdefault(key, []).append(value.lower())
        else:
            parsed[key] = value

    return parsed


def fetch_whois(domain):
    """Informations d'enregistrement du domaine.

    La plupart des extensions passent par RDAP, mais beaucoup de ccTLD n'en
    proposent pas (rdap.org repond alors 'No RDAP service available'). Pour ceux-la
    on interroge directement le WHOIS du registre, qui expose souvent davantage :
    le .dz donne le registrant et les contacts admin/tech avec leurs emails, que
    les registres gTLD masquent.
    """
    tld = domain.rsplit('.', 1)[-1]
    if tld in WHOIS_SERVERS:
        parsed = _parse_whois_text(_whois_query(WHOIS_SERVERS[tld], f'{domain}\r\n'))
        if not parsed:
            raise ValueError(f"Reponse WHOIS illisible pour {domain}")
        parsed['source'] = WHOIS_SERVERS[tld]
        return parsed

    response = requests.get(
        f'https://rdap.org/domain/{domain}',
        headers={**HEADERS, 'Accept': 'application/rdap+json'},
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    data = response.json()

    registrar = ''
    for entity in data.get('entities', []):
        if 'registrar' in (entity.get('roles') or []):
            registrar = _vcard_value(entity, 'fn') or registrar

    events = {
        event.get('eventAction'): event.get('eventDate')
        for event in data.get('events', [])
    }

    nameservers = sorted(
        (ns.get('ldhName') or '').lower()
        for ns in data.get('nameservers', [])
        if ns.get('ldhName')
    )

    return {
        'registrar': registrar,
        'statuses': data.get('status') or [],
        'created': events.get('registration', ''),
        'expires': events.get('expiration', ''),
        'updated': events.get('last changed', ''),
        'nameservers': nameservers,
        'source': 'rdap.org',
    }


def fetch_wayback(domain):
    """URLs historiques connues d'Archive.org. Revele d'anciens endpoints et fichiers
    exposes, et c'est la copie d'Archive qu'on lit, jamais le site de la cible."""
    response = requests.get(
        'https://web.archive.org/cdx/search/cdx',
        params={
            'url': f'{domain}/*',
            'output': 'json',
            'fl': 'original',
            'collapse': 'urlkey',
            'limit': WAYBACK_LIMIT,
        },
        headers=HEADERS,
        timeout=TIMEOUT,
    )
    response.raise_for_status()

    rows = response.json()
    # La premiere ligne du CDX est l'en-tete des colonnes
    return [row[0] for row in rows[1:]] if len(rows) > 1 else []


def _parse_cymru(raw):
    """Regroupe les lignes Team Cymru par prefixe BGP. Plusieurs adresses d'un meme
    domaine tombent souvent dans le meme bloc : on l'affiche une fois, avec ses IP."""
    blocks = {}

    for line in raw.splitlines():
        parts = [part.strip() for part in line.split('|')]
        # Ecarte l'en-tete et la banniere : seules les lignes de donnees
        # commencent par un numero d'AS
        if len(parts) < 7 or not parts[0].isdigit():
            continue

        asn, ip, prefix, country, registry, allocated, as_name = parts[:7]
        block = blocks.setdefault(prefix, {
            'prefix': prefix,
            'asn': asn,
            'as_name': as_name,
            'country': country,
            'registry': registry,
            'allocated': allocated,
            'ips': [],
        })
        block['ips'].append(ip)

    return sorted(blocks.values(), key=lambda block: block['prefix'])


def fetch_ip_ranges(domain):
    """Plages d'adresses et systemes autonomes derriere le domaine.

    Dit si la cible heberge sur son propre espace d'adressage (surface d'attaque
    reelle) ou derriere un CDN mutualise. Team Cymru traite toutes les IP en une
    seule connexion (mode bulk), la ou une requete RDAP par adresse multiplierait
    les appels pour la meme information.
    """
    addresses = []
    for record_type in ('A', 'AAAA'):
        try:
            addresses.extend(_doh_query(domain, record_type))
        except (requests.RequestException, ValueError, KeyError):
            continue

    addresses = sorted({address for address in addresses if address})[:MAX_IPS]
    if not addresses:
        raise ValueError(f"Aucune adresse IP resolue pour {domain}")

    payload = 'begin\nverbose\n' + '\n'.join(addresses) + '\nend\n'
    blocks = _parse_cymru(_whois_query(CYMRU_SERVER, payload))
    if not blocks:
        raise ValueError(f"Reponse Team Cymru illisible pour {domain}")

    return blocks


def _get_with_retry(url, attempts, **kwargs):
    """GET avec plusieurs tentatives et attente doublee a chaque echec, pour les
    services qui repondent de facon irreguliere."""
    delay = HE_BACKOFF

    for attempt in range(1, attempts + 1):
        try:
            response = requests.get(url, **kwargs)
            response.raise_for_status()
            return response
        except requests.RequestException as exc:
            logger.warning("%s : tentative %s/%s en echec (%s)", url, attempt, attempts, exc)
            if attempt == attempts:
                raise
            time.sleep(delay)
            delay *= 2


def fetch_as_prefixes(asns):
    """Tous les prefixes annonces par les AS du domaine, via le BGP Toolkit de
    Hurricane Electric.

    Team Cymru ne donne que le bloc dans lequel tombe l'adresse du domaine ; HE
    donne l'integralite de l'espace annonce par l'organisation, IPv4 et IPv6.
    """
    blocks = []

    for asn in sorted(set(asns), key=int)[:MAX_ASNS]:
        response = _get_with_retry(
            HE_AS_URL.format(asn=asn),
            attempts=HE_ATTEMPTS,
            headers=HE_HEADERS,
            timeout=TIMEOUT,
        )
        # Les prefixes sont les cibles des liens /net/ de la table rendue
        prefixes = sorted({
            prefix for prefix in re.findall(r'href="/net/([^"]+)"', response.text)
        })
        if prefixes:
            blocks.append({'asn': asn, 'prefixes': prefixes})

    if not blocks:
        raise ValueError("Aucun prefixe lisible sur bgp.he.net")

    return blocks


SOURCES = {
    'subdomains': fetch_subdomains,
    'dns': fetch_dns,
    'ip_ranges': fetch_ip_ranges,
    'whois': fetch_whois,
    'wayback': fetch_wayback,
}


def collect(domain):
    """Interroge toutes les sources en parallele et renvoie (resultats, sources_en_echec).

    Le parallelisme n'est pas cosmetique : en sequentiel, quatre sources a 12s de
    timeout peuvent faire attendre pres d'une minute. Une source qui echoue n'empeche
    jamais les autres de rendre leur resultat.
    """
    findings = {}
    failed = []

    with ThreadPoolExecutor(max_workers=len(SOURCES)) as pool:
        futures = {pool.submit(func, domain): name for name, func in SOURCES.items()}
        for future in as_completed(futures):
            name = futures[future]
            try:
                findings[name] = future.result()
            except Exception:
                logger.exception("Source OSINT '%s' en echec pour %s", name, domain)
                failed.append(name)

    # Seconde phase : bgp.he.net a besoin des ASN que Team Cymru vient de trouver.
    # Cette dependance est reelle, on la modelise plutot que de resoudre deux fois.
    asns = [block['asn'] for block in findings.get('ip_ranges', [])]
    if asns:
        try:
            findings['as_prefixes'] = fetch_as_prefixes(asns)
        except Exception:
            logger.exception("Source OSINT 'as_prefixes' en echec pour %s", domain)
            failed.append('as_prefixes')

    return findings, failed
