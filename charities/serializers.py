"""
Charities Serializers
Location: charities/serializers.py
"""

from rest_framework import serializers
from .models import CharityOrganization


class CharityRegistrationSerializer(serializers.ModelSerializer):
    """Register a new charity organization"""
    
    class Meta:
        model = CharityOrganization
        fields = (
            'organization_name',
            'registration_number',
            'legal_registration_cert_url',
            'address',
            'responsible_person',
            'bank_account_number',
            'bank_name',
            'website',
            'description',
        )
    
    def create(self, validated_data):
        """Create charity with current user"""
        user = self.context['request'].user
        charity = CharityOrganization.objects.create(user=user, **validated_data)
        return charity


class CharityDetailSerializer(serializers.ModelSerializer):
    """Full charity details"""
    
    user_email = serializers.CharField(source='user.email', read_only=True)
    verified_by_name = serializers.CharField(
        source='verified_by.username',
        read_only=True,
        allow_null=True
    )
    
    class Meta:
        model = CharityOrganization
        fields = (
            'id',
            'organization_name',
            'registration_number',
            'legal_registration_cert_url',
            'address',
            'responsible_person',
            'bank_account_number',
            'bank_name',
            'bank_verification_status',
            'website',
            'description',
            'status',
            'verified_by_name',
            'rejection_reason',
            'suspension_reason',
            'total_funds_raised',
            'total_funds_spent',
            'user_email',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'id',
            'status',
            'verified_by',
            'total_funds_raised',
            'total_funds_spent',
            'created_at',
            'updated_at',
        )


class CharityListSerializer(serializers.ModelSerializer):
    """Lightweight charity listing"""
    
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = CharityOrganization
        fields = (
            'id',
            'organization_name',
            'status',
            'total_funds_raised',
            'total_funds_spent',
            'user_email',
        )


class CharityUpdateSerializer(serializers.ModelSerializer):
    """Update charity organization"""
    
    class Meta:
        model = CharityOrganization
        fields = (
            'organization_name',
            'address',
            'responsible_person',
            'website',
            'description',
        )


class CharityVerifySerializer(serializers.Serializer):
    """Verify/reject charity"""
    
    DECISION_CHOICES = (
        ('verify', 'Verify'),
        ('reject', 'Reject'),
        ('suspend', 'Suspend'),
    )
    
    decision = serializers.ChoiceField(choices=DECISION_CHOICES)
    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text='Reason for rejection or suspension'
    )