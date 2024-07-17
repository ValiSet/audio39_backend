from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import size_views, brand_views, product_views, category_views, image_views , color_views, country_views, currency_views, size_table_views

app_name = 'api'

router = DefaultRouter()
router.register(r'products', product_views.ProductViewSet)
router.register(r'categories', category_views.CategoryViewSet)
router.register(r'images', image_views.ImageViewSet)
router.register(r'brands', brand_views.BrandViewSet)
router.register(r'sizes', size_views.SizeViewSet)
router.register(r'colors', color_views.ColorViewSet)
router.register(r'countries', country_views.CountryViewSet)
router.register(r'currencies', currency_views.CurrencyViewSet)
router.register(r'sizetable', size_table_views.SizeTableViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('brand/<int:brand_id>/products/', brand_views.ProductByBrandViewSet.as_view({'get': 'list'}), name='products-by-brand'),
    path('categories/<int:category_id>/products/', category_views.ProductByCategoryViewSet.as_view({'get': 'list'}), name='products-by-categories'),
]

