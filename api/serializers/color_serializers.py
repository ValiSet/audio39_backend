from rest_framework import serializers
from api.models import Color, ProductType


class ColorSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Color.
    """
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Color
        fields = ['id', 'name', 'code', 'product_count']

    def get_product_count(self, obj):
        if hasattr(obj, 'product_count'):
            return obj.product_count
        return ProductType.objects.filter(color=obj).count()
