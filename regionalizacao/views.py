import os

from copy import deepcopy
from datetime import date

from django.http import HttpResponse, Http404
from django_filters import rest_framework as filters
from rest_framework import generics
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.response import Response

from regionalizacao.constants import GENERATED_XLSX_PATH
from regionalizacao.dao.models_dao import EscolaInfoDao
from regionalizacao.models import EscolaInfo
from regionalizacao.serializers import PlacesSerializer


class InitialFilter(filters.FilterSet):
    # Taken from https://django-filter.readthedocs.io/en/master/guide/tips.html#using-initial-values-as-defaults

    def __init__(self, data=None, *args, **kwargs):
        # if filterset is bound, use initial values as defaults
        if data is not None:
            # get a mutable copy of the QueryDict
            data = data.copy()

            for name, f in self.base_filters.items():
                initial = f.extra.get('initial')

                # filter param is either missing or empty, use initial as default
                if not data.get(name) and initial:
                    if callable(initial):
                        data[name] = initial()
                    else:
                        data[name] = initial

        super().__init__(data, *args, **kwargs)


def newest_year():
    return EscolaInfoDao().get_newest_year()


class EscolaInfoFilter(InitialFilter):
    LOCALIDADE_CHOICES = (
        ('zona', 'Região'),
        ('dre', 'Diretoria Regional de Educação'),
    )

    zona = filters.CharFilter(field_name='distrito__zona')
    dre = filters.CharFilter(field_name='dre__code')
    distrito = filters.NumberFilter(field_name='distrito__coddist')
    escola = filters.CharFilter(field_name='escola__codesc')
    year = filters.AllValuesFilter(field_name='year', empty_label=None,
                                   initial=newest_year)
    rede = filters.AllValuesFilter(field_name='rede', empty_label=None,
                                   initial='DIR')
    localidade = filters.ChoiceFilter(choices=LOCALIDADE_CHOICES,
                                      method='filter_localidade',
                                      empty_label=None)

    def filter_queryset(self, queryset):
        query_params = deepcopy(self.form.cleaned_data)
        if query_params.get('escola'):
            e = EscolaInfo.objects.get(year=query_params.get('year'), escola__codesc=query_params.get('escola'))
            if not e.rede == query_params.get('rede'):
                del query_params['escola']

        if self.form.cleaned_data['distrito']:
            self.form.cleaned_data['dre'] = ''
        map_qs = super().filter_queryset(queryset)
        if map_qs.count() == 0:
            map_qs = EscolaInfo.objects.filter(distrito__coddist=query_params.get('distrito'),
                                               rede=query_params.get('rede'),
                                               year=query_params.get('year'))

        self.form.cleaned_data['zona'] = ''
        self.form.cleaned_data['dre'] = ''
        self.form.cleaned_data['distrito'] = ''
        self.form.cleaned_data['escola'] = ''
        locations_qs = super().filter_queryset(queryset)
        if locations_qs.count() == 0:
            locations_qs = EscolaInfo.objects.filter(distrito__coddist=query_params.get('distrito'),
                                                     rede=query_params.get('rede'),
                                                     year=query_params.get('year'))
        return query_params, map_qs, locations_qs

    def filter_localidade(self, queryset, name, value):
        return queryset


class FilteredTemplateHTMLRenderer(TemplateHTMLRenderer):
    def get_template_context(self, data, renderer_context):
        data = super().get_template_context(data, renderer_context)
        view = renderer_context['view']
        request = renderer_context['request']

        filter_backend = view.filter_backends[0]()
        qs = view.get_queryset()
        filterset = filter_backend.get_filterset(request, qs, view)

        filter_form = deepcopy(filterset.form)
        data['filter_form'] = filter_form

        return data


class HomeView(generics.ListAPIView):
    renderer_classes = [FilteredTemplateHTMLRenderer, JSONRenderer]
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = EscolaInfoFilter
    template_name = 'regionalizacao/home.html'
    queryset = EscolaInfoDao().filter_etapa_is_not_null()
    serializer_class = PlacesSerializer

    def list(self, request, *args, **kwargs):
        query_params, map_qs, locations_qs = self.filter_queryset(
            self.get_queryset())
        level = 0
        if 'zona' in request.query_params:
            level = 1
        if 'dre' in request.query_params:
            level = 2
        if 'distrito' in request.query_params:
            level = 3
        if 'escola' in request.query_params:
            level = 4

        locations_graph_type = request.query_params.get('localidade', 'zona')
        serializer = self.get_serializer(
            map_queryset=map_qs, locations_queryset=locations_qs, level=level,
            query_params=query_params,
            locations_graph_type=locations_graph_type)
        return Response({**serializer.data})


def download_view(request):
    """
    Inicia o download do arquivo gerado no servidor contendo os dados
    extendidos utilizados na ferramenta.
    :param request: objeto HTTP request.
    """
    if 'year' in request.GET:
        year = request.GET['year']
    else:
        escolas_info_dao = EscolaInfoDao()
        year = escolas_info_dao.get_newest_year()

    filename = f'regionalizacao_{year}.xlsx'
    filepath = os.path.join(GENERATED_XLSX_PATH, filename)
    if not os.path.exists(filepath):
        raise Http404

    with open(filepath, 'rb') as fh:
        response = HttpResponse(
            fh.read(), content_type="application/vnd.ms-excel")
        response['Content-Disposition'] = (
                'inline; filename=' + os.path.basename(filepath))
        return response
