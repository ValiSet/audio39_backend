from django.db.models import Count
from django.shortcuts import get_object_or_404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from api.models import Brand, Product, Category, Size, Color, Country
from api.pagination import ProductPagination
from api.serializers.brand_serializers import BrandSerializer
from api.serializers.category_serializers import CategorySerializer
from api.serializers.color_serializers import ColorSerializer
from api.serializers.country_serializers import CountrySerializer
from api.serializers.product_serializers import ProductSerializer
from api.serializers.size_serializers import SizeSerializer


@extend_schema_view(
    retrieve=extend_schema(
        summary="Получить детали конкретной категории.",
        tags=['Categories']
    ),
    list=extend_schema(
        summary="Получить список всех категорий.",
        tags=['Categories']
    ),
    brands=extend_schema(
        summary="Получить список брендов продуктов в данной категории и её подкатегориях.",
        tags=['Categories'],
        parameters=[
                        OpenApiParameter(name='brand_name', description='Поиск по имени бренда', required=False, type=str)
                    ]
    ),
    sizes=extend_schema(
        summary="Получить список размеров продуктов в данной категории и её подкатегориях.",
        tags=['Categories'],
        parameters=[
                        OpenApiParameter(name='name_size', description='Поиск по имени размера', required=False, type=str)
                    ]
    ),
    colors=extend_schema(
        summary="Получить список цветов продуктов в данной категории и её подкатегориях.",
        tags=['Categories'],
        parameters=[
                OpenApiParameter(name='name_color', description='Поиск по имени цвета', required=False, type=str)
            ]
    ),
    countries=extend_schema(
        summary="Получить список стран продуктов в данной категории и её подкатегориях.",
        tags=['Categories'],
        parameters=[
                        OpenApiParameter(name='name_country', description='Поиск по имени iso коду страны', required=False, type=str)
                    ]
    ),
    children=extend_schema(
        summary="Получить список подкатегорий данной категории.",
        tags=['Categories']
    ),
)
class CategoryViewSet(viewsets.GenericViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    pagination_class = ProductPagination

    def list(self, request):
        queryset = self.queryset.filter(parent=None).prefetch_related('children')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        category = self.queryset.prefetch_related('children').get(pk=pk)
        serialized_data = self.serializer_class(category).data
        return Response(serialized_data)

    @action(detail=True, methods=['get'])
    def children(self, request, pk=None):
        category = self.queryset.prefetch_related('children').get(pk=pk)
        children = category.children.all()
        serializer = self.serializer_class(children, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def brands(self, request, pk=None):
        search = request.query_params.get('brand_name', None)
        return self.get_action_response(request, pk, self.get_category_brands, BrandSerializer, search=search)

    @staticmethod
    def get_category_brands(category, search=None):
        category_ids = category.get_descendants(include_self=True).values_list('id', flat=True)
        brands = Brand.objects.filter(
            product__productcategory__category_id__in=category_ids
        ).order_by('name').distinct()
        if search:
            brands = brands.filter(name__icontains=search)
        brands_with_counts = brands.annotate(product_count=Count('product__brand_id'))

        return brands_with_counts

    @action(detail=True, methods=['get'])
    def sizes(self, request, pk=None):
        search = request.query_params.get('name_size', None)
        return self.get_action_response(request, pk, self.get_category_sizes, SizeSerializer, search=search)

    @staticmethod
    def get_category_sizes(category, search=None):
        category_ids = category.get_descendants(include_self=True).values_list('id', flat=True)
        sizes = Size.objects.filter(
            productsize__product__productcategory__category_id__in=category_ids
        ).order_by('id').distinct()
        if search:
            sizes = sizes.filter(raw_size__icontains=search)
        sizes_with_counts = sizes.annotate(product_count=Count('productsize__product'))
        return sizes_with_counts

    @action(detail=True, methods=['get'])
    def colors(self, request, pk=None, search=None):
        search = request.query_params.get('name_color', None)
        return self.get_action_response(request, pk, self.get_category_colors, ColorSerializer, search=search)

    @staticmethod
    def get_category_colors(category, search=None):
        category_ids = category.get_descendants(include_self=True).values_list('id', flat=True)
        colors = Color.objects.filter(
            producttype__product__productcategory__category_id__in=category_ids
        ).order_by('id').distinct()

        if search:
            colors = colors.filter(name__icontains=search)

        colors_with_counts = colors.annotate(product_count=Count('producttype__product'))
        return colors_with_counts

    @action(detail=True, methods=['get'])
    def countries(self, request, pk=None):
        search = request.query_params.get('name_country', None)
        return self.get_action_response(request, pk, self.get_category_countries, CountrySerializer, search=search)

    @staticmethod
    def get_category_countries(category, search=None):
        category_ids = category.get_descendants(include_self=True).values_list('id', flat=True)
        countries = Country.objects.filter(
            productcountry__product__productcategory__category_id__in=category_ids
        ).order_by('name_ru').distinct()
        if search:
            countries = countries.filter(iso_code__icontains=search)
        countries_with_counts = countries.annotate(product_count=Count('productcountry__product'))

        return countries_with_counts

    def get_action_response(self, request, pk, fetch_method, serializer_class, **kwargs):
        category = self.queryset.get(pk=pk)


        data = fetch_method(category, **kwargs)

        paginator = ProductPagination()
        paginated_data = paginator.paginate_queryset(data, request)
        serializer = serializer_class(paginated_data, many=True)
        try:
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            print(e)


@extend_schema_view(
    list=extend_schema(
        summary="Получить список товаров для указанной категории.",
        tags=['Products'],
        parameters=[
            OpenApiParameter(name='category_id', type=OpenApiTypes.INT, location=OpenApiParameter.PATH, description='Product category ID.'),
        ],
        responses=ProductSerializer(many=True)
    )
)
class ProductByCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductSerializer
    pagination_class = ProductPagination

    def get_queryset(self):
        category_id = self.kwargs.get('category_id')
        category = get_object_or_404(Category, pk=category_id)
        categories = self.get_descendants(category)
        queryset = Product.objects.filter(productcategory__category__in=categories)
        return queryset

    @staticmethod
    def get_descendants(category):
        descendants = set()
        stack = [category]
        while stack:
            node = stack.pop()
            descendants.add(node)
            stack.extend(node.children.all())
        return descendants