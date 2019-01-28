import pytest

from datetime import date
from unittest.mock import patch

from model_mommy.mommy import make
from rest_framework.test import APITestCase

from django.test import RequestFactory
from django.urls import reverse

from budget_execution.constants import SME_ORGAO_ID
from budget_execution.models import (Execucao, FonteDeRecursoGrupo, Subfuncao,
                                     Subgrupo)
from mosaico.views import (
    SimplesViewMixin,
    TecnicoViewMixin,
    BaseListView,

    GruposListView,
    SubgruposListView,
    ElementosListView,
    SubelementosListView,

    SubfuncoesListView,
    ProgramasListView,
    ProjetosAtividadesListView,
)

from mosaico.serializers import (
    ElementoSerializer,
    GrupoSerializer,
    ProgramaSerializer,
    ProjetoAtividadeSerializer,
    SubelementoSerializer,
    SubgrupoSerializer,
    SubfuncaoSerializer,
)


SERIALIZERS_BY_SECTION = {
    'grupos': GrupoSerializer,
    'subgrupos': SubgrupoSerializer,
    'elementos': ElementoSerializer,
    'subelementos': SubelementoSerializer,
    'subfuncoes': SubfuncaoSerializer,
    'programas': ProgramaSerializer,
    'projetos': ProjetoAtividadeSerializer,
}

DISTINCT_FIELD_BY_SECTION = {
    'grupos': 'subgrupo__grupo_id',
    'subgrupos': 'subgrupo',
    'elementos': 'elemento',
    'subelementos': 'subelemento',
    'subfuncoes': 'subfuncao',
    'programas': 'programa',
    'projetos': 'projeto',
}


class TestBaseListView(APITestCase):
    def get(self, **kwargs):
        url = reverse('mosaico:grupos')
        return self.client.get(url, kwargs)

    def test_filter_by_year(self):
        # I'm setting the following id to prevent test from breaking in case of
        # negative integer generated by model_mommyt
        subgrupo_1 = make('Subgrupo', grupo=make('Grupo', id=1))
        subgrupo_2 = make('Subgrupo', grupo=make('Grupo', id=2))
        make('Execucao', year=date(1500, 1, 1), subgrupo=subgrupo_1,
             orgao__id=SME_ORGAO_ID)
        make('Execucao', year=date(2018, 1, 1), subgrupo=subgrupo_2,
             orgao__id=SME_ORGAO_ID)
        response = self.get(year=1500)
        assert 1 == len(response.data['execucoes'])
        assert 1500 == response.data['year']

    def test_returns_fonte_grupo_filters(self):
        # I'm setting the following id to prevent test from breaking in case of
        # negative integer generated by model_mommyt
        subgrupo = make('Subgrupo', grupo=make('Grupo', id=13))
        make('Execucao', year=date(1500, 1, 1), subgrupo=subgrupo,
             orgao__id=SME_ORGAO_ID)

        make(FonteDeRecursoGrupo, id=1, desc='fg1'),
        make(FonteDeRecursoGrupo, id=2, desc='fg2'),
        make(FonteDeRecursoGrupo, id=3, desc='fg3'),

        expected = [
            dict(id=1, desc='fg1', selecionado=False),
            dict(id=2, desc='fg2', selecionado=True),
            dict(id=3, desc='fg3', selecionado=False),
        ]

        response = self.get(year=1500, fonte=2)
        assert expected == response.data['fontes_de_recurso']

    def test_returns_non_selected_fonte_grupo_filters(self):
        # I'm setting the following id to prevent test from breaking in case of
        # negative integer generated by model_mommyt
        subgrupo = make('Subgrupo', grupo=make('Grupo', id=13))
        make('Execucao', year=date(1500, 1, 1), subgrupo=subgrupo)

        make(FonteDeRecursoGrupo, id=1, desc='fg1'),
        make(FonteDeRecursoGrupo, id=2, desc='fg2'),
        make(FonteDeRecursoGrupo, id=3, desc='fg3'),

        expected = [
            dict(id=1, desc='fg1', selecionado=False),
            dict(id=2, desc='fg2', selecionado=False),
            dict(id=3, desc='fg3', selecionado=False),
        ]

        response = self.get(year=1500)
        assert expected == response.data['fontes_de_recurso']

    def test_returns_only_execucoes_with_orgao_sme(self):
        make('Execucao', year=date.today(), orgao__id=SME_ORGAO_ID,
             is_minimo_legal=False, subgrupo__grupo__id=1)

        # not expected
        make('Execucao', year=date.today(), orgao__id=SME_ORGAO_ID,
             is_minimo_legal=True, subgrupo__grupo__id=2)
        make('Execucao',  year=date.today(), orgao__id=20, is_minimo_legal=True,
             subgrupo__grupo__id=3)

        response = self.get()
        assert 1 == len(response.data['execucoes'])
        assert 1 == response.data['execucoes'][0]['grupo_id']

    def test_most_recent_year_as_default(self):
        year = 1500
        make('Grupo', id=1)

        subgrupo_1 = make('Subgrupo', grupo=make('Grupo', id=1))
        subgrupo_2 = make('Subgrupo', grupo=make('Grupo', id=2))
        subgrupo_3 = make('Subgrupo', grupo=make('Grupo', id=3))

        make('Execucao', subgrupo=subgrupo_1, year=date(year, 1, 1),
             orgao__id=SME_ORGAO_ID)
        response = self.get()
        assert year == response.data['year']
        assert 1 == len(response.data['execucoes'])

        year = 2018
        make('Execucao', subgrupo=subgrupo_1, year=date(year, 1, 1),
             orgao__id=SME_ORGAO_ID)
        response = self.get()
        assert year == response.data['year']
        assert 1 == len(response.data['execucoes'])

        make('Execucao', subgrupo=subgrupo_2, year=date(year, 1, 1),
             orgao__id=SME_ORGAO_ID)
        response = self.get()
        assert year == response.data['year']
        assert 2 == len(response.data['execucoes'])

        make('Execucao', subgrupo=subgrupo_3, year=date(1998, 1, 1),
             orgao__id=SME_ORGAO_ID)
        response = self.get()
        assert year == response.data['year']
        assert 2 == len(response.data['execucoes'])

    @patch('mosaico.views.TimeseriesSerializer')
    def test_calls_serializer_with_deflate_true(self, mock_serializer):
        make(Execucao, _quantity=2)
        execucoes_qs = Execucao.objects.all().order_by('year')

        response = self.get(deflate=True, year=2018)

        assert set(execucoes_qs) == set(mock_serializer.call_args[0][0])
        assert {"deflate": True} == mock_serializer.call_args[1]
        assert response.context.get('deflate')


class TestMinimoLegalFilter(APITestCase):

    def get(self, **kwargs):
        url = reverse('mosaico:subfuncoes')
        return self.client.get(url, kwargs)

    def test_minimo_legal_filter(self):
        exec1 = make('Execucao', year=date.today(), orgao__id=SME_ORGAO_ID,
                     is_minimo_legal=False, subfuncao__id=1)
        exec2 = make('Execucao', year=date.today(), orgao__id=SME_ORGAO_ID,
                     is_minimo_legal=True, subfuncao__id=2)
        exec3 = make('Execucao',  year=date.today(), orgao__id=20,
                     is_minimo_legal=True, subfuncao__id=3)
        # not expected
        make('Execucao',  year=date.today(), orgao__id=20,
             is_minimo_legal=False, subfuncao__id=4)

        response = self.get(minimo_legal=False)
        assert 1 == len(response.data['execucoes'])
        assert exec1.subfuncao_id \
            == response.data['execucoes'][0]['subfuncao_id']

        response = self.get(minimo_legal=True)
        assert 2 == len(response.data['execucoes'])
        assert set([exec2.subfuncao_id, exec3.subfuncao_id]) \
            == set([ex['subfuncao_id'] for ex in response.data['execucoes']])


class BaseTestCase(APITestCase):

    def get(self, **query_params):
        return self.client.get(self.base_url, query_params)

    def get_serializer(self, execucoes, **query_params):
        factory = RequestFactory()
        request = factory.get(self.base_url, data=query_params)
        serializer = self.serializer_class

        return serializer(execucoes, many=True,
                          context={'request': request})


class TestGruposListView(BaseTestCase):

    serializer_class = GrupoSerializer

    @property
    def base_url(self):
        return reverse('mosaico:grupos')

    @pytest.fixture(autouse=True, scope='class')
    def initial(self):
        make(Execucao,
             orgao__id=SME_ORGAO_ID,
             subgrupo__grupo__id=1,
             fonte_grupo__id=1,
             year=date(2018, 1, 1),
             _quantity=2)
        make(Execucao,
             orgao__id=SME_ORGAO_ID,
             subgrupo__grupo__id=2,
             fonte_grupo__id=1,
             year=date(2018, 1, 1),
             _quantity=2)
        make(Execucao,
             orgao__id=SME_ORGAO_ID,
             subgrupo__grupo__id=3,
             fonte_grupo__id=2,
             year=date(2018, 1, 1),
             _quantity=2)

    def test_serializes_execucoes_data(self):
        execucoes = Execucao.objects.all()
        serializer = self.get_serializer(execucoes, year=2018)
        expected = serializer.data

        response = self.get(year=2018)
        assert expected == response.data['execucoes']

    def test_filters_by_fonte_grupo_querystring_data(self):
        execucoes = Execucao.objects.filter(fonte_grupo__id=1)
        serializer = self.get_serializer(execucoes, fonte=1, year=2018)
        expected = serializer.data

        response = self.get(fonte=1, year=2018)
        data = response.data['execucoes']
        assert 2 == len(data)
        assert expected == data

    def test_view_works_when_queryset_is_empty(self):
        make(FonteDeRecursoGrupo, id=3)
        response = self.get(fonte=3, year=2018)
        assert [] == response.data['execucoes']

    def test_issubclass_of_baselistview_and_simplesviewmixin(self):
        assert issubclass(GruposListView, BaseListView)
        assert issubclass(GruposListView, SimplesViewMixin)


class TestSubgruposListView(BaseTestCase):

    serializer_class = SubgrupoSerializer

    @property
    def base_url(self):
        return reverse('mosaico:subgrupos', args=[1])

    @pytest.fixture(autouse=True, scope='class')
    def initial(self):
        subgrupo1 = make(Subgrupo, id=96, grupo__id=1)
        subgrupo2 = make(Subgrupo, id=97, grupo__id=1)
        subgrupo3 = make(Subgrupo, id=98, grupo__id=1)

        make(Execucao,
             orgao__id=SME_ORGAO_ID,
             subgrupo=subgrupo1,
             fonte_grupo__id=1,
             year=date(2018, 1, 1),
             _quantity=2)
        make(Execucao,
             orgao__id=SME_ORGAO_ID,
             subgrupo=subgrupo2,
             fonte_grupo__id=1,
             year=date(2018, 1, 1),
             _quantity=2)
        make(Execucao,
             orgao__id=SME_ORGAO_ID,
             subgrupo=subgrupo3,
             fonte_grupo__id=2,
             year=date(2018, 1, 1),
             _quantity=2)

    def test_serializes_execucoes_data(self):
        execucoes = Execucao.objects.all()
        serializer = self.get_serializer(execucoes, year=2018)
        expected = serializer.data

        response = self.get(year=2018)
        data = response.data['execucoes']
        assert 3 == len(data)
        assert expected == data

    def test_filters_by_fonte_grupo_querystring_data(self):
        execucoes = Execucao.objects.filter(fonte_grupo__id=1)
        serializer = self.get_serializer(execucoes, fonte=1, year=2018)
        expected = serializer.data

        response = self.get(fonte=1, year=2018)
        data = response.data['execucoes']
        assert 2 == len(data)
        assert expected == data

    def test_view_works_when_queryset_is_empty(self):
        make(FonteDeRecursoGrupo, id=3)
        response = self.get(fonte=3, year=2018)
        assert [] == response.data['execucoes']

    def test_issubclass_of_baselistview_and_simplesviewmixin(self):
        assert issubclass(SubgruposListView, BaseListView)
        assert issubclass(SubgruposListView, SimplesViewMixin)


class TestElementosListView(BaseTestCase):

    serializer_class = ElementoSerializer

    @property
    def base_url(self):
        return reverse('mosaico:elementos', args=[1, 1])

    @pytest.fixture(autouse=True, scope='class')
    def initial(self):
        subgrupo = make(Subgrupo, id=1, grupo__id=1)
        make(Execucao,
             orgao__id=SME_ORGAO_ID,
             elemento__id=1,
             subgrupo=subgrupo,
             fonte_grupo__id=1,
             year=date(2018, 1, 1),
             _quantity=2)
        make(Execucao,
             orgao__id=SME_ORGAO_ID,
             elemento__id=2,
             subgrupo=subgrupo,
             fonte_grupo__id=1,
             year=date(2018, 1, 1),
             _quantity=2)
        make(Execucao,
             orgao__id=SME_ORGAO_ID,
             elemento__id=3,
             subgrupo=subgrupo,
             fonte_grupo__id=2,
             year=date(2018, 1, 1),
             _quantity=2)

    def test_serializes_execucoes_data(self):
        execucoes = Execucao.objects.all()
        serializer = self.get_serializer(execucoes, year=2018)
        expected = serializer.data

        response = self.get(year=2018)
        data = response.data['execucoes']
        assert 3 == len(data)
        assert expected == data

    def test_filters_by_fonte_grupo_querystring_data(self):
        execucoes = Execucao.objects.filter(fonte_grupo__id=1)
        serializer = self.get_serializer(execucoes, fonte=1, year=2018)
        expected = serializer.data

        response = self.get(fonte=1, year=2018)
        data = response.data['execucoes']
        assert 2 == len(data)
        assert expected == data

    def test_view_works_when_queryset_is_empty(self):
        make(FonteDeRecursoGrupo, id=3)
        response = self.get(fonte=3, year=2018)
        assert [] == response.data['execucoes']

    def test_issubclass_of_baselistview_and_simplesviewmixin(self):
        assert issubclass(ElementosListView, BaseListView)
        assert issubclass(ElementosListView, SimplesViewMixin)


class TestSubelementosListView(BaseTestCase):

    serializer_class = SubelementoSerializer

    @property
    def base_url(self):
        return reverse('mosaico:subelementos', args=[1, 1, 1])

    @pytest.fixture(autouse=True, scope='class')
    def initial(self):
        grupo = make('Grupo', id=1)
        subgrupo = make(Subgrupo, id=1, grupo=grupo)
        make(Execucao,
             orgao__id=SME_ORGAO_ID,
             subelemento__id=1,
             subelemento_friendly__id=1,
             elemento__id=1,
             subgrupo=subgrupo,
             fonte_grupo__id=1,
             year=date(2018, 1, 1),
             orcado_atualizado=1,
             _quantity=2)
        make(Execucao,
             orgao__id=SME_ORGAO_ID,
             subelemento__id=2,
             subelemento_friendly__id=2,
             elemento__id=1,
             subgrupo=subgrupo,
             fonte_grupo__id=1,
             year=date(2018, 1, 1),
             orcado_atualizado=1,
             _quantity=2)
        make(Execucao,
             orgao__id=SME_ORGAO_ID,
             subelemento__id=3,
             subelemento_friendly__id=3,
             elemento__id=1,
             subgrupo=subgrupo,
             fonte_grupo__id=2,
             year=date(2018, 1, 1),
             orcado_atualizado=1,
             _quantity=2)

    def test_serializes_execucoes_data(self):
        execucoes = Execucao.objects.all()
        serializer = self.get_serializer(execucoes, year=2018)
        expected = serializer.data

        response = self.get(year=2018)
        data = response.data['execucoes']
        assert 3 == len(data)
        assert expected == data

    def test_filters_by_fonte_grupo_querystring_data(self):
        execucoes = Execucao.objects.filter(fonte_grupo__id=1)
        serializer = self.get_serializer(execucoes, fonte=1, year=2018)
        expected = serializer.data

        response = self.get(fonte=1, year=2018)
        data = response.data['execucoes']
        assert 2 == len(data)
        assert expected == data

    def test_view_works_when_queryset_is_empty(self):
        make(FonteDeRecursoGrupo, id=3)
        response = self.get(fonte=3, year=2018)
        assert [] == response.data['execucoes']

    def test_issubclass_of_baselistview_and_simplesviewmixin(self):
        assert issubclass(SubelementosListView, BaseListView)
        assert issubclass(SubelementosListView, SimplesViewMixin)


class TestSubfuncaoListView(BaseTestCase):

    serializer_class = SubfuncaoSerializer

    @property
    def base_url(self):
        return reverse('mosaico:subfuncoes')

    @pytest.fixture(autouse=True, scope='class')
    def initial(self):
        make(Execucao,
             orgao__id=SME_ORGAO_ID,
             subfuncao__id=1,
             fonte_grupo__id=1,
             year=date(2018, 1, 1),
             _quantity=2)
        make(Execucao,
             orgao__id=SME_ORGAO_ID,
             subfuncao__id=2,
             fonte_grupo__id=1,
             year=date(2018, 1, 1),
             _quantity=2)
        make(Execucao,
             orgao__id=SME_ORGAO_ID,
             subfuncao__id=3,
             fonte_grupo__id=2,
             year=date(2018, 1, 1),
             _quantity=2)

    def test_serializes_execucoes_data(self):
        execucoes = Execucao.objects.all()
        serializer = self.get_serializer(execucoes, year=2018)
        expected = serializer.data

        response = self.get(year=2018)
        data = response.data['execucoes']
        assert 3 == len(data)
        assert expected == data

    def test_filters_by_fonte_grupo_querystring_data(self):
        execucoes = Execucao.objects.filter(fonte_grupo__id=1)
        serializer = self.get_serializer(execucoes, fonte=1, year=2018)
        expected = serializer.data

        response = self.get(fonte=1, year=2018)
        data = response.data['execucoes']
        assert 2 == len(data)
        assert expected == data

    def test_view_works_when_queryset_is_empty(self):
        make(FonteDeRecursoGrupo, id=3)
        response = self.get(fonte=3, year=2018)
        assert [] == response.data['execucoes']

    def test_issubclass_of_baselistview_and_simplesviewmixin(self):
        assert issubclass(SubfuncoesListView, BaseListView)
        assert issubclass(SubfuncoesListView, TecnicoViewMixin)


class TestProgramasListView(BaseTestCase):

    serializer_class = ProgramaSerializer

    @property
    def base_url(self):
        return reverse('mosaico:programas', args=[1])

    @pytest.fixture(autouse=True, scope='class')
    def initial(self):
        make(Execucao,
             orgao__id=SME_ORGAO_ID,
             programa__id=1,
             subfuncao__id=1,
             fonte_grupo__id=1,
             year=date(2018, 1, 1),
             _quantity=2)
        make(Execucao,
             orgao__id=SME_ORGAO_ID,
             programa__id=2,
             subfuncao__id=1,
             fonte_grupo__id=1,
             year=date(2018, 1, 1),
             _quantity=2)
        make(Execucao,
             orgao__id=SME_ORGAO_ID,
             programa__id=3,
             subfuncao__id=1,
             fonte_grupo__id=2,
             year=date(2018, 1, 1),
             _quantity=2)

    def test_serializes_execucoes_data(self):
        execucoes = Execucao.objects.all()
        serializer = self.get_serializer(execucoes, year=2018)
        expected = serializer.data

        response = self.get(year=2018)
        data = response.data['execucoes']
        assert 3 == len(data)
        assert expected == data

    def test_filters_by_fonte_grupo_querystring_data(self):
        execucoes = Execucao.objects.filter(fonte_grupo__id=1)
        serializer = self.get_serializer(execucoes, fonte=1, year=2018)
        expected = serializer.data

        response = self.get(fonte=1, year=2018)
        data = response.data['execucoes']
        assert 2 == len(data)
        assert expected == data

    def test_view_works_when_queryset_is_empty(self):
        make(FonteDeRecursoGrupo, id=3)
        response = self.get(fonte=3, year=2018)
        assert [] == response.data['execucoes']

    def test_issubclass_of_baselistview_and_simplesviewmixin(self):
        assert issubclass(ProgramasListView, BaseListView)
        assert issubclass(ProgramasListView, TecnicoViewMixin)


class TestProjetosAtividadesListView(BaseTestCase):

    serializer_class = ProjetoAtividadeSerializer

    @property
    def base_url(self):
        return reverse('mosaico:projetos', args=[1, 1])

    @pytest.fixture(autouse=True, scope='class')
    def initial(self):
        make(Execucao,
             orgao__id=SME_ORGAO_ID,
             projeto__id=1,
             programa__id=1,
             subfuncao__id=1,
             fonte_grupo__id=1,
             year=date(2018, 1, 1),
             _quantity=2)
        make(Execucao,
             orgao__id=SME_ORGAO_ID,
             projeto__id=2,
             programa__id=1,
             subfuncao__id=1,
             fonte_grupo__id=1,
             year=date(2018, 1, 1),
             _quantity=2)
        make(Execucao,
             orgao__id=SME_ORGAO_ID,
             projeto__id=3,
             programa__id=1,
             subfuncao__id=1,
             fonte_grupo__id=2,
             year=date(2018, 1, 1),
             _quantity=2)

    def test_serializes_execucoes_data(self):
        execucoes = Execucao.objects.all()
        serializer = self.get_serializer(execucoes, year=2018)
        expected = serializer.data

        response = self.get(year=2018)
        data = response.data['execucoes']
        assert 3 == len(data)
        assert expected == data

    def test_filters_by_fonte_grupo_querystring_data(self):
        execucoes = Execucao.objects.filter(fonte_grupo__id=1)
        serializer = self.get_serializer(execucoes, fonte=1, year=2018)
        expected = serializer.data

        response = self.get(fonte=1, year=2018)
        data = response.data['execucoes']
        assert 2 == len(data)
        assert expected == data

    def test_view_works_when_queryset_is_empty(self):
        make(FonteDeRecursoGrupo, id=3)
        response = self.get(fonte=3, year=2018)
        assert [] == response.data['execucoes']

    def test_issubclass_of_baselistview_and_simplesviewmixin(self):
        assert issubclass(ProjetosAtividadesListView, BaseListView)
        assert issubclass(ProjetosAtividadesListView, TecnicoViewMixin)


class TestDownloadView(APITestCase):

    def get(self, view_name, **query_params):
        url = self.base_url(view_name)
        return self.client.get(url, query_params)

    def base_url(self, view_name):
        return reverse('mosaico:download', args=[view_name])

    @pytest.fixture(autouse=True, scope='class')
    def initial(self):
        subgrupo1 = make(Subgrupo, id=1, grupo__id=1)
        subgrupo2 = make(Subgrupo, id=2, grupo__id=1)
        subgrupo3 = make(Subgrupo, id=3, grupo__id=2)
        subfuncao = make(Subfuncao, id=1, desc="sub")

        make(Execucao,
             orgao__id=SME_ORGAO_ID,
             subgrupo=subgrupo1,
             elemento__id=1,
             subelemento__id=1,
             subfuncao=subfuncao,
             programa__id=1,
             projeto__id=1,
             year=date(2018, 1, 1),
             orcado_atualizado=1,
             _quantity=2)
        make(Execucao,
             orgao__id=SME_ORGAO_ID,
             subgrupo=subgrupo2,
             elemento__id=1,
             subelemento__id=2,
             subfuncao=subfuncao,
             programa__id=1,
             projeto__id=2,
             year=date(2018, 1, 1),
             orcado_atualizado=1,
             _quantity=2)
        make(Execucao,
             orgao__id=SME_ORGAO_ID,
             subgrupo=subgrupo3,
             elemento__id=2,
             subelemento__id=3,
             subfuncao__id=100,
             programa__id=2,
             projeto__id=3,
             year=date(2017, 1, 1),
             orcado_atualizado=1,
             _quantity=2)

    def prepare_expected_data(self, section, year=None):
        factory = RequestFactory()
        if year:
            execucoes = Execucao.objects.filter(year=date(year, 1, 1))
            request = factory.get(self.base_url(section), {'year': year})
        else:
            execucoes = Execucao.objects.all()
            request = factory.get(self.base_url(section))

        serializer_class = SERIALIZERS_BY_SECTION[section]
        return serializer_class(
            execucoes, many=True, context={'request': request}).data

    def test_uses_correct_renderer(self):
        response = self.get('grupos')
        assert 'csv' == response.accepted_renderer.format

    def test_downloads_grupos_data(self):
        expected = self.prepare_expected_data('grupos')
        data = self.get('grupos').data
        assert 2 == len(data)
        assert expected == data

    def test_downloads_grupos_filtered_data(self):
        expected = self.prepare_expected_data('grupos', year=2018)
        data = self.get('grupos', year=2018).data
        assert 1 == len(data)
        assert expected == data

    def test_downloads_subgrupos_data(self):
        expected = self.prepare_expected_data('subgrupos')
        data = self.get('subgrupos').data
        assert 3 == len(data)
        assert expected == data

    def test_downloads_subgrupos_filtered_data(self):
        expected = self.prepare_expected_data('subgrupos', year=2018)
        data = self.get('subgrupos', year=2018).data
        assert 2 == len(data)
        assert expected == data

    def test_downloads_elementos_data(self):
        expected = self.prepare_expected_data('elementos')
        data = self.get('elementos').data
        assert 2 == len(data)
        assert expected == data

    def test_downloads_elementos_filtered_data(self):
        expected = self.prepare_expected_data('elementos', year=2018)
        data = self.get('elementos', year=2018).data
        assert 1 == len(data)
        assert expected == data

    def test_downloads_subelementos_data(self):
        expected = self.prepare_expected_data('subelementos')
        data = self.get('subelementos').data
        assert 3 == len(data)
        assert expected == data

    def test_downloads_subelementos_filtered_data(self):
        expected = self.prepare_expected_data('subelementos', year=2018)
        data = self.get('subelementos', year=2018).data
        assert 2 == len(data)
        assert expected == data

    def test_downloads_subfuncoes_data(self):
        expected = self.prepare_expected_data('subfuncoes')
        data = self.get('subfuncoes').data
        assert 2 == len(data)
        assert expected == data

    def test_downloads_subfuncoes_filtered_data(self):
        expected = self.prepare_expected_data('subfuncoes', year=2018)
        data = self.get('subfuncoes', year=2018).data
        assert 1 == len(data)
        assert expected == data

    def test_downloads_programas_data(self):
        expected = self.prepare_expected_data('programas')
        data = self.get('programas').data
        assert 2 == len(data)
        assert expected == data

    def test_downloads_programas_filtered_data(self):
        expected = self.prepare_expected_data('programas', year=2018)
        data = self.get('programas', year=2018).data
        assert 1 == len(data)
        assert expected == data

    def test_downloads_projetos_data(self):
        expected = self.prepare_expected_data('projetos')
        data = self.get('projetos').data
        assert 3 == len(data)
        assert expected == data

    def test_downloads_projetos_filtered_data(self):
        expected = self.prepare_expected_data('projetos', year=2018)
        data = self.get('projetos', year=2018).data
        assert 2 == len(data)
        assert expected == data
