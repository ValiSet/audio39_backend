from api.models import Brand, Product, Category, Size, ProductType, ProductSize
from api.pagination import ProductPagination
from api.serializers.product_serializers import ProductSerializer
from rest_framework import viewsets
from django.db.models import F
from django.db.models import Exists, OuterRef
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from django.db.models import Max, Min, Q
from rest_framework.filters import OrderingFilter, SearchFilter
from django.db.models import F, Value
from django.db.models.functions import Coalesce
from decimal import Decimal
from rest_framework.decorators import action
from rest_framework import status
@extend_schema_view(
    retrieve=extend_schema(
        summary="Получить детали конкретного товара.",
        tags=['Products']
    ),
    list=extend_schema(
        summary="Получить список всех товаров.",
        tags=['Products'],

        parameters=[
            OpenApiParameter(name='page_size', description='Number of items per page', required=False,
                                                 type=int),

            OpenApiParameter(name='category', type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, description='Category ID for filtering products.'),
            OpenApiParameter(name='category_slug', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, description='Category slug for filtering products.'),
            OpenApiParameter(
                name='brand',
                type={'type': 'array', 'items': {'type': 'integer'}},
                style='form',
                explode=True,
                location=OpenApiParameter.QUERY,
                description='Brand ID for filtering products.'
            ),
            OpenApiParameter(name='brand_filter', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, description='Brand name for filtering products.'),
            OpenApiParameter(name='min_price', type=OpenApiTypes.NUMBER, location=OpenApiParameter.QUERY, description='Minimum price for filtering products.'),
            OpenApiParameter(name='max_price', type=OpenApiTypes.NUMBER, location=OpenApiParameter.QUERY, description='Maximum price for filtering products.'),

            OpenApiParameter(name='size', type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, description='Size ID for filtering products.'),
            OpenApiParameter(
                            name='size_filter',
                            type={'type': 'array', 'items': {'type': 'string'}},
                            location=OpenApiParameter.QUERY,
                            description='List of country STR for filtering products.',
                            style='form',
                            explode=True
                        ),
            OpenApiParameter(name='color', type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, description='Color ID for filtering products.'),
            OpenApiParameter(name='color_filter', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, description='Color name for filtering products.'),
            OpenApiParameter(
                name='country',
                type={'type': 'array', 'items': {'type': 'integer'}},
                location=OpenApiParameter.QUERY,
                description='List of country IDs for filtering products.',
                style='form',
                explode=True
            ),
            OpenApiParameter(name='discount', type=OpenApiTypes.BOOL, location=OpenApiParameter.QUERY, description='Boolean flag for filtering products by discount.'),
            OpenApiParameter(name='in_stock', type=OpenApiTypes.BOOL, location=OpenApiParameter.QUERY, description='Boolean flag for filtering products by in stock.'),
            OpenApiParameter(name='has_price', type=OpenApiTypes.BOOL, location=OpenApiParameter.QUERY,
                             description='Boolean flag for filtering products by has price.'),

            OpenApiParameter(name='currency', type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, description='Currency ID for filtering products.'),
            OpenApiParameter(name='search', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, description='Search products.'),
            OpenApiParameter(name='sort', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, description='Sort products.'),
        ],
        responses=ProductSerializer(many=True)
    ),
)
class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.annotate(
        has_product_types=Exists(ProductType.objects.filter(product_id=OuterRef('pk')))
    ).filter(has_product_types=True).prefetch_related('productcategory_set', 'productsize_set')
    pagination_class = ProductPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title_ru', 'title_en', 'brand__name']
    ordering_fields = ['title_ru', 'price']
    permission_classes = []
    def list(self, request, **kwargs):

        max_price, min_price= self.category_filtered_queryset(request.query_params)
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        if page is not None:
                serializer = self.serializer_class(page, many=True)


                response_data = {
                    'count': len(serializer.data),
                    'max_price_value': max_price,
                    'min_price_value': min_price,
                    'results': serializer.data
                }
                return self.get_paginated_response(response_data)
        serializer = self.serializer_class(queryset, many=True)

        min_price_value = queryset.aggregate(Min('productcurrency__price'))['productcurrency__price__min']
        max_price_value = queryset.aggregate(Max('productcurrency__price'))['productcurrency__price__max']

        response_data = {
            'count': len(serializer.data),
            'max_price_value': max_price_value,
            'min_price_value': min_price_value,
            'results': serializer.data
        }
        return Response(response_data)

    def get_queryset(self):
        if hasattr(self, '_queryset'):
            return self._queryset

        queryset = self.queryset
        query_params = self.request.query_params
        _filters = Q()

        _filters &= self.filter_by_category(query_params)
        _filters &= self.filter_by_discount(query_params)
        _filters &= self.filter_by_in_stock(query_params)
        _filters &= self.filter_by_brand(query_params)
        _filters &= self.filter_by_size(query_params)
        _filters &= self.filter_by_price(query_params)
        _filters &= self.filter_by_color(query_params)
        _filters &= self.filter_by_country(query_params)
        _filters &= self.filter_by_currency(query_params)
        _filters &= self.filter_by_color_name(query_params)
        _filters &= self.filter_by_size_name(query_params)
        _filters &= self.filter_by_search(query_params)

        queryset = queryset.filter(_filters).distinct().annotate(price=F('productcurrency__price'))

        sort = query_params.get('sort')
        sort_mapping = {
            'popular': 'popularity',
            'popular_desc': '-popularity',
            'rating': 'rating',
            'rating_desc': '-rating',
            'price': 'price',
            'price_desc': '-price'
        }
        sort_field = sort_mapping.get(sort, 'title_ru')
        queryset = queryset.order_by(sort_field)


        self._queryset = queryset
        return queryset

    @staticmethod
    def filter_by_category(query_params):
        category_id = query_params.get('category')
        category_slug = query_params.get('category_slug')
        category_filters = Q()
        if category_id or category_slug:
            try:
                category = None
                if category_id:
                    category = get_object_or_404(Category, id=category_id)
                elif category_slug:
                    category = get_object_or_404(Category, slug=category_slug)

                if category:
                    descendant_category_ids = list(category.get_descendants(include_self=True).values_list('id', flat=True))
                    category_filters &= Q(productcategory__category_id__in=descendant_category_ids)

            except Category.DoesNotExist:
                return Q(pk__in=[])

        return category_filters

    @staticmethod
    def filter_by_discount(query_params):
        discount = query_params.get('discount')
        discount_filters = Q()

        if discount:
            discount = discount.lower() == 'true'
            if discount:
                discount_filters &= Q(productcurrency__discount_price__gt=0)
            else:
                discount_filters &= Q(Q(productcurrency__discount_price=0) | Q(productcurrency__discount_price__isnull=True))

        return discount_filters

    @staticmethod
    def filter_by_in_stock(query_params):
        in_stock = query_params.get('in_stock')
        stock_filters = Q()

        if in_stock:
            in_stock = in_stock.lower() == 'true'
            available_product_ids = ProductSize.objects.filter(is_available=in_stock).values_list('product_id', flat=True)
            stock_filters &= Q(id__in=available_product_ids)

        return stock_filters

    @staticmethod
    def filter_by_brand(query_params):
        brand_ids = query_params.getlist('brand')
        brand_name = query_params.get('brand_filter')
        brand_filters = Q()

        if brand_ids:
            brand_filters &= Q(brand_id__in=brand_ids)
        if brand_name:
            brand_ids = Brand.objects.filter(name__icontains=brand_name).values_list('id', flat=True)
            brand_filters &= Q(brand_id__in=brand_ids)

        return brand_filters

    @staticmethod
    def filter_by_size(query_params):
        size = query_params.getlist('size')
        size_filters = Q()

        if size:
            size_filters &= Q(productsize__size_id__in=size)

        return size_filters

    @staticmethod
    def filter_by_price(query_params):
        min_price = query_params.get('min_price')
        max_price = query_params.get('max_price')
        has_price = query_params.get('has_price')

        price_filters = Q()

        if min_price:
            price_filters &= Q(productcurrency__price__gte=min_price)
        if max_price:
            price_filters &= Q(productcurrency__price__lte=max_price)
        if has_price == 'true':
            price_filters &= Q(productcurrency__price__isnull=False)
        if has_price == 'false':
            price_filters &= Q(productcurrency__price__isnull=True)

        return price_filters

    @staticmethod
    def filter_by_color(query_params):
        color_id = query_params.get('color')
        color_filters = Q()

        if color_id:
            color_filters &= Q(producttype__color_id=color_id)

        return color_filters

    @staticmethod
    def filter_by_country(query_params):
        country_ids = query_params.getlist('country')
        country_filters = Q()

        if country_ids:
            country_filters &= Q(productcountry__country_id__in=country_ids)

        return country_filters

    @staticmethod
    def filter_by_currency(query_params):
        currency_id = query_params.get('currency')
        currency_filters = Q()

        if currency_id:
            currency_filters &= Q(productcurrency__currency_id=currency_id)

        return currency_filters

    @staticmethod
    def filter_by_color_name(query_params):
        color_name = query_params.get('color_filter')
        color_filters = Q()

        if color_name:
            color_filters &= Q(producttype__color__name__icontains=color_name)

        return color_filters

    @staticmethod
    def filter_by_size_name(query_params):
        size_name = query_params.getlist('size_filter')

        size_filters = Q()

        if size_name:
            try:
                size_queries = Q()
                for name in size_name:
                    size_queries |= Q(raw_size__icontains=name)
                sizes = Size.objects.filter(size_queries).values_list('id', flat=True)
                size_filters &= Q(productsize__size_id__in=sizes)
            except Size.DoesNotExist:
                return Q(pk__in=[])

        return size_filters

    @staticmethod
    def category_filtered_queryset(query_params):
        category_id = query_params.get('category')# Подставьте свой способ получения категории

        if not category_id:
            products = Product.objects.all()
        else:
            products = Product.objects.filter(productcategory__category_id=category_id)
        min_price_value = products.aggregate(min_price=Min('productcurrency__price'))['min_price']
        max_price_value = products.aggregate(max_price=Max('productcurrency__price'))['max_price']

        return max_price_value, min_price_value

    def get_max_price(self):
        max_price_value = self.category_filtered_queryset.aggregate(Max('productcurrency__price'))['productcurrency__price__max']
        return max_price_value

    def get_min_price(self):
        min_price_value = self.category_filtered_queryset.aggregate(Min('productcurrency__price'))['productcurrency__price__min']
        return min_price_value

    @staticmethod
    def filter_by_search(query_params):
        search_query = query_params.get('search')
        search_filters = Q()

        if search_query:
            search_filters &= (
                    Q(title_ru__icontains=search_query) |
                    Q(title_en__icontains=search_query) |
                    Q(brand__name__icontains=search_query)
            )

        return search_filters

    @action(detail=False, methods=['post'], url_path='ids')
    def get_products_by_ids(self, request, *args, **kwargs):
        ids = request.data.get('ids', [])
        if not ids:
            return Response({"detail": "IDs list is required."}, status=status.HTTP_400_BAD_REQUEST)

        queryset = self.get_queryset().filter(id__in=ids)
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)