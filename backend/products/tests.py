from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Category, Product


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
        self.category = Category.objects.create(name="Test category")
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
        self.category = Category.objects.create(name="Electronics")
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
        self.assertEqual(Product.objects.count(), 0)


class ProductValidationTests(APITestCase):
    def setUp(self):
        self.seller = User.objects.create_user(
            username="seller", password="password"
        )
        self.category = Category.objects.create(name="Home")
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
        self.category_a = Category.objects.create(name="Category A")
        self.category_b = Category.objects.create(name="Category B")
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

    def test_get_categories(self):
        Category.objects.create(name="Cat 1")
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 1)

    def test_update_category(self):
        cat = Category.objects.create(name="Cat 1")
        url = reverse("category-detail", kwargs={"id": cat.id})
        response = self.client.put(url, {"name": "Cat 2"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        cat.refresh_from_db()
        self.assertEqual(cat.name, "Cat 2")

    def test_delete_unused_category(self):
        cat = Category.objects.create(name="Unused")
        url = reverse("category-detail", kwargs={"id": cat.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Category.objects.count(), 0)

    def test_delete_used_category_fails(self):
        cat = Category.objects.create(name="Used")
        Product.objects.create(seller=self.seller, category=cat, name="Prod", sku="SKU1", price="1", stock=1)
        url = reverse("category-detail", kwargs={"id": cat.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertEqual(response.data["message"], "Category cannot be deleted because it is still used by products.")
        self.assertEqual(Category.objects.count(), 1)


class DashboardTests(APITestCase):
    def setUp(self):
        self.seller = User.objects.create_user(username="seller", password="password")
        self.other_seller = User.objects.create_user(username="other", password="password")
        self.category = Category.objects.create(name="Cat")
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
