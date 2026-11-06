from django.test import TestCase
from django.urls import reverse


class CartilhasTests(TestCase):
    def test_pagina_de_cartilhas_carrega(self):
        resposta = self.client.get(reverse('homepage:cartilhas'))
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, 'Cartilhas do GID')

    def test_pagina_inicial_aponta_para_cartilhas(self):
        resposta = self.client.get(reverse('homepage:index'))
        self.assertContains(resposta, reverse('homepage:cartilhas'))
