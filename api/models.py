from django.db import models
from autoslug import AutoSlugField
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey

# Brand model
class Brand(models.Model):
    name = models.CharField(max_length=100)
    image_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


# Product model
class Product(models.Model):
    article = models.CharField(max_length=200, unique=True, blank=True, null=True)
    title_ru = models.CharField(_("Title (RU)"), max_length=200, null=True, blank=True)
    title_en = models.CharField(_("Title (EN)"), max_length=200)
    slug = AutoSlugField(max_length=200, unique=True, populate_from='title_en')
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    info_ru = models.TextField(_("Info (RU)"), null=True, blank=True)
    info = models.TextField(_("Info"), null=True, blank=True)
    product_url = models.TextField(blank=True, null=True)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    website_name = models.CharField(max_length=200, blank=True, null=True)
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=0.0)
    popularity = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['title_ru']
        indexes = [
            models.Index(fields=['id', 'slug']),
            models.Index(fields=['title_ru']),
            models.Index(fields=['title_en']),
            models.Index(fields=['created']),
            models.Index(fields=['updated']),
            models.Index(fields=['brand']),
            models.Index(fields=['rating']),
            models.Index(fields=['popularity']),
        ]
        verbose_name = _('product')
        verbose_name_plural = _('products')

    def __str__(self):
        if self.title_ru:
            return self.title_ru
        else:
            return self.title_en

    def get_sizes(self):
        product_color_sizes = ProductType.objects.filter(product=self)
        sizes = [pcs.size.international_size for pcs in product_color_sizes if pcs.size and pcs.size.international_size]
        return sizes

    def get_categories(self):
        return [pc.category for pc in self.productcategory_set.all()] if self.productcategory_set.exists() else []


# Image model
class Image(models.Model):
    product = models.ForeignKey('Product', related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='static/product_images/%Y/%m/%d', max_length=500, blank=True, null=True)
    image_original = models.JSONField(blank=True, null=True)


    def __str__(self):
        return self.product.title_en


# Category model
class Category(MPTTModel):
    name_ru = models.CharField(_("Name (RU)"), max_length=200, null=True, blank=True)
    name_en = models.CharField(_("Name (EN)"), max_length=200)
    slug = AutoSlugField(max_length=255, unique=True, populate_from='name_en')
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    class MPTTMeta:
        order_insertion_by = ['name_ru']

    def __str__(self):
        return self.name_ru or self.name_en

    class Meta:
        default_related_name = 'categories'


# ProductCategory model
class ProductCategory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('product', 'category'),)

        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['category']),
        ]
    def __str__(self):
        return f' {self.product} - {self.category}'


# Size model
class Size(models.Model):
    raw_size = models.CharField(max_length=100, blank=True, null=True)
    international_size = models.CharField(max_length=100, blank=True, null=True)
    russian_size = models.CharField(max_length=100, blank=True, null=True)
    us_size = models.CharField(max_length=100, blank=True, null=True)
    eu_size = models.CharField(max_length=100, blank=True, null=True)
    uk_size = models.CharField(max_length=100, blank=True, null=True)
    jp_size = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.russian_size or self.international_size


# Color model
class Color(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)
    code = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.name

class ProductSize(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    is_available = models.BooleanField(default=True)

    class Meta:
        unique_together = ('product', 'size')
        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['size']),
            models.Index(fields=['is_available']),
        ]


# ProductVariant model
class ProductType(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True)
    color = models.ForeignKey('Color', on_delete=models.CASCADE, blank=True, null=True)
    type = models.JSONField(null=True, blank=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['color']),
            models.Index(fields=['type']),
            models.Index(fields=['is_available']),
        ]


# Country model
class Country(models.Model):
    name_ru = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100)
    iso_code = models.CharField(max_length=10, blank=True, null=True)
    flag_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name_ru


class ProductCountry(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('product', 'country'),)

    def __str__(self):
        return f' {self.product} - {self.country}'


# Currency model
class Currency(models.Model):
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=10)
    code = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class ProductCurrency(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    available = models.BooleanField(default=True)

    class Meta:
        unique_together = (('product', 'currency'),)

        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['price']),
            models.Index(fields=['discount_price']),
        ]

    def __str__(self):
        return f' {self.product} - {self.currency}'


class SizeTable(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    category_id = models.IntegerField( unique=True, null=True, blank=True)
    data = models.JSONField()

    def __str__(self):
        if self.name:
            return self.name
        return str(self.category_id)

