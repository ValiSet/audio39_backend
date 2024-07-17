from django.contrib import admin
from .models import (
    Product, Category, Image, Size, Country, Brand, Color, Currency,
    ProductCategory, ProductCurrency, ProductCountry, SizeTable
)
from mptt.admin import MPTTModelAdmin


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name_ru', 'id')


class SizeAdmin(MPTTModelAdmin):
    list_display = ['category_name', 'raw_size']

    @admin.display(description='Category Name')
    def category_name(self, obj):
        return obj.category.name_ru


admin.site.register(Product)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Size, SizeAdmin)

models = [Country, Brand, Color, Currency, Image, ProductCategory, ProductCurrency, ProductCountry]
for model in models:
    admin.site.register(model)


@admin.register(SizeTable)
class SizeTableAdmin(admin.ModelAdmin):
    list_display = ('name', 'category_id')
    search_fields = ('name', 'category_id')
    list_filter = ('category_id',)