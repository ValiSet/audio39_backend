from rest_framework import serializers
from api.models import Country, ProductCountry


class CountrySerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Country.
    """
    product_count = serializers.SerializerMethodField()
    class Meta:
        model = Country
        fields = ['id', 'name_ru', 'name_en', 'iso_code', 'flag_url','product_count']

    def get_product_count(self, obj):
        if hasattr(obj, 'product_count'):
            return obj.product_count
        return ProductCountry.objects.filter(country=obj).count()


class ProductCountrySerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели ProductCountry, связанной с Country.
    """
    country = CountrySerializer()

    class Meta:
        model = ProductCountry
        fields = ['country']
