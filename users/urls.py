from django.urls import path
from .views import RegisterView, ConfirmCodeView, CustomTokenView, ConfirmView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.authtoken.views import obtain_auth_token
from users .oauth import GoogleLoginView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
schema_view = get_schema_view(
    openapi.Info(
        title="Shop API",
        default_version='v1',
        description="Документация API",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)
urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('confirm/', ConfirmCodeView.as_view()),
    path('login/', CustomTokenView.as_view()),
    path('refresh/', TokenRefreshView.as_view()),
    path('api/v1/auth-token/', obtain_auth_token, name='api_token_auth'),
    path('google-login/', GoogleLoginView.as_view()),
    path("register/", RegisterView.as_view()),
    path("confirm/", ConfirmView.as_view()),
    path("swagger/", schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    
]
