from django.test import SimpleTestCase

from .sources import _keep_subdomain, _parse_cymru, _parse_whois_text, normalize_domain


# Reponse reelle de whois.nic.dz pour poste.dz, telle que recue le 26/10/2026
NIC_DZ_RESPONSE = """% This is the WHOIS server for Example Registry.
% Queries are subject to terms of use.
%
Domain Name:    POSTE.DZ
Registrar:      wissal
Registrant:     Algerie Poste
Admin Name:    GUESMI Salem
Admin Email:      guesmi.salem@poste.dz
Tech Name:   GUESMI Salem
Tech Email:     guesmi.salem@poste.dz
Creation Date:  2002-10-07
Expiry Date:    N/A

% Query served at 2026-10-26T13:23:31.595970623+01:00
"""

# Reponse reelle de whois.cymru.com en mode bulk verbose
CYMRU_RESPONSE = """Bulk mode; whois.cymru.com [2026-10-26 12:29:47 +0000]
36459   | 140.82.121.4     | 140.82.121.0/24     | US | arin     | 2018-04-25 | GITHUB - GitHub, Inc., US
36947   | 41.111.0.1       | 41.111.0.0/20       | DZ | afrinic  | 2009-05-04 | Telecom Algeria - Telecom Algeria, DZ
"""


class NormalizeDomainTests(SimpleTestCase):
    def test_retire_schema_chemin_et_majuscules(self):
        self.assertEqual(normalize_domain('https://Exemple.COM/page?x=1'), 'exemple.com')

    def test_accepte_un_domaine_nu(self):
        self.assertEqual(normalize_domain('  exemple.com  '), 'exemple.com')

    def test_schema_en_majuscules(self):
        self.assertEqual(normalize_domain('HTTP://exemple.com'), 'exemple.com')

    def test_chaine_vide(self):
        self.assertEqual(normalize_domain(''), '')


class KeepSubdomainTests(SimpleTestCase):
    def test_retire_le_joker(self):
        self.assertEqual(_keep_subdomain('*.api.exemple.com', 'exemple.com'), 'api.exemple.com')

    def test_rejette_un_domaine_etranger(self):
        # Un certificat multi-domaines peut lister des noms sans rapport avec la cible
        self.assertEqual(_keep_subdomain('autre-site.org', 'exemple.com'), '')

    def test_normalise_la_casse(self):
        self.assertEqual(_keep_subdomain('WWW.Exemple.com', 'exemple.com'), 'www.exemple.com')


class ParseWhoisTextTests(SimpleTestCase):
    def setUp(self):
        self.parsed = _parse_whois_text(NIC_DZ_RESPONSE)

    def test_extrait_titulaire_et_contacts(self):
        self.assertEqual(self.parsed['registrant'], 'Algerie Poste')
        self.assertEqual(self.parsed['admin_email'], 'guesmi.salem@poste.dz')
        self.assertEqual(self.parsed['tech_name'], 'GUESMI Salem')

    def test_ignore_les_valeurs_na(self):
        # « Expiry Date: N/A » ne doit pas devenir une date affichee
        self.assertNotIn('expires', self.parsed)

    def test_garde_la_date_de_creation(self):
        self.assertEqual(self.parsed['created'], '2002-10-07')

    def test_ignore_commentaires_et_champs_inconnus(self):
        # « Domain Name » n'est pas mappe et les lignes % sont des commentaires
        self.assertNotIn('domain name', self.parsed)
        self.assertTrue(all(not key.startswith('%') for key in self.parsed))

    def test_cumule_plusieurs_serveurs_de_noms(self):
        parsed = _parse_whois_text('Name Server: NS1.EXEMPLE.DZ\nName Server: ns2.exemple.dz\n')
        self.assertEqual(parsed['nameservers'], ['ns1.exemple.dz', 'ns2.exemple.dz'])

    def test_reponse_vide(self):
        self.assertEqual(_parse_whois_text(''), {})


class ParseCymruTests(SimpleTestCase):
    def test_extrait_chaque_bloc(self):
        blocks = _parse_cymru(CYMRU_RESPONSE)
        self.assertEqual(len(blocks), 2)

        github = next(b for b in blocks if b['asn'] == '36459')
        self.assertEqual(github['prefix'], '140.82.121.0/24')
        self.assertEqual(github['country'], 'US')
        self.assertEqual(github['registry'], 'arin')
        self.assertEqual(github['ips'], ['140.82.121.4'])

    def test_ignore_la_banniere(self):
        # La premiere ligne « Bulk mode; ... » ne commence pas par un numero d'AS
        blocks = _parse_cymru(CYMRU_RESPONSE)
        self.assertTrue(all(b['asn'].isdigit() for b in blocks))

    def test_regroupe_les_ip_d_un_meme_prefixe(self):
        # Derriere un CDN, plusieurs adresses tombent dans le meme bloc :
        # il doit apparaitre une seule fois, avec toutes ses IP
        raw = (
            '13335 | 104.16.1.1 | 104.16.0.0/13 | US | arin | 2014-03-28 | CLOUDFLARENET, US\n'
            '13335 | 104.16.2.2 | 104.16.0.0/13 | US | arin | 2014-03-28 | CLOUDFLARENET, US\n'
        )
        blocks = _parse_cymru(raw)
        self.assertEqual(len(blocks), 1)
        self.assertEqual(blocks[0]['ips'], ['104.16.1.1', '104.16.2.2'])

    def test_reponse_vide(self):
        self.assertEqual(_parse_cymru(''), [])
