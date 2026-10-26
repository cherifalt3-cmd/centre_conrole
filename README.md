# Centre de contrôle

Application web personnelle regroupant plusieurs outils de cybersécurité et de
productivité sous un même compte et une même base de données. Usage local.

## Modules

| Module | État | Description |
|---|---|---|
| **Carnet de cibles** | ✅ | Enregistrement des cibles (IP ou domaine) avec notes |
| **Générateur de commandes** | ✅ | Construit des commandes de reconnaissance (nmap, whois, dig, theHarvester, Metasploit…) à copier dans un terminal. Ne les exécute jamais : il produit du texte. |
| **OSINT automatique** | ✅ | Empreinte publique d'un domaine, collectée **passivement** |
| **Veille cybersécu & IA** | ✅ | Agrégation de flux RSS, détection de gravité CVSS, résumé en français à la demande |
| **Kanban projets** | ✅ | Tableau à colonnes, intégré à l'accueil |
| **Suivi de conso** | ⏳ | Non construit |

### À propos du module OSINT

Il interroge six sources tierces en parallèle et **ne contacte jamais le domaine
analysé** — rien n'apparaît dans ses journaux :

- **Sous-domaines** — Certificate Transparency (certspotter, crt.sh en secours)
- **DNS** — A/AAAA/MX/NS/TXT/SOA et DMARC, via DNS-over-HTTPS
- **Plages d'adresses** — ASN et préfixes BGP (Team Cymru)
- **Espace d'adressage annoncé** — tous les préfixes des AS (bgp.he.net)
- **Enregistrement du domaine** — RDAP, ou le WHOIS du registre pour les
  extensions qui n'ont pas de RDAP (`.dz` via `whois.nic.dz`)
- **Historique des URLs** — Wayback Machine

Aucune clé d'API n'est nécessaire pour ces sources.

Une nuance honnête : la résolution DNS passe par un résolveur public, qui fait
lui-même une requête récursive atteignant les serveurs de noms de la cible. La
requête n'est jamais attribuable à toi, mais au sens strict ce n'est pas « zéro
paquet ».

## Pile technique

- **Backend** — Django 6.1 + Django REST Framework, authentification par token
- **Frontend** — Vue 3 (`<script setup>`), sans TypeScript, routeur ni Pinia
- **Base de données** — SQLite en local

## Installation

Prérequis : Python 3.14 et Node 22.

### Backend

```bash
git clone git@github.com:cherifalt3-cmd/centre_conrole.git
cd centre_control

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Crée un fichier `.env` à la racine (il est ignoré par git) :

```
SECRET_KEY=une-cle-secrete-generee
NVIDIA_API_KEY=nvapi-...
NVIDIA_MODEL=nvidia/nemotron-3.5-lightning-30b-a3b
```

Pour générer la clé secrète sans l'afficher à l'écran :

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(f'SECRET_KEY={get_random_secret_key()}')" >> .env
```

Puis :

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Frontend

Dans un second terminal :

```bash
cd frontend
npm install
npm run dev
```

L'interface est sur `http://localhost:5173`, l'API sur `http://localhost:8000`.
Connecte-toi avec le superutilisateur créé plus haut.

## Variables d'environnement

| Variable | Requise | Rôle |
|---|---|---|
| `SECRET_KEY` | oui | Clé de signature Django. L'application refuse de démarrer sans elle. |
| `NVIDIA_API_KEY` | non | Résumés d'articles dans la veille. Sans elle, le reste fonctionne et le bouton « Résumer » renvoie une erreur explicite. Clé gratuite sur build.nvidia.com. |
| `NVIDIA_MODEL` | non | Identifiant du modèle. Dans l'environnement plutôt que dans le code, parce que NVIDIA retire régulièrement des modèles. |
| `DJANGO_DEBUG` | non | `True` par défaut. Passe à `False` pour désactiver les pages d'erreur détaillées. |

## Données de départ

`python manage.py migrate` installe les ~90 commandes préenregistrées du
générateur (semées par migrations).

En revanche, **deux choses sont à créer à la main** via l'admin Django
(`http://localhost:8000/admin/`) sur une installation neuve :

- les **sources RSS** de la veille (modèle `Source` : un nom, l'URL du flux, et
  la catégorie cybersécurité ou IA) ;
- un **tableau Kanban** avec ses colonnes (modèles `Board` puis `Column`).

## Notes

- L'application est prévue pour tourner en local. `runserver` n'écoute que sur
  `127.0.0.1`, et `DEBUG` est actif par défaut : ne l'expose pas en l'état.
- Le générateur de commandes ne lance aucune commande système. Il assemble des
  chaînes de caractères que tu copies dans ton propre terminal.
- N'utilise ces outils que sur des systèmes que tu es autorisé à tester.
