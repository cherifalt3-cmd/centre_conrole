from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Target


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
