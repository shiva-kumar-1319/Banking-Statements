from rest_framework import viewsets, permissions, status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from .models import BankAccount, UserProfile
from .serializers import (
    BankAccountSerializer,
    UserSerializer,
    UserRegistrationSerializer,
    UserProfileSerializer,
)


class UserRegistrationView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            "message": "User registered successfully.",
            "user": UserSerializer(user).data,
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


class CurrentUserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        user = request.user
        profile, _ = UserProfile.objects.get_or_create(user=user)

        user_data = {}
        if 'first_name' in request.data:
            user_data['first_name'] = request.data['first_name']
        if 'last_name' in request.data:
            user_data['last_name'] = request.data['last_name']
        if 'email' in request.data:
            user_data['email'] = request.data['email']

        for key, value in user_data.items():
            setattr(user, key, value)
        user.save()

        if 'preferred_currency' in request.data:
            profile.preferred_currency = request.data['preferred_currency']
        if 'theme' in request.data:
            profile.theme = request.data['theme']
        profile.save()

        return Response(UserSerializer(user).data)


class BankAccountViewSet(viewsets.ModelViewSet):
    serializer_class = BankAccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return BankAccount.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def recalculate(self, request, pk=None):
        account = self.get_object()
        new_balance = account.recalculate_balance()
        return Response({
            "message": "Account balance recalculated successfully.",
            "balance": str(new_balance),
            "account": BankAccountSerializer(account).data
        })


# Backward compatibility alias
AccountViewSet = BankAccountViewSet
