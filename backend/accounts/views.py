from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import LoginSerializer, RegisterSerializer, UserSerializer


class LoginAPIView(APIView):
    """Endpoint for user login.

    POST /api/auth/login/
    Returns auth token and user data.
    """

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
        }
        return Response({
            'success': True,
            'data': {
                'token': token.key,
                'user': user_data,
            }
        }, status=status.HTTP_200_OK)


class RegisterAPIView(APIView):
    """Endpoint for user registration.

    POST /api/auth/register/
    Returns created user data (excluding password) with success flag.
    """

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_201_CREATED)


class LogoutAPIView(APIView):
    """Endpoint for user logout.

    POST /api/auth/logout/
    Requires authentication; deletes the user's token.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        token = request.auth
        if token:
            token.delete()
        return Response({"success": True, "data": None}, status=status.HTTP_200_OK)


class MeAPIView(APIView):
    """Endpoint for retrieving current authenticated user.

    GET /api/auth/me/
    Returns user id, username, email.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = UserSerializer(request.user)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)
