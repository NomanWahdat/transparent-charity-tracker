"""
Campaign Management System - Serializers
Handles campaign creation, management, and status transitions
"""

from rest_framework import serializers
from django.utils import timezone
from campaigns.models import Campaign
from charities.models import CharityOrganization
from donations.models import Donation


class CampaignSerializer(serializers.ModelSerializer):
    """Display campaign details"""
    
    charity_name = serializers.CharField(
        source='charity.organization_name',
        read_only=True
    )
    charity_id = serializers.CharField(
        source='charity.id',
        read_only=True
    )
    percentage_funded = serializers.SerializerMethodField()
    time_remaining = serializers.SerializerMethodField()
    days_active = serializers.SerializerMethodField()
    
    class Meta:
        model = Campaign
        fields = [
            'id', 'title', 'description', 'goal_amount', 'current_amount',
            'status', 'start_date', 'end_date', 'target_beneficiaries',
            'beneficiary_location', 'expected_expenses', 'estimated_product_list',
            'donor_count', 'percentage_funded', 'time_remaining', 'days_active',
            'charity_id', 'charity_name', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'current_amount', 'donor_count', 'created_at', 'updated_at'
        ]
    
    def get_percentage_funded(self, obj):
        """Calculate funding percentage"""
        if obj.goal_amount == 0:
            return 0
        return round((obj.current_amount / obj.goal_amount) * 100, 2)
    
    def get_time_remaining(self, obj):
        """Calculate time remaining in hours"""
        if obj.status in ['completed', 'failed']:
            return 0
        
        now = timezone.now()
        if obj.end_date > now:
            delta = obj.end_date - now
            hours = delta.total_seconds() / 3600
            return round(hours, 2)
        return 0
    
    def get_days_active(self, obj):
        """Calculate days campaign has been active"""
        delta = timezone.now() - obj.start_date
        return delta.days


class CampaignCreateSerializer(serializers.ModelSerializer):
    """Create new campaign"""
    
    class Meta:
        model = Campaign
        fields = [
            'title', 'description', 'goal_amount', 'end_date',
            'expected_expenses', 'estimated_product_list',
            'target_beneficiaries', 'beneficiary_location'
        ]
    
    def validate_goal_amount(self, value):
        """Validate goal amount"""
        if value <= 0:
            raise serializers.ValidationError('Goal amount must be greater than 0.')
        return value
    
    def validate_end_date(self, value):
        """Validate end date is in future"""
        if value <= timezone.now():
            raise serializers.ValidationError('End date must be in the future.')
        return value
    
    def validate_target_beneficiaries(self, value):
        """Validate beneficiaries count"""
        if value <= 0:
            raise serializers.ValidationError('Target beneficiaries must be greater than 0.')
        return value
    
    def create(self, validated_data):
        """Create campaign for current charity"""
        user = self.context['request'].user
        
        try:
            charity = user.charity
        except:
            raise serializers.ValidationError('You must have a verified charity to create campaigns.')
        
        if charity.status != 'verified':
            raise serializers.ValidationError('Your charity must be verified to create campaigns.')
        
        campaign = Campaign.objects.create(
            charity=charity,
            **validated_data
        )
        
        return campaign


class CampaignUpdateSerializer(serializers.ModelSerializer):
    """Update campaign details"""
    
    class Meta:
        model = Campaign
        fields = [
            'title', 'description', 'goal_amount', 'end_date',
            'expected_expenses', 'estimated_product_list',
            'target_beneficiaries', 'beneficiary_location'
        ]
    
    def validate_end_date(self, value):
        """Validate end date cannot be in past"""
        if value <= timezone.now():
            raise serializers.ValidationError('End date must be in the future.')
        return value


class CampaignListSerializer(serializers.ModelSerializer):
    """Lightweight campaign listing"""
    
    charity_name = serializers.CharField(
        source='charity.organization_name',
        read_only=True
    )
    percentage_funded = serializers.SerializerMethodField()
    
    class Meta:
        model = Campaign
        fields = [
            'id', 'title', 'goal_amount', 'current_amount', 'status',
            'target_beneficiaries', 'beneficiary_location', 'percentage_funded',
            'charity_name', 'start_date', 'end_date'
        ]
    
    def get_percentage_funded(self, obj):
        if obj.goal_amount == 0:
            return 0
        return round((obj.current_amount / obj.goal_amount) * 100, 2)


class CampaignStatusChangeSerializer(serializers.Serializer):
    """Change campaign status"""
    
    status = serializers.ChoiceField(
        choices=['active', 'paused', 'completed', 'failed']
    )
    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text='Reason for status change (required for failed/paused)'
    )
    
    def validate(self, attrs):
        """Validate status transition"""
        status = attrs.get('status')
        
        if status in ['paused', 'failed'] and not attrs.get('reason'):
            raise serializers.ValidationError(
                'Reason is required for paused or failed status.'
            )
        
        return attrs


class CampaignDonationSummarySerializer(serializers.ModelSerializer):
    """Campaign with donation summary"""
    
    total_donations = serializers.SerializerMethodField()
    total_donors = serializers.SerializerMethodField()
    percentage_funded = serializers.SerializerMethodField()
    
    class Meta:
        model = Campaign
        fields = [
            'id', 'title', 'goal_amount', 'current_amount', 'status',
            'total_donations', 'total_donors', 'percentage_funded',
            'donor_count', 'start_date', 'end_date'
        ]
    
    def get_total_donations(self, obj):
        """Count total donations"""
        return obj.donations.filter(status='completed').count()
    
    def get_total_donors(self, obj):
        """Count unique donors"""
        return obj.donations.filter(status='completed').values('donor').distinct().count()
    
    def get_percentage_funded(self, obj):
        if obj.goal_amount == 0:
            return 0
        return round((obj.current_amount / obj.goal_amount) * 100, 2)


class CampaignDetailedSerializer(serializers.ModelSerializer):
    """Detailed campaign info with donations"""
    
    charity_name = serializers.CharField(
        source='charity.organization_name',
        read_only=True
    )
    charity_email = serializers.CharField(
        source='charity.user.email',
        read_only=True
    )
    percentage_funded = serializers.SerializerMethodField()
    recent_donations = serializers.SerializerMethodField()
    
    class Meta:
        model = Campaign
        fields = [
            'id', 'title', 'description', 'goal_amount', 'current_amount',
            'status', 'start_date', 'end_date', 'target_beneficiaries',
            'beneficiary_location', 'expected_expenses', 'estimated_product_list',
            'percentage_funded', 'donor_count', 'recent_donations',
            'charity_name', 'charity_email', 'created_at', 'updated_at'
        ]
    
    def get_percentage_funded(self, obj):
        if obj.goal_amount == 0:
            return 0
        return round((obj.current_amount / obj.goal_amount) * 100, 2)
    
    def get_recent_donations(self, obj):
        """Get last 5 donations"""
        donations = obj.donations.filter(
            status='completed'
        ).order_by('-created_at')[:5]
        
        return [
            {
                'id': str(d.id),
                'amount': str(d.amount),
                'donor_name': d.donor_name if d.is_anonymous else d.donor.username,
                'date': d.created_at
            }
            for d in donations
        ]