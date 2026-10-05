from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import EmailValidator
from rest_framework import serializers


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True, validators=[EmailValidator()])
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
    )

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True},
        }

    def validate(self, attrs):
        prospective_user = User(
            username=attrs.get('username', ''),
            email=attrs.get('email', ''),
        )

        try:
            validate_password(attrs['password'], user=prospective_user)
        except DjangoValidationError as error:
            raise serializers.ValidationError({'password': error.messages}) from error

        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login credentials."""

    username = serializers.CharField(required=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
    )

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError('Invalid username or password')
        attrs['user'] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')
