from django.urls import path

from .views import (
    CategoryAPIView,
    CategoryDetailAPIView,
    DashboardAPIView,
    ProductAPIView,
    ProductDetailAPIView,
    ProductExportCSVAPIView,
    ProductImportCSVAPIView,
    ProductTemplateCSVAPIView,
)

urlpatterns = [
    path('categories/', CategoryAPIView.as_view(), name='category-list'),
    path('categories/<uuid:id>/', CategoryDetailAPIView.as_view(), name='category-detail'),
    path('products/', ProductAPIView.as_view(), name='product-list'),
    path('products/export/', ProductExportCSVAPIView.as_view(), name='product-export-csv'),
    path('products/template/', ProductTemplateCSVAPIView.as_view(), name='product-template-csv'),
    path('products/import/', ProductImportCSVAPIView.as_view(), name='product-import-csv'),
    path('products/<uuid:id>/', ProductDetailAPIView.as_view(), name='product-detail'),
    path('dashboard/', DashboardAPIView.as_view(), name='dashboard'),
]