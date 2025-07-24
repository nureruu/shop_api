from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.generics import CreateAPIView
from rest_framework_simplejwt.views import TokenObtainPairView
from users.serializers import CustomTokenObtainSerializer
from django.core.cache import cache

from .serializers import (
    RegisterValidateSerializer,
    AuthValidateSerializer,
    ConfirmationSerializer
)
import random
import string
from users.models import CustomUser

class AuthorizationAPIView(CreateAPIView):
    serializer_class = AuthValidateSerializer
    def post(self, request):
        serializer = AuthValidateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(**serializer.validated_data)

        if user:
            if not user.is_active:
                return Response(
                    status=status.HTTP_401_UNAUTHORIZED,
                    data={'error': 'User account is not activated yet!'}
                )

            token, _ = Token.objects.get_or_create(user=user)
            return Response(data={'key': token.key})

        return Response(
            status=status.HTTP_401_UNAUTHORIZED,
            data={'error': 'User credentials are wrong!'}
        )


class RegistrationAPIView(CreateAPIView):
    serializer_class = RegisterValidateSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        with transaction.atomic():
            user = CustomUser.objects.create_user(
                email=email,
                password=password,
                is_active=False
            )

            # Генерируем 6-значный код
            code = ''.join(random.choices(string.digits, k=6))

            # Ключ Redis: confirm:<user_id>
            key = f'confirm:{user.id}'

            # Удаляем старый, если есть
            cache.delete(key)

            # Сохраняем новый код на 5 минут
            cache.set(key, code, timeout=300)  # 5 минут = 300 сек

        return Response(
            status=status.HTTP_201_CREATED,
            data={
                'user_id': user.id,
                'confirmation_code': code  # ⚠️ Только для отладки. В реальности надо отправлять email.
            }
        )



class ConfirmUserAPIView(CreateAPIView):
    serializer_class = ConfirmationSerializer

    def post(self, request):
        serializer = ConfirmationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = serializer.validated_data['user_id']
        user = CustomUser.objects.get(id=user_id)

        with transaction.atomic():
            user.is_active = True
            user.save()

            # Удаляем использованный код из Redis
            cache.delete(f'confirm:{user.id}')

            # Создаём токен
            token, _ = Token.objects.get_or_create(user=user)

        return Response(
            status=status.HTTP_200_OK,
            data={
                'message': 'User аккаунт успешно активирован',
                'key': token.key
            }
        )

    

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainSerializer