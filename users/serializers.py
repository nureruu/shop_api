from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import ConfirmationCode
from django.contrib.auth.models import User
from users.models import CustomUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from datetime import date
from django.core.cache import cache
User = get_user_model()

class User_Base_Serializers(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField()
    password = serializers.CharField()

class AuthValidateSerializer(serializers.Serializer):
    pass
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'password']

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        user.is_active = False
        user.save()
        return user
class ConfirmCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        code = attrs.get('code')

        from django.core.cache import cache
        real_code = cache.get(f"confirm_code:{email}")

        if real_code is None:
            raise serializers.ValidationError("Код истёк или не найден.")
        if real_code != code:
            raise serializers.ValidationError("Неверный код.")

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("Пользователь не найден.")

        attrs["user"] = user 
        return attrs
    def save(self, **kwargs):
        user = self.validated_data["user"]
        user.is_active = True
        user.save()
        cache.delete(f"confirm_code:{user.email}")
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user

        if user.birth_date is None:
            raise serializers.ValidationError("Пожалуйста, укажите дату рождения в профиле.")

        today = date.today()
        age = today.year - user.birth_date.year - (
            (today.month, today.day) < (user.birth_date.month, user.birth_date.day)
        )

        if age < 18:
            raise serializers.ValidationError("Вам должно быть не менее 18 лет для входа.")
        data['birth_date'] = str(user.birth_date)

        return data