from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q

from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated


class CategoryAPIView(APIView):
    """GET: list categories, POST: create a new category"""

    def get(self, request, *args, **kwargs):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = CategorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_201_CREATED)

class CategoryDetailAPIView(APIView):
    """GET: retrieve a single category by UUID"""

    def get(self, request, id, *args, **kwargs):
        category = get_object_or_404(Category, pk=id)
        serializer = CategorySerializer(category)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    def put(self, request, id, *args, **kwargs):
        """Update a category by UUID"""
        category = get_object_or_404(Category, pk=id)
        serializer = CategorySerializer(category, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    def patch(self, request, id, *args, **kwargs):
        """Partial update a category by UUID"""
        category = get_object_or_404(Category, pk=id)
        serializer = CategorySerializer(category, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    def delete(self, request, id, *args, **kwargs):
        """Delete a category by UUID"""
        category = get_object_or_404(Category, pk=id)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductAPIView(APIView):
    """GET: list products, POST: create a new product (seller set from request.user)"""
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Only return products belonging to the authenticated seller
        products = Product.objects.select_related('category', 'seller').filter(seller=request.user)

        # Search by name or SKU (already implemented)
        search = request.query_params.get('search', '').strip()
        if search:
            products = products.filter(Q(name__icontains=search) | Q(sku__icontains=search))

        # Category filter
        category = request.query_params.get('category', '').strip()
        if category:
            products = products.filter(category__name__icontains=category)

        # Status filter
        status_param = request.query_params.get('status', '').strip()
        if status_param:
            products = products.filter(status=status_param)

        # ----- Pagination (Task 27.4) -----
        from .pagination import ProductPagination
        paginator = ProductPagination()
        paginated_qs = paginator.paginate_queryset(products, request, view=self)
        serializer = ProductSerializer(paginated_qs, many=True)
        paginated_response = paginator.get_paginated_response(serializer.data)
        # Wrap with success flag as required by project
        return Response({"success": True, "data": paginated_response.data}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Assign the seller from the authenticated user
        serializer.save(seller=request.user)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_201_CREATED)

class ProductDetailAPIView(APIView):
    """GET, PUT, PATCH, DELETE: operate on a product belonging to the authenticated seller"""
    permission_classes = [IsAuthenticated]

    def get_object(self, id, user):
        # Helper to fetch product owned by the seller or raise 404
        return get_object_or_404(Product.objects.select_related('category', 'seller'), pk=id, seller=user)

    def get(self, request, id, *args, **kwargs):
        product = self.get_object(id, request.user)
        serializer = ProductSerializer(product)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    def put(self, request, id, *args, **kwargs):
        product = self.get_object(id, request.user)
        serializer = ProductSerializer(product, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    def patch(self, request, id, *args, **kwargs):
        """Partial update a product by UUID"""
        product = self.get_object(id, request.user)
        serializer = ProductSerializer(product, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    def delete(self, request, id, *args, **kwargs):
        """Delete a product by UUID"""
        product = self.get_object(id, request.user)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

