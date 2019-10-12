import os

from django.conf import settings


CONTRATOS_EMPENHOS_DIFFERENCE_PERCENT_LIMIT = settings.CONTRATOS_EMPENHOS_DIFFERENCE_PERCENT_LIMIT  # noqa
CONTRATOS_RAW_DUMP_DIR_PATH = settings.CONTRATOS_RAW_DUMP_DIR_PATH
CONTRATOS_RAW_DUMP_FILENAME = settings.CONTRATOS_RAW_DUMP_FILENAME
EXECUCOES_CONTRATOS_DUMP_DIR_PATH = settings.EXECUCOES_CONTRATOS_DUMP_DIR_PATH
EXECUCOES_CONTRATOS_DUMP_FILENAME = settings.EXECUCOES_CONTRATOS_DUMP_FILENAME

CATEGORIA_FROM_TO_SLUG = settings.CATEGORIA_FROM_TO_SLUG
CONTRATOS_BASE_DIR = os.path.join(settings.BASE_DIR, '../contratos')
GENERATED_XLSX_PATH = os.path.join(CONTRATOS_BASE_DIR, 'data')

PRODAM_URL = settings.PRODAM_URL
