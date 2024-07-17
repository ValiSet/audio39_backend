from rest_framework import serializers
from api.models import Brand
from api.models import Product


class BrandSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Brand.
    """
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Brand
        fields = ['id', 'name', 'image_url', 'product_count']

    def get_product_count(self, obj):
        if hasattr(obj, 'product_count'):
            return obj.product_count
        return Product.objects.filter(brand=obj).count()
