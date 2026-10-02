from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

User = get_user_model()

class AuthenticationTests(APITestCase):
    def setUp(self):
        self.register_url = reverse("register")
        self.login_url = reverse("login")
        self.me_url = reverse("me")
        self.logout_url = reverse("logout")

        self.user_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "testpassword123",
        }

    def test_register_success(self):
        """register dengan data valid harus berhasil."""
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(username=self.user_data["username"])

        # username harus tersimpan
        self.assertEqual(user.username, self.user_data["username"])

        # email harus tersimpan
        self.assertEqual(user.email, self.user_data["email"])

        # password harus tersimpan dalam bentuk hashed password, bukan plaintext
        self.assertNotEqual(user.password, self.user_data["password"])
        self.assertTrue(user.check_password(self.user_data["password"]))

    def test_login_success(self):
        """login dengan credential yang benar harus berhasil."""
        # Create user first
        User.objects.create_user(**self.user_data)

        response = self.client.post(self.login_url, {
            "username": self.user_data["username"],
            "password": self.user_data["password"],
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # response harus mengembalikan token
        self.assertIn("token", response.data["data"])
        self.assertTrue(len(response.data["data"]["token"]) > 0)

    def test_login_failure_wrong_password(self):
        """login dengan password salah harus ditolak."""
        User.objects.create_user(**self.user_data)

        response = self.client.post(self.login_url, {
            "username": self.user_data["username"],
            "password": "wrongpassword",
        })

        self.assertNotEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn("token", response.data.get("data", {}))

    def test_current_user_success(self):
        """GET /api/auth/me/ dengan token harus berhasil."""
        user = User.objects.create_user(**self.user_data)
        token, _ = Token.objects.get_or_create(user=user)

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        response = self.client.get(self.me_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # data user yang dikembalikan harus sesuai dengan user yang login
        self.assertEqual(response.data["data"]["username"], user.username)
        self.assertEqual(response.data["data"]["email"], user.email)

    def test_current_user_no_token_rejected(self):
        """request tanpa token harus ditolak."""
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_success(self):
        """logout dengan token harus berhasil."""
        user = User.objects.create_user(**self.user_data)
        token, _ = Token.objects.get_or_create(user=user)

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        response = self.client.post(self.logout_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # token yang sudah dihapus/revoke tidak boleh digunakan kembali
        response_me = self.client.get(self.me_url)
        self.assertEqual(response_me.status_code, status.HTTP_401_UNAUTHORIZED)
