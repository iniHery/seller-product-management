from django.urls import path
from .views import CategoryAPIView, ProductAPIView, ProductDetailAPIView, CategoryDetailAPIView

urlpatterns = [
    path('categories/', CategoryAPIView.as_view(), name='category-list'),
    path('categories/<uuid:id>/', CategoryDetailAPIView.as_view(), name='category-detail'),
    path('products/', ProductAPIView.as_view(), name='product-list'),
    path('products/<uuid:id>/', ProductDetailAPIView.as_view(), name='product-detail'),
]