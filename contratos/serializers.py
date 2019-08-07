from contratos.services import application as services


class ExecucaoContratoSerializer:

    def __init__(self, queryset, *args, **kwargs):
        self.queryset = queryset

    @property
    def data(self):
        # TODO: add tests
        return {
            'big_number': services.serialize_big_number_data(self.queryset),
            'destinations': services.serialize_destinations(self.queryset),
        }
