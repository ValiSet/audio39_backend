from rest_framework import serializers
from api.models import Size, ProductSize

class SizeSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Size
        fields = ['id', 'name', 'product_count']

    @staticmethod
    def get_name(obj):
        return obj.raw_size

    @staticmethod
    def parse_size_string(size_str):
        """
        Разбирает строку размера и возвращает словарь с ключами 'name' и 'available'.
        """
        name = size_str.strip()
        available = True
        return {'name': name, 'available': available}

    def get_product_count(self, obj):
        if hasattr(obj, 'product_count'):
            return obj.product_count
        return ProductSize.objects.filter(size=obj).count()