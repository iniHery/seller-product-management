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
