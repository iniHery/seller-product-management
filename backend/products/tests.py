from unittest.mock import Mock

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase

from .models import Category, Product
from .views import _save_with_seller_unique_value


User = get_user_model()


class ProductAuthorizationTests(APITestCase):
    def setUp(self):
        self.seller_a = User.objects.create_user(
            username="seller-a",
            password="test-password-a",
        )
        self.seller_b = User.objects.create_user(
            username="seller-b",
            password="test-password-b",
        )
        self.category = Category.objects.create(
            name="Test category",
            seller=self.seller_a,
            created_by=self.seller_a,
            updated_by=self.seller_a,
        )
        self.product_a = Product.objects.create(
            seller=self.seller_a,
            category=self.category,
            name="Seller A product",
            sku="SELLER-A-SKU",
            description="Owned by seller A",
            price="10.00",
            stock=5,
            status=Product.Status.ACTIVE,
        )
        self.product_b = Product.objects.create(
            seller=self.seller_b,
            category=self.category,
            name="Seller B product",
            sku="SELLER-B-SKU",
            description="Owned by seller B",
            price="20.00",
            stock=8,
            status=Product.Status.ACTIVE,
        )
        self.list_url = reverse("product-list")
        self.detail_url = reverse(
            "product-detail",
            kwargs={"id": self.product_b.id},
        )

    def test_unauthenticated_product_requests_are_rejected(self):
        self.client.force_authenticate(user=None)

        list_response = self.client.get(self.list_url)
        detail_response = self.client.get(self.detail_url)
        create_response = self.client.post(
            self.list_url,
            self.product_payload("Anonymous product", "ANONYMOUS-SKU"),
        )

        self.assertEqual(list_response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(detail_response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(create_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_seller_can_only_see_owned_products(self):
        self.client.force_authenticate(user=self.seller_a)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        product_ids = {
            product["id"] for product in response.data["data"]["results"]
        }
        self.assertEqual(product_ids, {str(self.product_a.id)})

    def test_seller_cannot_get_another_sellers_product(self):
        self.client.force_authenticate(user=self.seller_a)

        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_seller_cannot_put_another_sellers_product(self):
        self.client.force_authenticate(user=self.seller_a)

        response = self.client.put(
            self.detail_url,
            self.product_payload("Changed by seller A", "CHANGED-SELLER-A"),
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.product_b.refresh_from_db()
        self.assertEqual(self.product_b.name, "Seller B product")
        self.assertEqual(self.product_b.sku, "SELLER-B-SKU")

    def test_seller_cannot_patch_another_sellers_product(self):
        self.client.force_authenticate(user=self.seller_a)

        response = self.client.patch(
            self.detail_url,
            {"name": "Changed by seller A"},
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.product_b.refresh_from_db()
        self.assertEqual(self.product_b.name, "Seller B product")

    def test_seller_cannot_delete_another_sellers_product(self):
        self.client.force_authenticate(user=self.seller_a)

        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Product.objects.filter(pk=self.product_b.pk).exists())

    def test_created_product_uses_authenticated_seller(self):
        self.client.force_authenticate(user=self.seller_a)
        payload = self.product_payload("New seller A product", "NEW-SELLER-A")

        response = self.client.post(self.list_url, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_product = Product.objects.get(sku="NEW-SELLER-A")
        self.assertEqual(created_product.seller, self.seller_a)

    def product_payload(self, name, sku):
        return {
            "name": name,
            "sku": sku,
            "description": "Created for an authorization test",
            "price": "12.50",
            "stock": 3,
            "status": Product.Status.ACTIVE,
            "category_id": str(self.category.id),
        }


class ProductCRUDTests(APITestCase):
    def setUp(self):
        self.seller = User.objects.create_user(
            username="seller", password="password"
        )
        self.category = Category.objects.create(
            name="Electronics",
            seller=self.seller,
            created_by=self.seller,
            updated_by=self.seller,
        )
        self.client.force_authenticate(user=self.seller)
        self.list_url = reverse("product-list")

    def test_seller_can_create_product(self):
        """user yang login dapat membuat product."""
        payload = {
            "name": "New Smartphone",
            "sku": "SMART-001",
            "price": "499.99",
            "stock": 10,
            "status": Product.Status.ACTIVE,
            "category_id": str(self.category.id)
        }
        response = self.client.post(self.list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 1)
        product = Product.objects.first()
        self.assertEqual(product.seller, self.seller)
        # seller tidak dapat dikirim atau dipaksakan menjadi seller lain
        other_seller = User.objects.create_user(username="other", password="pwd")
        payload["seller"] = other_seller.id
        response2 = self.client.post(self.list_url, payload)
        # Should ignore the seller in payload and use request.user
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST) # Because SKU must be unique

        payload["sku"] = "SMART-002"
        response3 = self.client.post(self.list_url, payload)
        self.assertEqual(response3.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.get(sku="SMART-002").seller, self.seller)

    def test_seller_can_get_own_product_detail(self):
        """user dapat melihat product miliknya."""
        product = Product.objects.create(
            seller=self.seller, category=self.category, name="My Product",
            sku="MY-SKU", price="10", stock=5
        )
        url = reverse("product-detail", kwargs={"id": product.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["name"], "My Product")

    def test_seller_can_update_own_product(self):
        """user dapat mengubah product miliknya."""
        product = Product.objects.create(
            seller=self.seller, category=self.category, name="My Product",
            sku="MY-SKU", price="10", stock=5
        )
        url = reverse("product-detail", kwargs={"id": product.id})
        response = self.client.patch(url, {"name": "Updated Name"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        product.refresh_from_db()
        self.assertEqual(product.name, "Updated Name")

    def test_seller_can_delete_own_product(self):
        """user dapat menghapus product miliknya."""
        product = Product.objects.create(
            seller=self.seller, category=self.category, name="My Product",
            sku="MY-SKU", price="10", stock=5
        )
        url = reverse("product-detail", kwargs={"id": product.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        product.refresh_from_db()
        self.assertIsNotNone(product.deleted_at)
        self.assertEqual(Product.objects.filter(deleted_at__isnull=True).count(), 0)


class ProductValidationTests(APITestCase):
    def setUp(self):
        self.seller = User.objects.create_user(
            username="seller", password="password"
        )
        self.category = Category.objects.create(
            name="Home",
            seller=self.seller,
            created_by=self.seller,
            updated_by=self.seller,
        )
        self.client.force_authenticate(user=self.seller)
        self.list_url = reverse("product-list")
        self.valid_payload = {
            "name": "Sofa",
            "sku": "SOFA-123",
            "price": "100.00",
            "stock": 5,
            "category_id": str(self.category.id)
        }

    def test_name_required(self):
        payload = self.valid_payload.copy()
        payload.pop("name")
        response = self.client.post(self.list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)

    def test_sku_required(self):
        payload = self.valid_payload.copy()
        payload.pop("sku")
        response = self.client.post(self.list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("sku", response.data)

    def test_sku_unique(self):
        Product.objects.create(
            seller=self.seller, category=self.category,
            name="Existing", sku="SOFA-123", price="10", stock=1
        )
        response = self.client.post(self.list_url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("sku", response.data)

    def test_price_not_negative(self):
        payload = self.valid_payload.copy()
        payload["price"] = "-10.00"
        response = self.client.post(self.list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("price", response.data)

    def test_stock_not_negative(self):
        payload = self.valid_payload.copy()
        payload["stock"] = -5
        response = self.client.post(self.list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("stock", response.data)

    def test_category_valid(self):
        payload = self.valid_payload.copy()
        import uuid
        payload["category_id"] = str(uuid.uuid4())
        response = self.client.post(self.list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ProductSearchFilterPaginationTests(APITestCase):
    def setUp(self):
        self.seller = User.objects.create_user(username="seller", password="password")
        self.other_seller = User.objects.create_user(username="other", password="password")
        self.category_a = Category.objects.create(
            name="Category A",
            seller=self.seller,
            created_by=self.seller,
            updated_by=self.seller,
        )
        self.category_b = Category.objects.create(
            name="Category B",
            seller=self.seller,
            created_by=self.seller,
            updated_by=self.seller,
        )
        self.client.force_authenticate(user=self.seller)
        self.list_url = reverse("product-list")

        Product.objects.create(seller=self.seller, category=self.category_a, name="Apple", sku="APP-1", price="1", stock=1, status="active")
        Product.objects.create(seller=self.seller, category=self.category_a, name="Banana", sku="BAN-1", price="1", stock=1, status="inactive")
        Product.objects.create(seller=self.seller, category=self.category_b, name="Pineapple", sku="PIN-1", price="1", stock=1, status="active")

        Product.objects.create(seller=self.other_seller, category=self.category_a, name="Apple Other", sku="APP-2", price="1", stock=1, status="active")

    def test_search_by_name(self):
        response = self.client.get(self.list_url, {"search": "apple"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["data"]["results"]
        self.assertEqual(len(results), 2)  # Apple and Pineapple
        names = [r["name"] for r in results]
        self.assertIn("Apple", names)
        self.assertIn("Pineapple", names)

    def test_search_by_sku(self):
        response = self.client.get(self.list_url, {"search": "BAN-1"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["data"]["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Banana")

    def test_search_respects_ownership(self):
        response = self.client.get(self.list_url, {"search": "Apple"})
        results = response.data["data"]["results"]
        # Should not include "Apple Other"
        self.assertFalse(any(r["name"] == "Apple Other" for r in results))

    def test_filter_by_category(self):
        response = self.client.get(self.list_url, {"category": "Category A"})
        results = response.data["data"]["results"]
        self.assertEqual(len(results), 2)
        names = [r["name"] for r in results]
        self.assertIn("Apple", names)
        self.assertIn("Banana", names)

    def test_filter_by_status(self):
        response = self.client.get(self.list_url, {"status": "inactive"})
        results = response.data["data"]["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Banana")

    def test_pagination(self):
        # Create more products to test pagination (assuming page size is 10 or 20)
        # Let's force page size parameter or just test the response structure
        response = self.client.get(self.list_url)
        self.assertIn("count", response.data["data"])
        self.assertIn("next", response.data["data"])
        self.assertIn("previous", response.data["data"])
        self.assertEqual(response.data["data"]["count"], 3)


class CategoryCRUDTests(APITestCase):
    def setUp(self):
        self.seller = User.objects.create_user(username="seller", password="password")
        self.client.force_authenticate(user=self.seller)
        self.list_url = reverse("category-list")

    def test_category_requires_authentication(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_category(self):
        response = self.client.post(self.list_url, {"name": "New Cat"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 1)
        self.assertEqual(Category.objects.first().name, "New Cat")
        self.assertEqual(Category.objects.first().seller, self.seller)

    def test_duplicate_category_name_is_rejected_for_same_seller(self):
        Category.objects.create(name="Existing", seller=self.seller)

        response = self.client.post(self.list_url, {"name": "Existing"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(Category.objects.filter(seller=self.seller).count(), 1)

    def test_category_name_can_be_reused_after_soft_delete(self):
        category = Category.objects.create(name="Reusable", seller=self.seller)
        category.soft_delete(self.seller)

        response = self.client.post(self.list_url, {"name": "Reusable"})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_categories(self):
        Category.objects.create(
            name="Cat 1",
            seller=self.seller,
            created_by=self.seller,
            updated_by=self.seller,
        )
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 1)

    def test_update_category(self):
        cat = Category.objects.create(
            name="Cat 1",
            seller=self.seller,
            created_by=self.seller,
            updated_by=self.seller,
        )
        url = reverse("category-detail", kwargs={"id": cat.id})
        response = self.client.put(url, {"name": "Cat 2"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        cat.refresh_from_db()
        self.assertEqual(cat.name, "Cat 2")

    def test_delete_unused_category(self):
        cat = Category.objects.create(
            name="Unused",
            seller=self.seller,
            created_by=self.seller,
            updated_by=self.seller,
        )
        url = reverse("category-detail", kwargs={"id": cat.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        cat.refresh_from_db()
        self.assertIsNotNone(cat.deleted_at)
        self.assertEqual(cat.deleted_by, self.seller)
        self.assertEqual(cat.updated_by, self.seller)
        self.assertGreaterEqual(cat.updated_at, cat.deleted_at)
        self.assertEqual(Category.objects.filter(deleted_at__isnull=True).count(), 0)

    def test_delete_used_category_fails(self):
        cat = Category.objects.create(
            name="Used",
            seller=self.seller,
            created_by=self.seller,
            updated_by=self.seller,
        )
        Product.objects.create(seller=self.seller, category=cat, name="Prod", sku="SKU1", price="1", stock=1)
        url = reverse("category-detail", kwargs={"id": cat.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertEqual(
            response.data["message"],
            "Kategori tidak dapat dihapus karena masih digunakan produk aktif.",
        )
        self.assertEqual(Category.objects.count(), 1)


class ProductDataIntegrityTests(APITestCase):
    def setUp(self):
        self.seller_a = User.objects.create_user(
            username="seller-a", password="password"
        )
        self.seller_b = User.objects.create_user(
            username="seller-b", password="password"
        )
        self.category_a = Category.objects.create(
            name="Category A",
            seller=self.seller_a,
            created_by=self.seller_a,
            updated_by=self.seller_a,
        )
        self.category_b = Category.objects.create(
            name="Category B",
            seller=self.seller_b,
            created_by=self.seller_b,
            updated_by=self.seller_b,
        )
        self.products_url = reverse("product-list")
        self.categories_url = reverse("category-list")

    def product_payload(self, category_id, sku="SHARED-SKU"):
        return {
            "name": "Product",
            "sku": sku,
            "price": "10000",
            "stock": 1,
            "category_id": str(category_id),
        }

    def test_save_maps_concurrent_seller_unique_conflicts_to_validation_errors(self):
        category = Category.objects.create(
            name="Existing category",
            seller=self.seller_a,
        )
        product = Product.objects.create(
            seller=self.seller_a,
            category=self.category_a,
            name="Existing product",
            sku="EXISTING-SKU",
            price="10.00",
            stock=1,
        )

        cases = (
            (
                Category,
                "name",
                category.name,
                "Nama kategori sudah digunakan pada toko Anda.",
            ),
            (
                Product,
                "sku",
                product.sku,
                "SKU sudah digunakan pada toko Anda.",
            ),
        )
        for model, field, value, message in cases:
            with self.subTest(model=model.__name__):
                serializer = Mock()
                serializer.validated_data = {field: value}
                serializer.instance = None
                serializer.save.side_effect = IntegrityError("unique conflict")

                with self.assertRaises(ValidationError) as error:
                    _save_with_seller_unique_value(
                        serializer,
                        model,
                        self.seller_a,
                        field,
                        message,
                    )

                self.assertEqual(error.exception.detail[field][0], message)

    def test_save_reraises_unrelated_integrity_errors(self):
        serializer = Mock()
        serializer.validated_data = {"sku": "UNIQUE-SKU"}
        serializer.instance = None
        serializer.save.side_effect = IntegrityError("unrelated integrity error")

        with self.assertRaises(IntegrityError):
            _save_with_seller_unique_value(
                serializer,
                Product,
                self.seller_a,
                "sku",
                "SKU sudah digunakan pada toko Anda.",
            )

    def test_product_audit_fields_are_set_from_authenticated_seller(self):
        self.client.force_authenticate(user=self.seller_a)

        response = self.client.post(
            self.products_url,
            self.product_payload(self.category_a.id),
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        product = Product.objects.get(pk=response.data["data"]["id"])
        self.assertEqual(product.created_by, self.seller_a)
        self.assertEqual(product.updated_by, self.seller_a)

    def test_seller_cannot_use_another_sellers_category(self):
        self.client.force_authenticate(user=self.seller_a)

        response = self.client.post(
            self.products_url,
            self.product_payload(self.category_b.id),
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("category_id", response.data)

    def test_same_sku_is_allowed_for_different_sellers(self):
        self.client.force_authenticate(user=self.seller_a)
        first_response = self.client.post(
            self.products_url,
            self.product_payload(self.category_a.id),
        )
        self.client.force_authenticate(user=self.seller_b)
        second_response = self.client.post(
            self.products_url,
            self.product_payload(self.category_b.id),
        )

        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second_response.status_code, status.HTTP_201_CREATED)

    def test_duplicate_sku_is_rejected_for_same_seller(self):
        self.client.force_authenticate(user=self.seller_a)
        self.client.post(
            self.products_url,
            self.product_payload(self.category_a.id),
        )

        response = self.client.post(
            self.products_url,
            self.product_payload(self.category_a.id),
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("sku", response.data)

    def test_deleted_product_sku_can_be_reused(self):
        product = Product.objects.create(
            seller=self.seller_a,
            category=self.category_a,
            name="Deleted",
            sku="REUSABLE-SKU",
            price="10000",
            stock=1,
        )
        product.soft_delete(self.seller_a)
        self.client.force_authenticate(user=self.seller_a)

        response = self.client.post(
            self.products_url,
            self.product_payload(self.category_a.id, sku="REUSABLE-SKU"),
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_deleted_product_is_hidden_and_kept_for_audit(self):
        product = Product.objects.create(
            seller=self.seller_a,
            category=self.category_a,
            name="To delete",
            sku="DELETE-SKU",
            price="10000",
            stock=1,
            created_by=self.seller_a,
            updated_by=self.seller_a,
        )
        self.client.force_authenticate(user=self.seller_a)

        response = self.client.delete(
            reverse("product-detail", kwargs={"id": product.id})
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        product.refresh_from_db()
        self.assertIsNotNone(product.deleted_at)
        self.assertEqual(product.deleted_by, self.seller_a)
        self.assertEqual(product.updated_by, self.seller_a)
        self.assertGreaterEqual(product.updated_at, product.deleted_at)
        self.assertFalse(
            Product.objects.filter(
                seller=self.seller_a,
                deleted_at__isnull=True,
            ).exists()
        )

    def test_categories_are_scoped_to_the_authenticated_seller(self):
        self.client.force_authenticate(user=self.seller_a)

        response = self.client.get(self.categories_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [category["id"] for category in response.data["data"]],
            [str(self.category_a.id)],
        )


class DashboardTests(APITestCase):
    def setUp(self):
        self.seller = User.objects.create_user(username="seller", password="password")
        self.other_seller = User.objects.create_user(username="other", password="password")
        self.category = Category.objects.create(
            name="Cat",
            seller=self.seller,
            created_by=self.seller,
            updated_by=self.seller,
        )
        self.dashboard_url = reverse("dashboard")

        Product.objects.create(seller=self.seller, category=self.category, name="P1", sku="SKU1", price="10", stock=5, status="active")
        Product.objects.create(seller=self.seller, category=self.category, name="P2", sku="SKU2", price="20", stock=10, status="inactive")

        Product.objects.create(seller=self.other_seller, category=self.category, name="P3", sku="SKU3", price="10", stock=100, status="active")

    def test_dashboard_requires_authentication(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_dashboard_stats(self):
        self.client.force_authenticate(user=self.seller)
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data["data"]
        self.assertEqual(data["total_products"], 2)
        self.assertEqual(data["active_products"], 1)
        self.assertEqual(data["inactive_products"], 1)
        self.assertEqual(data["total_stock"], 15)
        self.assertEqual(data["low_stock_products"], 1)
        self.assertEqual(data["out_of_stock_products"], 0)
        self.assertEqual(data["total_valuation"], 50.0)
        self.assertEqual(len(data["category_distribution"]), 1)
        self.assertEqual(data["category_distribution"][0]["category_name"], "Cat")
        self.assertEqual(len(data["critical_products"]), 1)
        self.assertEqual(data["critical_products"][0]["sku"], "SKU1")


class ProductStockFilterTests(APITestCase):
    def setUp(self):
        self.seller = User.objects.create_user(username="seller-stock", password="password")
        self.category = Category.objects.create(
            name="Stock Category",
            seller=self.seller,
            created_by=self.seller,
            updated_by=self.seller,
        )
        self.list_url = reverse("product-list")

        self.p_out = Product.objects.create(
            seller=self.seller,
            category=self.category,
            name="Out of stock item",
            sku="OUT-1",
            price="10.00",
            stock=0,
            status=Product.Status.ACTIVE,
        )
        self.p_low = Product.objects.create(
            seller=self.seller,
            category=self.category,
            name="Low stock item",
            sku="LOW-1",
            price="20.00",
            stock=3,
            status=Product.Status.ACTIVE,
        )
        self.p_safe = Product.objects.create(
            seller=self.seller,
            category=self.category,
            name="Safe stock item",
            sku="SAFE-1",
            price="30.00",
            stock=12,
            status=Product.Status.ACTIVE,
        )

    def test_filter_stock_status_low(self):
        self.client.force_authenticate(user=self.seller)
        response = self.client.get(f"{self.list_url}?stock_status=low")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        skus = [p["sku"] for p in response.data["data"]["results"]]
        self.assertIn("LOW-1", skus)
        self.assertNotIn("OUT-1", skus)
        self.assertNotIn("SAFE-1", skus)

    def test_filter_stock_status_out(self):
        self.client.force_authenticate(user=self.seller)
        response = self.client.get(f"{self.list_url}?stock_status=out")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        skus = [p["sku"] for p in response.data["data"]["results"]]
        self.assertIn("OUT-1", skus)
        self.assertNotIn("LOW-1", skus)
        self.assertNotIn("SAFE-1", skus)

    def test_filter_stock_status_critical(self):
        self.client.force_authenticate(user=self.seller)
        response = self.client.get(f"{self.list_url}?stock_status=critical")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        skus = [p["sku"] for p in response.data["data"]["results"]]
        self.assertIn("OUT-1", skus)
        self.assertIn("LOW-1", skus)
        self.assertNotIn("SAFE-1", skus)

    def test_filter_stock_status_in_stock(self):
        self.client.force_authenticate(user=self.seller)
        response = self.client.get(f"{self.list_url}?stock_status=in_stock")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        skus = [p["sku"] for p in response.data["data"]["results"]]
        self.assertIn("SAFE-1", skus)
        self.assertNotIn("OUT-1", skus)
        self.assertNotIn("LOW-1", skus)

