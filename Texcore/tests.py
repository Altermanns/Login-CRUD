from django.test import TestCase, Client
from django.urls import reverse
from .models import Materia


class MateriaModelTest(TestCase):
    def test_str_representation(self):
        m = Materia.objects.create(tipo='Quimica', cantidad=5, lote='L-1')
        self.assertIn('L-1', str(m))


class MateriaViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Create a user and log in if necessary in the future.

    def test_listar_materias_view_unauthenticated_redirects(self):
        url = reverse('index_materia')
        response = self.client.get(url)
        # Should redirect to login (default Django behavior)
        self.assertIn(response.status_code, (301, 302))

