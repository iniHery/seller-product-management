from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Category, Product

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]
        read_only_fields = ["id", "name"]


class SellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]
        read_only_fields = ["id", "username", "email"]


class ProductSerializer(serializers.ModelSerializer):
    # read-only nested representations
    category = ProductCategorySerializer(read_only=True)
    seller = SellerSerializer(read_only=True)
    # write-only PK fields mapping to relationships
    category_id = serializers.PrimaryKeyRelatedField(
        source="category", queryset=Category.objects.all(), write_only=True
    )


    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "sku",
            "description",
            "price",
            "stock",
            "status",
            "created_at",
            "updated_at",
            "category",
            "category_id",
            "seller",

        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "category",
            "seller",
        ]

    # No extra validation needed; model validators handle price, stock, and unique SKU.
