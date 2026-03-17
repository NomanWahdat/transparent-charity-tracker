from django.contrib import admin
from .models import Campaign


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    """Campaign admin"""
    
    list_display = ('title', 'charity', 'status', 'goal_amount', 'current_amount', 'donor_count', 'end_date', 'created_at')
    list_filter = ('status', 'created_at', 'start_date', 'end_date')
    search_fields = ('title', 'charity__organization_name')
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Campaign Info', {
            'fields': ('id', 'title', 'description', 'charity')
        }),
        ('Funding', {
            'fields': ('goal_amount', 'current_amount', 'donor_count')
        }),
        ('Timeline', {
            'fields': ('start_date', 'end_date', 'status')
        }),
        ('Beneficiaries', {
            'fields': ('target_beneficiaries', 'beneficiary_location')
        }),
        ('Details', {
            'fields': ('expected_expenses', 'estimated_product_list')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )