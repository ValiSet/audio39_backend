from rest_framework import serializers
from api.models import Image


class ImageSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Image, включает поле 'id' и 'image_original'.
    """
    class Meta:
        model = Image
        fields = ['id', 'image_original']
