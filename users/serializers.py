from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.core.cache import cache
from users.models import CustomUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from djoser.serializers import UserSerializer as BaseUserSerializer
from django.contrib.auth import authenticate
class UserBaseSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=150)
    password = serializers.CharField()


class AuthValidateSerializer(UserBaseSerializer):
    pass


class RegisterValidateSerializer(UserBaseSerializer):
    def validate_email(self, email):
        try:
            CustomUser.objects.get(email=email)
        except:
            return email
        raise ValidationError('Email уже существует!')


class ConfirmationSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    code = serializers.CharField(max_length=6)

    def validate(self, attrs):
        user_id = attrs.get('user_id')
        code = attrs.get('code')

        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            raise ValidationError('Пользователь не существует.')

        redis_key = f"confirm:{user_id}"
        saved_code = cache.get(redis_key)

        if not saved_code:
            raise ValidationError('Код истёк или не найден.')

        if saved_code != code:
            raise ValidationError('Неверный код подтверждения.')

        return attrs
    

class CustomTokenObtainSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['birthday'] = str(user.birthday) if user.birthday else None
        return token
    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(request=self.context.get("request"), email=email, password=password)

        if not user:
            raise ValidationError("Неверный email или пароль")

        if not user.is_active:
            raise ValidationError("Аккаунт не активирован")

        data = super().validate(attrs)
        return data
class GoogleLoginSerializer(serializers.Serializer):
    code = serializers.CharField(required=True)

class CustomUserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        model = CustomUser
        fields = ('email', 'password', 'phone')
        extra_kwargs = {'password': {'write_only': True}}

class CustomUserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        model = CustomUser
        fields = ('email', 'phone')