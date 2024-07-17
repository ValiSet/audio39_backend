from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from rest_framework import viewsets
from api.models import Size
from api.serializers.size_serializers import SizeSerializer


@extend_schema_view(
    retrieve=extend_schema(
        summary="Получить детали конкретного размера.",
        tags=['Sizes']
    ),
    list=extend_schema(
        summary="Получить список всех доступных размеров.",
        tags=['Sizes'],
        parameters=[
            OpenApiParameter(name='size_name', description='Поиск по имени размеров', required=False, type=str),
            OpenApiParameter(name='page_size', description='Количество элементов на странице', required=False,
                             type=int),
        ],
    ),
)
class SizeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Size.objects.all()
    serializer_class = SizeSerializer

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


