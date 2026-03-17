"""
Donation Management System - Serializers
Handles donor contributions and tracking
Location: donations/serializers.py
"""

from rest_framework import serializers
from django.utils import timezone
from decimal import Decimal
from donations.models import Donation
from campaigns.models import Campaign


# ============================================
# DONATION SERIALIZERS
# ============================================

class DonationSerializer(serializers.ModelSerializer):
    """Display donation details"""
    
    donor_username = serializers.SerializerMethodField()
    campaign_title = serializers.CharField(
        source='campaign.title',
        read_only=True
    )
    
    class Meta:
        model = Donation
        fields = [
            'id', 'donor_username', 'campaign_title', 'amount',
            'is_anonymous', 'status', 'transaction_id',
            'payment_method', 'on_blockchain', 'blockchain_tx_hash',
            'created_at'
        ]
        read_only_fields = [
            'id', 'status', 'transaction_id', 'blockchain_tx_hash',
            'on_blockchain', 'created_at'
        ]
    
    def get_donor_username(self, obj):
        """Get donor name safely"""
        if obj.is_anonymous:
            return 'Anonymous Donor'
        return obj.donor.username if obj.donor else 'Unknown'


class DonationCreateSerializer(serializers.ModelSerializer):
    """Create new donation"""
    
    campaign_id = serializers.CharField(write_only=True)
    
    class Meta:
        model = Donation
        fields = [
            'campaign_id', 'amount', 'is_anonymous', 'donor_name',
            'payment_method'
        ]
    
    def validate_amount(self, value):
        """Validate donation amount"""
        if value <= 0:
            raise serializers.ValidationError('Donation amount must be greater than 0.')
        if value > Decimal('999999.99'):
            raise serializers.ValidationError('Donation amount exceeds maximum limit.')
        return value
    
    def validate(self, attrs):
        """Validate campaign exists and is active"""
        campaign_id = attrs.get('campaign_id')
        
        try:
            campaign = Campaign.objects.get(id=campaign_id)
        except Campaign.DoesNotExist:
            raise serializers.ValidationError('Campaign not found.')
        
        if campaign.status != 'active':
            raise serializers.ValidationError('Campaign is not accepting donations.')
        
        if campaign.end_date <= timezone.now():
            raise serializers.ValidationError('Campaign has ended.')
        
        attrs['campaign'] = campaign
        return attrs
    
    def create(self, validated_data):
        """Create donation"""
        campaign = validated_data.pop('campaign')
        user = self.context['request'].user
        
        donation = Donation.objects.create(
            donor=user,
            campaign=campaign,
            status='completed',
            transaction_id=f'TXN-{timezone.now().timestamp()}',
            **validated_data
        )
        
        # Update campaign current amount
        campaign.current_amount += donation.amount
        
        # Increment donor count if not anonymous
        if not donation.is_anonymous:
            campaign.donor_count += 1
        
        campaign.save()
        
        return donation


class DonationListSerializer(serializers.ModelSerializer):
    """Lightweight donation listing"""
    
    class Meta:
        model = Donation
        fields = [
            'id', 'amount', 'is_anonymous', 'status', 'created_at'
        ]


class DonationPublicSerializer(serializers.ModelSerializer):
    """Public donation display (for campaign page)"""
    
    donor_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Donation
        fields = [
            'id', 'donor_name', 'amount', 'created_at'
        ]
    
    def get_donor_name(self, obj):
        """Show donor name or anonymous"""
        if obj.is_anonymous:
            return 'Anonymous'
        return obj.donor_name if obj.donor_name else obj.donor.username


class DonationDetailSerializer(serializers.ModelSerializer):
    """Detailed donation information"""
    
    donor_info = serializers.SerializerMethodField()
    campaign_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Donation
        fields = [
            'id', 'amount', 'status', 'payment_method', 'transaction_id',
            'donor_info', 'campaign_info', 'blockchain_tx_hash', 'on_blockchain',
            'created_at', 'updated_at'
        ]
    
    def get_donor_info(self, obj):
        """Get donor information"""
        if obj.is_anonymous:
            return {
                'type': 'anonymous',
                'name': obj.donor_name or 'Anonymous Donor'
            }
        
        return {
            'type': 'registered',
            'id': str(obj.donor.id) if obj.donor else None,
            'username': obj.donor.username if obj.donor else 'Unknown',
            'email': obj.donor.email if obj.donor else None
        }
    
    def get_campaign_info(self, obj):
        """Get campaign information"""
        return {
            'id': str(obj.campaign.id),
            'title': obj.campaign.title,
            'charity': obj.campaign.charity.organization_name
        }