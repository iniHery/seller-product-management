from django.db import IntegrityError, transaction
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Category, Product
from .pagination import ProductPagination
from .serializers import CategorySerializer, ProductSerializer


def _save_with_seller_unique_value(serializer, model, user, field, message, **save_kwargs):
    try:
        with transaction.atomic():
            return serializer.save(**save_kwargs)
    except IntegrityError as error:
        value = serializer.validated_data.get(field)
        if value is not None:
            duplicates = model.objects.filter(
                seller=user,
                deleted_at__isnull=True,
                **{field: value},
            )
            if serializer.instance:
                duplicates = duplicates.exclude(pk=serializer.instance.pk)
            if duplicates.exists():
                raise ValidationError({field: [message]}) from error
        raise


class CategoryAPIView(APIView):
    """GET: list categories, POST: create a new category"""

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        categories = Category.objects.filter(
            seller=request.user,
            deleted_at__isnull=True,
        )
        serializer = CategorySerializer(categories, many=True)
        return Response(
            {"success": True, "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    def post(self, request, *args, **kwargs):
        serializer = CategorySerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        _save_with_seller_unique_value(
            serializer,
            Category,
            request.user,
            "name",
            "Nama kategori sudah digunakan pada toko Anda.",
            seller=request.user,
            created_by=request.user,
            updated_by=request.user,
        )
        return Response(
            {"success": True, "data": serializer.data},
            status=status.HTTP_201_CREATED,
        )


class CategoryDetailAPIView(APIView):
    """GET: retrieve a single category by UUID"""

    permission_classes = [IsAuthenticated]

    def get(self, request, id, *args, **kwargs):
        category = get_object_or_404(
            Category,
            pk=id,
            seller=request.user,
            deleted_at__isnull=True,
        )
        serializer = CategorySerializer(category)
        return Response(
            {"success": True, "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    def put(self, request, id, *args, **kwargs):
        """Update a category by UUID"""
        category = get_object_or_404(
            Category,
            pk=id,
            seller=request.user,
            deleted_at__isnull=True,
        )
        serializer = CategorySerializer(
            category,
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        _save_with_seller_unique_value(
            serializer,
            Category,
            request.user,
            "name",
            "Nama kategori sudah digunakan pada toko Anda.",
            updated_by=request.user,
        )
        return Response(
            {"success": True, "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    def patch(self, request, id, *args, **kwargs):
        """Partial update a category by UUID"""
        category = get_object_or_404(
            Category,
            pk=id,
            seller=request.user,
            deleted_at__isnull=True,
        )
        serializer = CategorySerializer(
            category,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        _save_with_seller_unique_value(
            serializer,
            Category,
            request.user,
            "name",
            "Nama kategori sudah digunakan pada toko Anda.",
            updated_by=request.user,
        )
        return Response(
            {"success": True, "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    def delete(self, request, id, *args, **kwargs):
        category = get_object_or_404(
            Category,
            pk=id,
            seller=request.user,
            deleted_at__isnull=True,
        )
        if Product.objects.filter(category=category, deleted_at__isnull=True).exists():
            return Response(
                {
                    "success": False,
                    "message": "Kategori tidak dapat dihapus karena masih digunakan produk aktif.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        category.soft_delete(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductAPIView(APIView):
    """GET: list products, POST: create a new product (seller set from request.user)"""

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        products = Product.objects.select_related("category", "seller").filter(
            seller=request.user,
            deleted_at__isnull=True,
        )

        search = request.query_params.get('search', '').strip()
        if search:
            products = products.filter(
                Q(name__icontains=search) | Q(sku__icontains=search)
            )

        category = request.query_params.get('category', '').strip()
        if category:
            products = products.filter(category__name__icontains=category)

        status_param = request.query_params.get('status', '').strip()
        if status_param:
            products = products.filter(status=status_param)

        products = products.order_by('-created_at', '-id')

        paginator = ProductPagination()
        paginated_qs = paginator.paginate_queryset(products, request, view=self)
        serializer = ProductSerializer(
            paginated_qs,
            many=True,
            context={"request": request},
        )
        paginated_response = paginator.get_paginated_response(serializer.data)
        return Response(
            {"success": True, "data": paginated_response.data},
            status=status.HTTP_200_OK,
        )

    def post(self, request, *args, **kwargs):
        serializer = ProductSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        _save_with_seller_unique_value(
            serializer,
            Product,
            request.user,
            "sku",
            "SKU sudah digunakan pada toko Anda.",
            seller=request.user,
            created_by=request.user,
            updated_by=request.user,
        )
        return Response(
            {"success": True, "data": serializer.data},
            status=status.HTTP_201_CREATED,
        )


class ProductDetailAPIView(APIView):
    """Product detail operations for the authenticated seller."""

    permission_classes = [IsAuthenticated]

    def get_object(self, id, user):
        return get_object_or_404(
            Product.objects.select_related("category", "seller"),
            pk=id,
            seller=user,
            deleted_at__isnull=True,
        )

    def get(self, request, id, *args, **kwargs):
        product = self.get_object(id, request.user)
        serializer = ProductSerializer(product, context={"request": request})
        return Response(
            {"success": True, "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    def put(self, request, id, *args, **kwargs):
        product = self.get_object(id, request.user)
        serializer = ProductSerializer(
            product,
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        _save_with_seller_unique_value(
            serializer,
            Product,
            request.user,
            "sku",
            "SKU sudah digunakan pada toko Anda.",
            updated_by=request.user,
        )
        return Response(
            {"success": True, "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    def patch(self, request, id, *args, **kwargs):
        """Partial update a product by UUID"""
        product = self.get_object(id, request.user)
        serializer = ProductSerializer(
            product,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        _save_with_seller_unique_value(
            serializer,
            Product,
            request.user,
            "sku",
            "SKU sudah digunakan pada toko Anda.",
            updated_by=request.user,
        )
        return Response(
            {"success": True, "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    def delete(self, request, id, *args, **kwargs):
        """Delete a product by UUID"""
        product = self.get_object(id, request.user)
        product.soft_delete(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class DashboardAPIView(APIView):
    """GET: return dashboard statistics for the authenticated seller"""
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        qs = Product.objects.filter(
            seller=request.user,
            deleted_at__isnull=True,
        )
        total_products = qs.count()
        active_products = qs.filter(status='active').count()
        inactive_products = qs.filter(status='inactive').count()
        total_stock = qs.aggregate(Sum('stock'))['stock__sum'] or 0

        data = {
            "total_products": total_products,
            "active_products": active_products,
            "inactive_products": inactive_products,
            "total_stock": total_stock,
        }
        return Response({"success": True, "data": data}, status=status.HTTP_200_OK)
