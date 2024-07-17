
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from rest_framework import viewsets
from api.models import Currency
from api.serializers.currency_serializers import CurrencySerializer


@extend_schema_view(
    retrieve=extend_schema(tags=['Currencies'], summary="Получить детали конкретной валюты."),
    list=extend_schema(tags=['Currencies'], parameters = [
        OpenApiParameter(name='search', description='Поиск по code валюты', required=False, type=str),
        OpenApiParameter(name='page_size', description='Количество элементов на странице', required=False,
                         type=int),
    ], summary="Получить список всех доступных валют."),
)
class CurrencyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)