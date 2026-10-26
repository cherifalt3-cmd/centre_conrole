import importlib
from unittest.mock import patch

from django.apps import apps
from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase
from rest_framework.test import APIClient

from .models import Target, normalize_address
from .serializers import TargetSerializer

# Le nom du module commence par un chiffre : import classique impossible
cleanup_migration = importlib.import_module('recon.migrations.0012_normalize_target_addresses')


class NormalizeAddressTests(SimpleTestCase):
    def test_domaine_nu(self):
        self.assertEqual(normalize_address('  Exemple.COM '), 'exemple.com')

    def test_chemin_et_requete_conserves(self):
        # /Admin et /admin peuvent etre deux ressources differentes sur le serveur
        self.assertEqual(
            normalize_address('HTTPS://Exemple.com/Admin/Login.php?id=AbC'),
            'https://exemple.com/Admin/Login.php?id=AbC',
        )

    def test_chemin_conserve_sans_schema(self):
        self.assertEqual(normalize_address('Exemple.com/Admin'), 'exemple.com/Admin')

    def test_identifiants_conserves(self):
        # Un mot de passe dans l'URL est sensible a la casse : seul l'hote change
        self.assertEqual(
            normalize_address('ftp://Admin:MotDePasse@FTP.Exemple.com/'),
            'ftp://Admin:MotDePasse@ftp.exemple.com/',
        )

    def test_adresse_ip(self):
        self.assertEqual(normalize_address(' 192.168.1.10 '), '192.168.1.10')


class TargetModelTests(TestCase):
    def test_tout_enregistrement_est_normalise(self):
        # L'admin et le shell passent par save(), pas par le serialiseur
        target = Target.objects.create(address='Exemple.COM/Admin')
        self.assertEqual(target.address, 'exemple.com/Admin')

    def test_validation_admin_sur_la_valeur_normalisee(self):
        # full_clean() est ce qu'appelle le formulaire de l'admin
        Target.objects.create(address='exemple.com')
        from django.core.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            Target(address='EXEMPLE.com').full_clean()


class CleanupMigrationTests(TestCase):
    def test_normalise_et_fusionne_les_doublons_existants(self):
        # bulk_create contourne save() : c'est l'etat d'une base remplie avant la regle
        Target.objects.bulk_create([
            Target(address='Exemple.com', notes='premiere note'),
            Target(address='exemple.com ', notes='seconde note'),
            Target(address='Autre.com/Chemin'),
        ])

        cleanup_migration.normalize_existing_targets(apps, None)

        addresses = sorted(Target.objects.values_list('address', flat=True))
        self.assertEqual(addresses, ['autre.com/Chemin', 'exemple.com'])
        merged = Target.objects.get(address='exemple.com')
        self.assertIn('premiere note', merged.notes)
        self.assertIn('seconde note', merged.notes)


class TargetAddressTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(User.objects.create_user('test', password='x'))

    def add(self, address):
        return self.client.post('/api/recon/targets/', {'address': address}, format='json')

    def test_normalise_espaces_et_casse(self):
        response = self.add('  Exemple.COM  ')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['address'], 'exemple.com')

    def test_refuse_un_doublon_qui_ne_differe_que_par_la_casse(self):
        self.add('exemple.com')
        response = self.add('EXEMPLE.com')
        # 400 avec un message clair, et non 500 sur une IntegrityError
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['address'][0], 'Cette cible est déjà dans le carnet.')
        self.assertEqual(Target.objects.count(), 1)

    def test_conserve_schema_et_chemin(self):
        # Contrairement a l'OSINT, le carnet peut noter une URL precise
        response = self.add('https://exemple.com/admin')
        self.assertEqual(response.data['address'], 'https://exemple.com/admin')

    def test_modifier_une_cible_sans_changer_son_adresse(self):
        # La cible ne doit pas se considerer comme son propre doublon
        target_id = self.add('exemple.com').data['id']
        response = self.client.patch(
            f'/api/recon/targets/{target_id}/',
            {'address': 'exemple.com', 'notes': 'mise a jour'},
            format='json',
        )
        self.assertEqual(response.status_code, 200)

    def test_modifier_vers_une_adresse_deja_prise(self):
        self.add('premiere.com')
        second_id = self.add('seconde.com').data['id']
        response = self.client.patch(
            f'/api/recon/targets/{second_id}/', {'address': 'PREMIERE.com'}, format='json'
        )
        self.assertEqual(response.status_code, 400)

    def test_conserve_la_casse_du_chemin(self):
        response = self.add('https://Exemple.com/Admin/Login.php?id=AbC')
        self.assertEqual(response.data['address'], 'https://exemple.com/Admin/Login.php?id=AbC')

    def test_double_clic_simultane_donne_400_et_non_500(self):
        # Simule deux requetes simultanees : la seconde passe le controle avant que
        # la premiere ait ecrit, et c'est la contrainte en base qui la refuse.
        self.add('exemple.com')
        with patch.object(TargetSerializer, 'validate_address', side_effect=normalize_address):
            response = self.add('exemple.com')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Target.objects.count(), 1)
