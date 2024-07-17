
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from rest_framework import viewsets
from api.models import Country
from api.serializers.country_serializers import CountrySerializer



@extend_schema_view(
    retrieve=extend_schema(
        summary="Получить детали конкретной страны.",
        tags=['Countries']
    ),
    list=extend_schema(
        summary="Получить список всех доступных стран.",
        tags=['Countries'],
        parameters=[
                            OpenApiParameter(name='search', description='Поиск по iso code страны', required=False, type=str),
                            OpenApiParameter(name='page_size', description='Количество элементов на странице', required=False,
                                             type=int),
                        ],
    ),
)
class CountryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)