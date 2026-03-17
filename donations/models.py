from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
import uuid


class Donation(models.Model):
    """Individual donations to campaigns"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    donor = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='donations'
    )
    campaign = models.ForeignKey(
        'campaigns.Campaign',
        on_delete=models.CASCADE,
        related_name='donations'
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    
    is_anonymous = models.BooleanField(default=False)
    donor_name = models.CharField(max_length=255, blank=True, null=True)
    
    transaction_id = models.CharField(max_length=255, unique=True)
    payment_method = models.CharField(max_length=50)
    status = models.CharField(
        max_length=20,
        choices=(
            ('pending', 'Pending'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
            ('refunded', 'Refunded'),
        ),
        default='pending'
    )
    
    blockchain_tx_hash = models.CharField(max_length=255, blank=True, null=True)
    on_blockchain = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"${self.amount} to {self.campaign.title}"