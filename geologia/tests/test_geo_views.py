from django.urls import reverse
from model_mommy import mommy
from rest_framework.test import APITestCase

from budget_execution.models import Execucao
from geologia.serializers import GeologiaSerializer


class TestHomeView(APITestCase):

    def get(self, programa=None):
        if programa:
            url = '{}?programa={}'.format(reverse('geologia:home'), programa)
        else:
            url = reverse('geologia:home')
        return self.client.get(url)

    def test_serializes_geologia_data(self):
        mommy.make(Execucao, _quantity=3)
        execucoes = Execucao.objects.all()
        serializer = GeologiaSerializer(execucoes)

        response = self.get()
        assert serializer.data == response.data
