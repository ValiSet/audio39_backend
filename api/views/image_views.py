
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from rest_framework import viewsets
from api.models import Image
from api.serializers.image_serializers import ImageSerializer


@extend_schema_view(
    retrieve=extend_schema(
        summary="Получить детали конкретного изображения.",
        tags=['Images'],
    ),
    list=extend_schema(
        summary="Получить список всех изображений.",
        tags=['Images'],
        parameters=[
            OpenApiParameter(name='page_size', description='Количество элементов на странице', required=False, type=int),
        ],
    ),
)
class ImageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
