from django.db import IntegrityError, transaction
from django.db.models import Count, F, Q, Sum
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

        stock_status = request.query_params.get('stock_status', '').strip().lower()
        if stock_status == 'low':
            products = products.filter(stock__gt=0, stock__lte=5)
        elif stock_status == 'out':
            products = products.filter(stock=0)
        elif stock_status == 'critical':
            products = products.filter(stock__lte=5)
        elif stock_status == 'in_stock':
            products = products.filter(stock__gt=5)

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

        # Tahap 1: Stok menipis (1-5 unit) dan stok habis (0 unit)
        active_qs = qs.filter(status='active')
        low_stock_products = active_qs.filter(stock__gt=0, stock__lte=5).count()
        out_of_stock_products = active_qs.filter(stock=0).count()

        # Tahap 4: Total Valuasi Inventaris (Harga * Stok) pada produk aktif
        valuation_agg = active_qs.aggregate(total=Sum(F('price') * F('stock')))['total']
        total_valuation = float(valuation_agg) if valuation_agg is not None else 0.0

        # Tahap 4: Distribusi Kategori (Top kategori beserta persentase)
        category_counts = (
            active_qs.filter(category__deleted_at__isnull=True)
            .values('category__id', 'category__name')
            .annotate(count=Count('id'))
            .order_by('-count')[:5]
        )
        category_distribution = [
            {
                "category_id": str(item['category__id']) if item['category__id'] else None,
                "category_name": item['category__name'] or 'Tanpa Kategori',
                "count": item['count'],
                "percentage": round((item['count'] / active_products * 100), 1) if active_products > 0 else 0,
            }
            for item in category_counts
        ]

        # Tahap 4: 5 Produk Paling Kritis (Stok <= 5) untuk Quick Restock Action
        critical_qs = (
            active_qs.select_related('category')
            .filter(stock__lte=5)
            .order_by('stock', 'name')[:5]
        )
        critical_products = [
            {
                "id": str(p.id),
                "name": p.name,
                "sku": p.sku,
                "stock": p.stock,
                "category_name": p.category.name if p.category else "-",
                "price": str(p.price),
                "is_out_of_stock": p.stock == 0,
            }
            for p in critical_qs
        ]

        data = {
            "total_products": total_products,
            "active_products": active_products,
            "inactive_products": inactive_products,
            "total_stock": total_stock,
            "low_stock_products": low_stock_products,
            "out_of_stock_products": out_of_stock_products,
            "total_valuation": total_valuation,
            "category_distribution": category_distribution,
            "critical_products": critical_products,
        }
        return Response({"success": True, "data": data}, status=status.HTTP_200_OK)
