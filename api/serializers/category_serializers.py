from rest_framework import serializers
from api.models import Category, ProductCategory

class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name_ru', 'name_en', 'slug', 'parent', 'children']

    def get_children(self, obj):
        """
        Рекурсивно сериализует дочерние категории.
        """
        children_queryset = obj.get_children()
        serializer = self.__class__(children_queryset, many=True, context=self.context)
        return serializer.data if children_queryset else None


class ProductCategorySerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели ProductCategory, связанной с Category.
    """
    category = CategorySerializer()

    class Meta:
        model = ProductCategory
        fields = ['category']