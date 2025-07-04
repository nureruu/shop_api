from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import RegisterSerializer, ConfirmCodeSerializer, CustomTokenObtainPairSerializer
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView 
from rest_framework_simplejwt.views import TokenObtainPairView
from django.core.cache import cache
from drf_yasg.utils import swagger_auto_schema
import random
User = get_user_model()

def generate_and_store_code(email):
    code = str(random.randint(100000, 999999))
    cache.set(f"confirm_code:{email}", code, timeout=300)
    return code

def check_code(email, input_code):
    real_code = cache.get(f"confirm_code:{email}")
    return real_code == input_code

class RegisterView(APIView):
    @swagger_auto_schema(request_body=RegisterSerializer)
    def post(self, request):
        email = request.data.get("email")

        if not email:
            return Response({"error": "Email is required"}, status=400)

        user, created = User.objects.get_or_create(email=email)
        user.is_active = False
        user.save()

        code = generate_and_store_code(email)
        print(f"Код подтверждения для {email}: {code}")
        from users.tasks import send_otp_email
        send_otp_email.delay(email, code)
        return Response({"message": "Code sent to email"})
class ConfirmView(APIView):
    def post(self, request):
        email = request.data.get("email")
        code = request.data.get("code")

        if check_code(email, code):
            try:
                user = User.objects.get(email=email)
                user.is_active = True
                user.save()
                cache.delete(f"confirm_code:{email}")
                return Response({"message": "User confirmed"})
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=404)
        return Response({"error": "Invalid or expired code"}, status=400)
class ConfirmCodeView(generics.GenericAPIView):
    serializer_class = ConfirmCodeSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Пользователь успешно подтвержден"}, status=200)
        return Response(serializer.errors, status=400)
class CustomTokenView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


