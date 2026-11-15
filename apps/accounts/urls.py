from django.urls import path

from .views import LoginAPIView, MeAPIView, RegisterAPIView

urlpatterns = [
    path("auth/register/", RegisterAPIView.as_view(), name="auth-register"),
    path("auth/login/", LoginAPIView.as_view(), name="auth-login"),
    path("auth/me/", MeAPIView.as_view(), name="auth-me"),
]
