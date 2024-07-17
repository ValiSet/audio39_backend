from rest_framework import serializers
from api.models import SizeTable


class SizeTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = SizeTable
        fields = ['name', 'category_id', 'data']