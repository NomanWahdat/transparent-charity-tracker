from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
import uuid


class Campaign(models.Model):
    """Fundraising campaigns by charities"""
    
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    charity = models.ForeignKey(
        'charities.CharityOrganization',
        on_delete=models.CASCADE,
        related_name='campaigns'
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    goal_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    current_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    expected_expenses = models.TextField(help_text="Breakdown of expected expenses")
    estimated_product_list = models.JSONField(
        default=list,
        help_text="List of products needed"
    )
    target_beneficiaries = models.IntegerField(validators=[MinValueValidator(1)])
    beneficiary_location = models.CharField(max_length=255)
    
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    donor_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def percentage_funded(self):
        if self.goal_amount == 0:
            return 0
        return (self.current_amount / self.goal_amount) * 100