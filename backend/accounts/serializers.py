from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import EmailValidator
from rest_framework import serializers


def validate_unique_email(value, instance=None):
    users = User.objects.filter(email__iexact=value)
    if instance:
        users = users.exclude(pk=instance.pk)
    if users.exists():
        raise serializers.ValidationError('Email sudah digunakan.')
    return value


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

    def validate_email(self, value):
        return validate_unique_email(value)

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


class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True, allow_blank=False)
    username = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email')
        read_only_fields = ('id',)

    def validate_username(self, value):
        users = User.objects.filter(username=value)
        if self.instance:
            users = users.exclude(pk=self.instance.pk)
        if users.exists():
            raise serializers.ValidationError('Username sudah digunakan.')
        return value

    def validate_email(self, value):
        return validate_unique_email(value, self.instance)


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_current_password(self, value):
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError('Password saat ini tidak sesuai.')
        return value

    def validate_new_password(self, value):
        if self.context['request'].user.check_password(value):
            raise serializers.ValidationError(
                'Password baru harus berbeda dari password saat ini.'
            )
        try:
            validate_password(value, user=self.context['request'].user)
        except DjangoValidationError as error:
            raise serializers.ValidationError(error.messages) from error
        return value
