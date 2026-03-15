from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, CharityOrganization, Campaign, Donation,
    Expense, PriceReference, FraudDetectionLog,
    PublicReport, ImpactReport, CharityRating,
    DonationNotification, BlockchainLedger, OCRExtraction
)

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone', 'address', 'verified', 'verified_at')}),
    )
    list_display = ('username', 'email', 'role', 'verified')
    list_filter = ('role', 'verified')

@admin.register(CharityOrganization)
class CharityOrganizationAdmin(admin.ModelAdmin):
    list_display = ('organization_name', 'status', 'total_funds_raised', 'total_funds_spent')
    list_filter = ('status', 'verified_by')
    search_fields = ('organization_name', 'registration_number')

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('title', 'charity', 'goal_amount', 'current_amount', 'status')
    list_filter = ('status', 'charity')
    search_fields = ('title', 'description')

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('id', 'campaign', 'amount', 'status', 'created_at')
    list_filter = ('status', 'campaign')
    search_fields = ('transaction_id', 'donor_name')

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('item_name', 'campaign', 'total_amount', 'status', 'is_suspicious')
    list_filter = ('status', 'is_suspicious', 'category')
    search_fields = ('item_name', 'vendor_name')

@admin.register(PriceReference)
class PriceReferenceAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'average_market_price', 'source')
    list_filter = ('category', 'source')
    search_fields = ('product_name',)

@admin.register(FraudDetectionLog)
class FraudDetectionLogAdmin(admin.ModelAdmin):
    list_display = ('expense', 'fraud_type', 'fraud_score')
    list_filter = ('fraud_type',)
    search_fields = ('expense__item_name',)

@admin.register(PublicReport)
class PublicReportAdmin(admin.ModelAdmin):
    list_display = ('expense', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('reporter_name', 'reporter_email')

@admin.register(ImpactReport)
class ImpactReportAdmin(admin.ModelAdmin):
    list_display = ('campaign', 'beneficiaries_count', 'location')
    list_filter = ('campaign',)
    search_fields = ('location',)

@admin.register(CharityRating)
class CharityRatingAdmin(admin.ModelAdmin):
    list_display = ('charity', 'overall_rating', 'donor')
    list_filter = ('overall_rating',)
    search_fields = ('charity__organization_name',)

@admin.register(DonationNotification)
class DonationNotificationAdmin(admin.ModelAdmin):
    list_display = ('donor', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read')
    search_fields = ('title',)

@admin.register(BlockchainLedger)
class BlockchainLedgerAdmin(admin.ModelAdmin):
    list_display = ('donation', 'blockchain_network', 'is_confirmed')
    list_filter = ('blockchain_network', 'is_confirmed')
    search_fields = ('transaction_hash',)

@admin.register(OCRExtraction)
class OCRExtractionAdmin(admin.ModelAdmin):
    list_display = ('expense', 'confidence_score', 'matches_submitted_amount')
    list_filter = ('matches_submitted_amount',)
    search_fields = ('expense__item_name',)