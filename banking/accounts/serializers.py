from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import BankAccount, UserProfile
from decimal import Decimal


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['preferred_currency', 'theme']


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile']


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)
    preferred_currency = serializers.CharField(write_only=True, required=False, default='INR')

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name', 'preferred_currency']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        preferred_currency = validated_data.pop('preferred_currency', 'INR')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        UserProfile.objects.create(user=user, preferred_currency=preferred_currency)
        return user


class BankAccountSerializer(serializers.ModelSerializer):
    masked_account_number = serializers.ReadOnlyField()

    class Meta:
        model = BankAccount
        fields = [
            'id',
            'name',
            'bank_name',
            'account_number',
            'masked_account_number',
            'account_type',
            'currency',
            'opening_balance',
            'balance',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'balance', 'created_at', 'updated_at', 'masked_account_number']
        extra_kwargs = {
            'account_number': {'write_only': True}
        }

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['masked_account_number'] = instance.masked_account_number
        return ret

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        validated_data['balance'] = validated_data.get('opening_balance', Decimal('0.00'))
        return super().create(validated_data)


# Backward compatibility alias
AccountSerializer = BankAccountSerializer
