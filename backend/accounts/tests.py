from django.core.cache import caches
from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

User = get_user_model()


@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'accounts-auth-tests',
        },
    },
)
class AuthenticationTests(APITestCase):
    def setUp(self):
        caches['default'].clear()
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
        self.assertNotIn("password", response.data["data"])

        login_response = self.client.post(self.login_url, {
            "username": self.user_data["username"],
            "password": self.user_data["password"],
        })
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

    def test_register_rejects_weak_password(self):
        user_data = {
            **self.user_data,
            "password": "short",
        }

        response = self.client.post(self.register_url, user_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)
        self.assertFalse(User.objects.filter(username=user_data["username"]).exists())

    def test_register_rejects_common_password(self):
        user_data = {
            **self.user_data,
            "password": "password",
        }

        response = self.client.post(self.register_url, user_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)
        self.assertFalse(User.objects.filter(username=user_data["username"]).exists())

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
        self.assertFalse(Token.objects.filter(pk=token.pk).exists())

        # token yang sudah dihapus/revoke tidak boleh digunakan kembali
        response_me = self.client.get(self.me_url)
        self.assertEqual(response_me.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_without_token_rejected(self):
        response = self.client.post(self.logout_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_again_after_logout_creates_usable_token(self):
        User.objects.create_user(**self.user_data)
        credentials = {
            "username": self.user_data["username"],
            "password": self.user_data["password"],
        }

        first_login = self.client.post(self.login_url, credentials)
        self.assertEqual(first_login.status_code, status.HTTP_200_OK)
        first_token = first_login.data["data"]["token"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {first_token}")
        logout_response = self.client.post(self.logout_url)
        self.assertEqual(logout_response.status_code, status.HTTP_200_OK)

        self.client.credentials()
        second_login = self.client.post(self.login_url, credentials)
        self.assertEqual(second_login.status_code, status.HTTP_200_OK)
        second_token = second_login.data["data"]["token"]
        self.assertNotEqual(second_token, first_token)

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {second_token}")
        me_response = self.client.get(self.me_url)
        self.assertEqual(me_response.status_code, status.HTTP_200_OK)


@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'accounts-throttle-tests',
        },
    },
)
class AuthenticationThrottleTests(APITestCase):
    def setUp(self):
        caches['default'].clear()
        self.login_url = reverse('login')
        self.register_url = reverse('register')
        self.user = User.objects.create_user(
            username='throttle-user',
            email='throttle-user@example.com',
            password='Throttle-Test-Password-123!',
        )

    def test_login_within_rate_allows_valid_and_invalid_attempts(self):
        valid_response = self.client.post(
            self.login_url,
            {
                'username': self.user.username,
                'password': 'Throttle-Test-Password-123!',
            },
        )
        invalid_responses = [
            self.client.post(
                self.login_url,
                {'username': self.user.username, 'password': 'wrong'},
            )
            for _ in range(4)
        ]

        self.assertEqual(valid_response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            all(
                response.status_code == status.HTTP_400_BAD_REQUEST
                for response in invalid_responses
            )
        )

    def test_login_exceeding_rate_returns_429(self):
        for _ in range(5):
            response = self.client.post(
                self.login_url,
                {'username': self.user.username, 'password': 'wrong'},
            )
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        throttled_response = self.client.post(
            self.login_url,
            {'username': self.user.username, 'password': 'wrong'},
        )

        self.assertEqual(
            throttled_response.status_code,
            status.HTTP_429_TOO_MANY_REQUESTS,
        )

    def test_register_within_rate_allows_valid_requests(self):
        for index in range(5):
            response = self.client.post(
                self.register_url,
                {
                    'username': f'register-user-{index}',
                    'email': f'register-user-{index}@example.com',
                    'password': 'Register-Test-Password-123!',
                },
            )
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_register_exceeding_rate_returns_429(self):
        for index in range(5):
            response = self.client.post(
                self.register_url,
                {
                    'username': f'register-user-{index}',
                    'email': f'register-user-{index}@example.com',
                    'password': 'Register-Test-Password-123!',
                },
            )
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        throttled_response = self.client.post(
            self.register_url,
            {
                'username': 'register-user-over-limit',
                'email': 'register-user-over-limit@example.com',
                'password': 'Register-Test-Password-123!',
            },
        )

        self.assertEqual(
            throttled_response.status_code,
            status.HTTP_429_TOO_MANY_REQUESTS,
        )

    def test_auth_throttles_do_not_apply_to_product_category_or_dashboard(self):
        for _ in range(3):
            self.client.post(
                self.login_url,
                {'username': self.user.username, 'password': 'wrong'},
            )

        for endpoint_name in ('product-list', 'category-list', 'dashboard'):
            with self.subTest(endpoint=endpoint_name):
                response = self.client.get(reverse(endpoint_name))
                self.assertEqual(
                    response.status_code,
                    status.HTTP_401_UNAUTHORIZED,
                )
