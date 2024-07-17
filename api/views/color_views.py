from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from api.models import Color
from api.serializers.color_serializers import ColorSerializer
from rest_framework import viewsets, filters



@extend_schema_view(
    retrieve=extend_schema(
        summary="Получить детали конкретного цвета.",
        tags=['Colors']
    ),
    list=extend_schema(
        summary="Получить список всех доступных цветов.",
        tags=['Colors'],
        parameters=[
                    OpenApiParameter(name='color_name', description='Поиск по имени цвета', required=False, type=str),
                    OpenApiParameter(name='page_size', description='Количество элементов на странице', required=False,
                                     type=int),
                ],
    ),
)
class ColorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Color.objects.all()
    serializer_class = ColorSerializer
    filter_backends = [filters.SearchFilter]  # Добавляем SearchFilter
    search_fields = ['name']  # Указываем поля для поиска по имени

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)