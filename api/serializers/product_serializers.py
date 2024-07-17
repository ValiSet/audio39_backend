import re
from rest_framework import serializers
from django.forms.models import model_to_dict
from api.models import Product, ProductCategory, ProductCountry, ProductCurrency, ProductSize, ProductType, Image
from api.serializers.color_serializers import ColorSerializer
from api.serializers.country_serializers import ProductCountrySerializer
from api.serializers.image_serializers import ImageSerializer
from api.serializers.brand_serializers import BrandSerializer
from api.serializers.currency_serializers import ProductCurrencySerializer


class ProductSerializer(serializers.ModelSerializer):
    categories = serializers.SerializerMethodField()
    brand = BrandSerializer(read_only=True)
    countries = serializers.SerializerMethodField()
    currencies = ProductCurrencySerializer(source='productcurrency_set', many=True)
    images = ImageSerializer(many=True)
    colors = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'article', 'title_ru', 'title_en', 'slug', 'info', 'info_ru', 'weight', 'available',
            'rating', 'popularity', 'categories', 'brand', 'countries', 'currencies', 'images', 'colors'
        ]

    def get_countries(self, obj):
        """
        Получает список стран, связанных с продуктом, включая их данные.
        """
        countries_qs = ProductCountry.objects.filter(product=obj)

        countries_data = ProductCountrySerializer(countries_qs, many=True, context=self.context).data
        return [country['country'] for country in countries_data]

    @staticmethod
    def get_categories(obj):
        """
        Получает список категорий продукта без дочерних элементов.
        """
        categories_qs = ProductCategory.objects.filter(product=obj)
        categories_data = [model_to_dict(category.category) for category in categories_qs]
        for category_data in categories_data:
            category_data.pop('children', None)
        return categories_data

    @staticmethod
    def parse_size_string(size_str):
        """
        Разбирает строку размера и возвращает словарь с ключами 'name' и 'available'.
        """
        pattern = r'^(.*?)\s*-\s*(.*?)$'
        match = re.match(pattern, size_str)

        if match:
            name = match.group(0).strip()
            available = True
            return {'name': name, 'available': available}
        return None

    def get_sizes_for_color(self, product_type):
        sizes_data = []

        try:
            price = self.get_price_for_color(product_type)
            discount_price = self.get_discount_price_for_color(product_type)
            product_sizes = ProductSize.objects.filter(product=product_type.product)

            for product_size in product_sizes:
                size_obj = {
                    'id': product_size.size.id,
                    'name': product_size.size.raw_size,
                    'available': product_size.is_available,
                    'price': price,
                    'discount_price': discount_price,
                }
                sizes_data.append(size_obj)

        except (ProductCurrency.DoesNotExist, ProductType.DoesNotExist):
            pass

        return sizes_data

    @staticmethod
    def get_price_for_color(product_type):
        try:
            return ProductCurrency.objects.get(product_id=product_type.product_id).price
        except ProductCurrency.DoesNotExist:
            return None

    @staticmethod
    def get_discount_price_for_color(product_type):
        try:
            return ProductCurrency.objects.get(product_id=product_type.product_id).discount_price
        except ProductCurrency.DoesNotExist:
            return None

    def get_colors(self, obj):
        """
        Получает список доступных цветов для продукта, включая изображения и размеры для каждого цвета.
        """
        try:
            product_types = ProductType.objects.filter(product_id=obj.id).select_related('color')

            colors_data = []
            for product_type in product_types:
                color_serializer = ColorSerializer(product_type.color)
                color_data = color_serializer.data

                image_original = Image.objects.filter(product_id=obj.id).first().image_original
                color_data['image_original'] = image_original

                sizes_data = self.get_sizes_for_color(product_type)
                color_data['sizes'] = sizes_data

                colors_data.append(color_data)

            return colors_data

        except Exception as e:
            print(f"Error fetching ProductTypes for product_id {obj.id}: {e}")
            return []