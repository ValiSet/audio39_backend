from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from rest_framework import viewsets, filters
from api.models import Brand, Product
from api.serializers.brand_serializers import BrandSerializer
from api.serializers.product_serializers import ProductSerializer


@extend_schema_view(
    retrieve=extend_schema(
        summary="Получить детали конкретного бренда.",
        tags=['Brands']
    ),
    list=extend_schema(
        summary="Получить список всех брендов.",
        tags=['Brands'],
        parameters=[
            OpenApiParameter(name='brand_name', description='Поиск по имени брендов', required=False, type=str),
            OpenApiParameter(name='page_size', description='Количество элементов на странице', required=False,
                             type=int),
        ],
    ),
)
class BrandViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)



@extend_schema_view(
    list=extend_schema(
        summary="Получить список товаров для указанного бренда.",
        tags=['Products'],
        parameters=[
            OpenApiParameter(name='brand_id', type=OpenApiTypes.INT, location=OpenApiParameter.PATH, description='Product brand ID.'),
        ],
        responses=ProductSerializer(many=True)
    )
)
class ProductByBrandViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductSerializer

    def get_queryset(self):
        brand_id = self.kwargs.get('brand_id')
        return Product.objects.filter(brand__id=brand_id)