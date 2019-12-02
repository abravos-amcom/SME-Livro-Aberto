import pytest
import requests

from datetime import date
from unittest import TestCase
from unittest.mock import patch

from model_mommy import mommy

from regionalizacao.dao.eol_api_dao import (
    update_dre_table,
    update_escola_table,
    update_tipo_escola_table,
)
from regionalizacao.models import (
    Distrito, Dre, Escola, TipoEscola, EscolaInfo)


@pytest.mark.django_db
class TestUpdateDreTable(TestCase):

    def dres_fixture(self):
        return {
            "results": [
                {
                    "dre": "BT",
                    "diretoria": "DIRETORIA REGIONAL DE EDUCACAO BUTANTA",
                },
                {
                    "dre": "SA",
                    "diretoria": "DIRETORIA REGIONAL DE EDUCACAO SANTO AMARO"
                },
            ],
        }

    @patch.object(requests, 'get')
    def test_populate_dre_table(self, mock_get):
        api_return = self.dres_fixture()
        mock_get.return_value = api_return

        created, updated = update_dre_table()
        assert 2 == created
        assert 0 == updated

        dres = Dre.objects.all().order_by('code')
        assert 2 == dres.count()

        for dre, expected in zip(dres, api_return['results']):
            assert dre.code == expected['dre']
            assert dre.name == expected['diretoria']

    @patch.object(requests, 'get')
    def test_updates_existing_dre(self, mock_get):
        mommy.make(Dre, code="BT", name="old name")

        api_return = self.dres_fixture()
        mock_get.return_value = api_return

        created, updated = update_dre_table()
        assert 1 == created
        assert 1 == updated

        dres = Dre.objects.all().order_by('code')
        assert 2 == dres.count()

        for dre, expected in zip(dres, api_return['results']):
            assert dre.code == expected['dre']
            assert dre.name == expected['diretoria']


@pytest.mark.django_db
class TestUpdateTipoEscolaTable(TestCase):

    def tipos_escola_fixture(self):
        return {
            "results": [
                {
                    "tipoesc": "CIEJA",
                },
                {
                    "tipoesc": "MOVA",
                },
            ],
        }

    @patch.object(requests, 'get')
    def test_populate_tipo_escola_table(self, mock_get):
        api_return = self.tipos_escola_fixture()
        mock_get.return_value = api_return

        created = update_tipo_escola_table()
        assert 2 == created

        tipos = TipoEscola.objects.all().order_by('code')
        assert 2 == tipos.count()

        for tipo, expected in zip(tipos, api_return['results']):
            assert tipo.code == expected['tipoesc']

    @patch.object(requests, 'get')
    def test_ignores_when_tipo_already_exist(self, mock_get):
        mommy.make(TipoEscola, code="CIEJA")

        api_return = self.tipos_escola_fixture()
        mock_get.return_value = api_return

        created = update_tipo_escola_table()
        assert 1 == created

        tipos = TipoEscola.objects.all().order_by('code')
        assert 2 == tipos.count()

        for tipo, expected in zip(tipos, api_return['results']):
            assert tipo.code == expected['tipoesc']


@pytest.mark.django_db
class TestUpdateEscolaTable(TestCase):

    def escolas_fixture(self):
        return {
            "results": [
                {
                  "dre": "BT",
                  "codesc": "000191",
                  "tipoesc": "EMEF",
                  "nomesc": "ALIPIO CORREA NETO, PROF",
                  "diretoria": "DIRETORIA REGIONAL DE EDUCACAO BUTANTA",
                  "endereco": "Avenida JOAO CAIAFFA",
                  "numero": "140   ",
                  "bairro": "JARDIM TABOAO",
                  "cep": 5742100,
                  "situacao": "ATIVA",
                  "coddist": "94",
                  "distrito": "VILA SONIA",
                  "rede": "DIR",
                  "latitude": -23.612237,
                  "longitude": -46.749888,
                  "total_vagas": 502
                },
                {
                  "dre": "BT",
                  "codesc": "000477",
                  "tipoesc": "EMEF",
                  "nomesc": "PROFA. EDA TEREZINHA CHICA MEDEIROS",
                  "diretoria": "DIRETORIA REGIONAL DE EDUCACAO BUTANTA",
                  "endereco": "Rua ENGENHEIRO HUGO TAKAHASHI",
                  "numero": "333   ",
                  "bairro": "RAPOSO TAVARES",
                  "cep": 5563120,
                  "situacao": "ATIVA",
                  "coddist": "65",
                  "distrito": "RAPOSO TAVARES",
                  "rede": "DIR",
                  "latitude": -23.602076,
                  "longitude": -46.783825,
                  "total_vagas": 670
                },
            ],
        }

    @patch.object(requests, 'get')
    def test_populate_escola_table(self, mock_get):
        api_return = self.escolas_fixture()
        mock_get.return_value = api_return

        created = update_escola_table()
        assert 2 == created

        dres = Dre.objects.all()
        assert 1 == dres.count()

        tipos = TipoEscola.objects.all()
        assert 1 == tipos.count()

        distritos = Distrito.objects.all().order_by('-coddist')
        assert 2 == distritos.count()

        escolas = Escola.objects.all().order_by('codesc')
        assert 2 == escolas.count()

        infos = EscolaInfo.objects.all().order_by('escola__codesc')
        assert 2 == infos.count()

        dre = dres.first()
        assert 'BT' == dre.code
        assert 'DIRETORIA REGIONAL DE EDUCACAO BUTANTA' == dre.name

        tipo = tipos.first()
        assert 'EMEF' == tipo.code

        for distrito, expected in zip(distritos, api_return['results']):
            assert distrito.coddist == int(expected['coddist'])
            assert distrito.name == expected['distrito']

        for info, expected in zip(infos, api_return['results']):
            assert info.escola.codesc == expected['codesc']
            assert info.dre == dre
            assert info.tipoesc == tipo
            assert info.distrito.coddist == int(expected['coddist'])
            assert info.nomesc == expected['nomesc']
            assert info.endereco == expected['endereco']
            assert info.numero == int(expected['numero'])
            assert info.bairro == expected['bairro']
            assert info.cep == expected['cep']
            assert info.rede == expected['rede']
            assert str(info.latitude) == str(expected['latitude'])
            assert str(info.longitude) == str(expected['longitude'])
            assert info.total_vagas == expected['total_vagas']
            assert info.year == date.today().year

    @patch.object(requests, 'get')
    def test_updates_existing_escola(self, mock_get):
        mommy.make(EscolaInfo, escola__codesc="000191", year=date.today().year,
                   _fill_optional=True)
        assert 1 == Dre.objects.count()
        assert 1 == TipoEscola.objects.count()
        assert 1 == Distrito.objects.count()
        assert 1 == Escola.objects.count()
        assert 1 == EscolaInfo.objects.count()

        api_return = self.escolas_fixture()
        mock_get.return_value = api_return

        created = update_escola_table()
        assert 1 == created

        dres = Dre.objects.all()
        assert 2 == dres.count()

        tipos = TipoEscola.objects.all()
        assert 2 == tipos.count()

        distritos = Distrito.objects.all().order_by('-code')
        assert 3 == distritos.count()

        escolas = Escola.objects.all().order_by('codesc')
        assert 2 == escolas.count()

        infos = EscolaInfo.objects.all().order_by('escola__codesc')
        assert 2 == infos.count()

        for info, expected in zip(infos, api_return['results']):
            assert info.escola.codesc == expected['codesc']
            assert info.dre.code == expected['dre']
            assert info.tipoesc.code == expected['tipoesc']
            assert info.distrito.coddist == int(expected['coddist'])
            assert info.nomesc == expected['nomesc']
            assert info.endereco == expected['endereco']
            assert info.numero == int(expected['numero'])
            assert info.bairro == expected['bairro']
            assert info.cep == expected['cep']
            assert info.rede == expected['rede']
            assert str(info.latitude) == str(expected['latitude'])
            assert str(info.longitude) == str(expected['longitude'])
            assert info.total_vagas == expected['total_vagas']
            assert info.year == date.today().year
