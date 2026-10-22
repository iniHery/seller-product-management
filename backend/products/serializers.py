from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Category, Product

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    def validate_name(self, value):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return value

        categories = Category.objects.filter(
            seller=request.user,
            name=value,
            deleted_at__isnull=True,
        )
        if self.instance:
            categories = categories.exclude(pk=self.instance.pk)

        if categories.exists():
            raise serializers.ValidationError(
                "Nama kategori sudah digunakan pada toko Anda."
            )

        return value

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
            "deleted_at",
            "deleted_by",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
            "deleted_at",
            "deleted_by",
        ]


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
    category = ProductCategorySerializer(read_only=True)
    seller = SellerSerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        source="category", queryset=Category.objects.none(), write_only=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            self.fields["category_id"].queryset = Category.objects.filter(
                seller=request.user,
                deleted_at__isnull=True,
            )

    def validate_sku(self, value):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return value

        products = Product.objects.filter(
            seller=request.user,
            sku=value,
            deleted_at__isnull=True,
        )
        if self.instance:
            products = products.exclude(pk=self.instance.pk)

        if products.exists():
            raise serializers.ValidationError(
                "SKU sudah digunakan pada toko Anda."
            )

        return value

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
            "created_by",
            "updated_at",
            "updated_by",
            "deleted_at",
            "deleted_by",
            "category",
            "category_id",
            "seller",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
            "deleted_at",
            "deleted_by",
            "category",
            "seller",
        ]


class ProductCSVRowSerializer(serializers.Serializer):
    name = serializers.CharField(
        max_length=255,
        required=True,
        error_messages={
            "required": "Nama produk wajib diisi.",
            "blank": "Nama produk tidak boleh kosong.",
        },
    )
    sku = serializers.CharField(
        max_length=100,
        required=True,
        error_messages={
            "required": "SKU wajib diisi.",
            "blank": "SKU tidak boleh kosong.",
        },
    )
    category = serializers.CharField(
        max_length=255,
        required=True,
        error_messages={
            "required": "Kategori wajib diisi.",
            "blank": "Kategori tidak boleh kosong.",
        },
    )
    price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0,
        required=True,
        error_messages={
            "required": "Harga wajib diisi.",
            "invalid": "Harga harus berupa angka yang valid.",
            "min_value": "Harga tidak boleh bernilai negatif.",
        },
    )
    stock = serializers.IntegerField(
        min_value=0,
        required=True,
        error_messages={
            "required": "Stok wajib diisi.",
            "invalid": "Stok harus berupa bilangan bulat yang valid.",
            "min_value": "Stok tidak boleh bernilai negatif.",
        },
    )
    status = serializers.ChoiceField(
        choices=["active", "inactive"],
        default="active",
        required=False,
        error_messages={
            "invalid_choice": "Status hanya boleh 'active' atau 'inactive'.",
        },
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )
