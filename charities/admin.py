"""
Charities Admin Configuration
Location: charities/admin.py
IMPORTANT: Only import CharityOrganization from .models
User is available through ForeignKey relationships
"""

from django.contrib import admin
from .models import CharityOrganization


@admin.register(CharityOrganization)
class CharityOrganizationAdmin(admin.ModelAdmin):
    """Charity organization admin"""
    
    list_display = ('organization_name', 'status', 'registration_number', 'total_funds_raised', 'created_at')
    list_filter = ('status', 'bank_verification_status', 'created_at')
    search_fields = ('organization_name', 'registration_number', 'user__email')
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Organization Info', {
            'fields': ('id', 'organization_name', 'registration_number', 'legal_registration_cert_url')
        }),
        ('Contact Info', {
            'fields': ('user', 'responsible_person', 'address', 'website')
        }),
        ('Financial Info', {
            'fields': ('bank_name', 'bank_account_number', 'bank_verification_status', 'total_funds_raised', 'total_funds_spent')
        }),
        ('Verification', {
            'fields': ('status', 'verified_by', 'rejection_reason', 'suspension_reason')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )