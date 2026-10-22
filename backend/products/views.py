import csv
import io

from django.db import IntegrityError, transaction
from django.db.models import Count, F, Q, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Category, Product
from .pagination import ProductPagination
from .serializers import (
    CategorySerializer,
    ProductCSVRowSerializer,
    ProductSerializer,
)


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
    # Existing methods omitted for brevity
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
        # Note: CSV export endpoint does not use pagination; see ProductExportCSVAPIView
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


class ProductExportCSVAPIView(APIView):
    """GET: Export seller's products as formatted CSV with optional filtering."""

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        products = Product.objects.select_related("category").filter(
            seller=request.user,
            deleted_at__isnull=True,
        )

        search = request.query_params.get("search", "").strip()
        if search:
            products = products.filter(
                Q(name__icontains=search) | Q(sku__icontains=search)
            )

        category = request.query_params.get("category", "").strip()
        if category:
            products = products.filter(category__name__icontains=category)

        status_param = request.query_params.get("status", "").strip()
        if status_param:
            products = products.filter(status=status_param)

        stock_status = request.query_params.get("stock_status", "").strip().lower()
        if stock_status == "low":
            products = products.filter(stock__gt=0, stock__lte=5)
        elif stock_status == "out":
            products = products.filter(stock=0)
        elif stock_status == "critical":
            products = products.filter(stock__lte=5)
        elif stock_status == "in_stock":
            products = products.filter(stock__gt=5)

        products = products.order_by("-created_at", "-id")

        response = HttpResponse(
            content_type="text/csv; charset=utf-8",
        )
        date_str = timezone.now().strftime("%d-%m-%Y")
        response["Content-Disposition"] = f'attachment; filename="produk-{date_str}.csv"'

        # Write UTF-8 BOM so Excel and spreadsheet applications display Indonesian characters and formatting correctly
        response.write("\ufeff")

        writer = csv.writer(response)
        writer.writerow([
            "No.",
            "SKU",
            "Nama Produk",
            "Kategori",
            "Harga Satuan",
            "Stok",
            "Total Nilai Stok",
            "Status",
            "Tanggal Terdaftar",
            "Deskripsi",
        ])

        for idx, p in enumerate(products, start=1):
            price_val = f"{p.price:.2f}"
            if price_val.endswith(".00"):
                price_val = price_val[:-3]

            total_val = f"{(p.price * p.stock):.2f}"
            if total_val.endswith(".00"):
                total_val = total_val[:-3]

            status_label = "Aktif" if p.status == "active" else "Tidak Aktif"
            created_str = (
                timezone.localtime(p.created_at).strftime("%d/%m/%Y %H:%M")
                if p.created_at
                else "-"
            )
            clean_desc = (p.description or "").replace("\r", " ").replace("\n", " ").strip()

            writer.writerow([
                idx,
                p.sku,
                p.name,
                p.category.name if p.category else "-",
                price_val,
                p.stock,
                total_val,
                status_label,
                created_str,
                clean_desc,
            ])

        return response


class ProductTemplateCSVAPIView(APIView):
    """GET: Download a formatted CSV template with sample product rows."""

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        response = HttpResponse(
            content_type="text/csv; charset=utf-8",
        )
        date_str = timezone.now().strftime("%d-%m-%Y")
        response["Content-Disposition"] = f'attachment; filename="template-import-produk-{date_str}.csv"'
        response.write("\ufeff")

        writer = csv.writer(response)
        writer.writerow(["SKU", "Nama Produk", "Kategori", "Harga", "Stok", "Status", "Deskripsi"])
        writer.writerow(["PROD-001", "Kopi Arabika Gayo 250g", "Minuman", "45000", "50", "active", "Biji kopi arabika pilihan single origin"])
        writer.writerow(["PROD-002", "Teh Hijau Organik", "Minuman", "25000", "100", "active", "Teh hijau melati alami"])

        return response


class ProductImportCSVAPIView(APIView):
    """POST: Import products from CSV with robust column, type, duplicate, and category validation."""

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        uploaded_file = request.FILES.get("file")
        if not uploaded_file:
            return Response(
                {"success": False, "message": "File CSV wajib diunggah."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not uploaded_file.name.lower().endswith(".csv"):
            return Response(
                {"success": False, "message": "Format file tidak valid. Harap unggah file berekstensi .csv."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if uploaded_file.size > 5 * 1024 * 1024:
            return Response(
                {"success": False, "message": "Ukuran file terlalu besar. Maksimal 5 MB."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            content = uploaded_file.read()
            try:
                decoded_file = content.decode("utf-8-sig")
            except UnicodeDecodeError:
                decoded_file = content.decode("latin-1")
        except Exception:
            return Response(
                {"success": False, "message": "Gagal membaca isi file CSV. Pastikan encoding file valid."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        csv_reader = csv.reader(io.StringIO(decoded_file))
        rows = list(csv_reader)

        if not rows:
            return Response(
                {"success": False, "message": "File CSV kosong."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        raw_headers = rows[0]
        header_map = {}
        canonical_map = {
            "sku": "sku",
            "kode sku": "sku",
            "product sku": "sku",
            "name": "name",
            "nama": "name",
            "nama produk": "name",
            "product name": "name",
            "category": "category",
            "kategori": "category",
            "kategori produk": "category",
            "price": "price",
            "harga": "price",
            "harga satuan": "price",
            "harga produk": "price",
            "unit price": "price",
            "stock": "stock",
            "stok": "stock",
            "jumlah stok": "stock",
            "status": "status",
            "status produk": "status",
            "description": "description",
            "deskripsi": "description",
            "keterangan": "description",
        }

        for idx, h in enumerate(raw_headers):
            clean_h = h.strip().lower()
            if clean_h in canonical_map:
                field_name = canonical_map[clean_h]
                if field_name not in header_map:
                    header_map[field_name] = idx

        required_fields = ["sku", "name", "category", "price", "stock"]
        missing_fields = [f for f in required_fields if f not in header_map]
        if missing_fields:
            missing_labels = {
                "sku": "SKU",
                "name": "Nama Produk",
                "category": "Kategori",
                "price": "Harga",
                "stock": "Stok",
            }
            missing_names = ", ".join(missing_labels.get(f, f) for f in missing_fields)
            return Response(
                {
                    "success": False,
                    "message": f"Kolom wajib tidak ditemukan dalam file CSV: {missing_names}.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        existing_categories = {
            cat.name.strip().lower(): cat
            for cat in Category.objects.filter(
                seller=request.user,
                deleted_at__isnull=True,
            )
        }

        existing_skus = set(
            Product.objects.filter(
                seller=request.user,
                deleted_at__isnull=True,
            ).values_list("sku", flat=True)
        )

        file_seen_skus = {}
        errors = []
        valid_items = []
        data_rows = rows[1:]

        def get_val(row_cells, field):
            idx = header_map.get(field)
            if idx is not None and idx < len(row_cells):
                return row_cells[idx].strip()
            return ""

        for row_idx, row in enumerate(data_rows, start=2):
            if not row or not any(cell.strip() for cell in row):
                continue

            status_raw = get_val(row, "status").lower()
            if status_raw in ["aktif", "active"]:
                normalized_status = "active"
            elif status_raw in ["tidak aktif", "nonaktif", "inactive"]:
                normalized_status = "inactive"
            else:
                normalized_status = status_raw or "active"

            raw_data = {
                "name": get_val(row, "name"),
                "sku": get_val(row, "sku"),
                "category": get_val(row, "category"),
                "price": get_val(row, "price"),
                "stock": get_val(row, "stock"),
                "status": normalized_status,
                "description": get_val(row, "description"),
            }

            serializer = ProductCSVRowSerializer(data=raw_data)
            if not serializer.is_valid():
                for field, err_list in serializer.errors.items():
                    errors.append({
                        "row": row_idx,
                        "sku": raw_data.get("sku") or "-",
                        "field": field,
                        "message": err_list[0] if isinstance(err_list, list) else str(err_list),
                    })
                continue

            cleaned = serializer.validated_data
            sku = cleaned["sku"]
            category_name = cleaned["category"]

            if sku in file_seen_skus:
                errors.append({
                    "row": row_idx,
                    "sku": sku,
                    "field": "sku",
                    "message": f"SKU '{sku}' duplikat di dalam file CSV (sama dengan baris {file_seen_skus[sku]}).",
                })
                continue
            file_seen_skus[sku] = row_idx

            if sku in existing_skus:
                errors.append({
                    "row": row_idx,
                    "sku": sku,
                    "field": "sku",
                    "message": f"SKU '{sku}' sudah digunakan oleh produk lain di toko Anda.",
                })
                continue

            cat_obj = existing_categories.get(category_name.strip().lower())
            if not cat_obj:
                errors.append({
                    "row": row_idx,
                    "sku": sku,
                    "field": "category",
                    "message": f"Kategori '{category_name}' tidak ditemukan. Pastikan kategori sudah terdaftar di menu Kategori.",
                })
                continue

            valid_items.append({
                "name": cleaned["name"],
                "sku": sku,
                "category": cat_obj,
                "price": cleaned["price"],
                "stock": cleaned["stock"],
                "status": cleaned.get("status", "active"),
                "description": cleaned.get("description", ""),
            })

        if errors:
            return Response(
                {
                    "success": False,
                    "message": f"Terdapat {len(errors)} kesalahan validasi pada file CSV. Mohon perbaiki data berikut.",
                    "total_rows": len(valid_items) + len(errors),
                    "errors": errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not valid_items:
            return Response(
                {
                    "success": False,
                    "message": "Tidak ada baris data produk yang dapat diimpor pada file CSV.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            products_to_create = [
                Product(
                    seller=request.user,
                    category=item["category"],
                    name=item["name"],
                    sku=item["sku"],
                    description=item["description"],
                    price=item["price"],
                    stock=item["stock"],
                    status=item["status"],
                    created_by=request.user,
                    updated_by=request.user,
                )
                for item in valid_items
            ]
            Product.objects.bulk_create(products_to_create)

        return Response(
            {
                "success": True,
                "message": f"Berhasil mengimpor {len(products_to_create)} produk ke toko Anda.",
                "total_rows": len(products_to_create),
                "imported_count": len(products_to_create),
            },
            status=status.HTTP_201_CREATED,
        )

