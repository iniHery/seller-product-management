from django.urls import path
from .views import CategoryAPIView, ProductAPIView

urlpatterns = [
    path('categories/', CategoryAPIView.as_view(), name='category-list'),
    path('products/', ProductAPIView.as_view(), name='product-list'),
]
