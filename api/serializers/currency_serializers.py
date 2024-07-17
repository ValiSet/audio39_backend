from rest_framework import serializers
from api.models import ProductCurrency, Currency


class CurrencySerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Currency.
    """
    count_products = serializers.SerializerMethodField()

    class Meta:
        model = Currency
        fields = ['id', 'name', 'symbol', 'code', 'count_products']

    def get_count_products(self, obj):
        try:
            return ProductCurrency.objects.filter(currency=obj).count()
        except Exception as e:
            print(f"Error counting products for country {obj.id}: {e}")
            return 0


class ProductCurrencySerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели ProductCurrency, связанной с Currency.
    """
    currency = CurrencySerializer()
    price = serializers.SerializerMethodField()
    def get_price(self, obj):
        return obj.price

    class Meta:
        model = ProductCurrency
        fields = ['currency', 'price']
