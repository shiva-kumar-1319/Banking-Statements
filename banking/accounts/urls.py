from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BankAccountViewSet, UserRegistrationView, CurrentUserProfileView

router = DefaultRouter()
router.register('accounts', BankAccountViewSet, basename='bankaccount')

urlpatterns = [
    path('auth/register/', UserRegistrationView.as_view(), name='auth-register'),
    path('auth/me/', CurrentUserProfileView.as_view(), name='auth-me'),
    path('', include(router.urls)),
]
