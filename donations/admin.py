from django.contrib import admin
from .models import Donation


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    """Donation admin"""
    
    list_display = ('id', 'donor', 'campaign', 'amount', 'status', 'is_anonymous', 'on_blockchain', 'created_at')
    list_filter = ('status', 'is_anonymous', 'on_blockchain', 'created_at', 'payment_method')
    search_fields = ('campaign__title', 'donor__email', 'transaction_id')
    readonly_fields = ('id', 'created_at', 'updated_at', 'transaction_id')
    
    fieldsets = (
        ('Donation Info', {
            'fields': ('id', 'campaign', 'amount', 'transaction_id')
        }),
        ('Donor Info', {
            'fields': ('donor', 'is_anonymous', 'donor_name')
        }),
        ('Payment', {
            'fields': ('status', 'payment_method')
        }),
        ('Blockchain', {
            'fields': ('on_blockchain', 'blockchain_tx_hash')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )