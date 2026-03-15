"""
Django Models for Transparent Charity Tracker
Complete database schema with all relationships
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.core import validators
import uuid


class User(AbstractUser):
    """Extended User model with role-based system"""
    
    ROLE_CHOICES = (
        ('donor', 'Donor'),
        ('charity', 'Charity Organization'),
        ('admin', 'Admin/Auditor'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['role']),
            models.Index(fields=['verified']),
        ]
    
    def __str__(self):
        return f"{self.username} ({self.role})"


class CharityOrganization(models.Model):
    """Verified charity organizations"""
    
    VERIFICATION_STATUS = (
        ('pending', 'Pending Verification'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
        ('suspended', 'Suspended'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='charity')
    organization_name = models.CharField(max_length=255)
    registration_number = models.CharField(max_length=100, unique=True)
    legal_registration_cert_url = models.URLField()
    address = models.TextField()
    responsible_person = models.CharField(max_length=255)
    bank_account_number = models.CharField(max_length=50)
    bank_name = models.CharField(max_length=255)
    bank_verification_status = models.BooleanField(default=False)
    website = models.URLField(blank=True, null=True)
    description = models.TextField()
    
    # Verification
    status = models.CharField(
        max_length=20, 
        choices=VERIFICATION_STATUS, 
        default='pending'
    )
    verified_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='charities_verified'
    )
    rejection_reason = models.TextField(blank=True, null=True)
    suspension_reason = models.TextField(blank=True, null=True)
    
    # Metadata
    total_funds_raised = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)]
    )
    total_funds_spent = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['registration_number']),
        ]
    
    def __str__(self):
        return self.organization_name


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
        CharityOrganization, 
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
    
    # Campaign Details
    expected_expenses = models.TextField(help_text="Breakdown of expected expenses")
    estimated_product_list = models.JSONField(
        default=list,
        help_text="List of products needed: [{name, quantity, est_price}, ...]"
    )
    target_beneficiaries = models.IntegerField(validators=[MinValueValidator(1)])
    beneficiary_location = models.CharField(max_length=255)
    
    # Timeline
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Metadata
    donor_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['charity']),
        ]
    
    def __str__(self):
        return self.title
    
    def percentage_funded(self):
        if self.goal_amount == 0:
            return 0
        return (self.current_amount / self.goal_amount) * 100


class Donation(models.Model):
    """Individual donations to campaigns"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    donor = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='donations'
    )
    campaign = models.ForeignKey(
        Campaign, 
        on_delete=models.CASCADE, 
        related_name='donations'
    )
    amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    
    # Anonymous donations
    is_anonymous = models.BooleanField(default=False)
    donor_name = models.CharField(max_length=255, blank=True, null=True)
    
    # Transaction details
    transaction_id = models.CharField(max_length=255, unique=True)
    payment_method = models.CharField(max_length=50)  # card, bank_transfer, etc
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
    
    # Blockchain
    blockchain_tx_hash = models.CharField(max_length=255, blank=True, null=True)
    on_blockchain = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['campaign']),
            models.Index(fields=['donor']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        donor_str = self.donor_name if self.is_anonymous else str(self.donor)
        return f"${self.amount} to {self.campaign.title}"


class Expense(models.Model):
    """Expense records submitted by charities"""
    
    STATUS_CHOICES = (
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('flagged', 'Flagged for Review'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campaign = models.ForeignKey(
        Campaign, 
        on_delete=models.CASCADE, 
        related_name='expenses'
    )
    
    # Item details
    item_name = models.CharField(max_length=255)
    category = models.CharField(
        max_length=50,
        choices=(
            ('education', 'Education'),
            ('health', 'Healthcare'),
            ('food', 'Food & Nutrition'),
            ('supplies', 'Supplies'),
            ('infrastructure', 'Infrastructure'),
            ('other', 'Other'),
        )
    )
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    total_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    
    # Pricing Verification
    market_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True,
        help_text="Market price per unit"
    )
    price_difference = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True,
        help_text="Difference from market price"
    )
    price_variance_percent = models.FloatField(
        blank=True, 
        null=True,
        help_text="Percentage difference: (entered - market) / market * 100"
    )
    is_overpriced = models.BooleanField(default=False)
    
    # Vendor & Purchase Info
    vendor_name = models.CharField(max_length=255)
    vendor_location = models.CharField(max_length=255, blank=True, null=True)
    purchase_date = models.DateField()
    
    # Documentation
    receipt_url = models.URLField(blank=True, null=True)
    invoice_url = models.URLField(blank=True, null=True)
    delivery_photo_url = models.URLField(blank=True, null=True)
    beneficiary_confirmation_url = models.URLField(blank=True, null=True)
    
    # Status & Review
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending'
    )
    explanation = models.TextField(blank=True, null=True)
    
    # Fraud Detection
    is_suspicious = models.BooleanField(default=False)
    fraud_score = models.FloatField(default=0.0, validators=[MinValueValidator(0), validators.MaxValueValidator(1)])
    fraud_reason = models.TextField(blank=True, null=True)
    is_duplicate = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['campaign']),
            models.Index(fields=['status']),
            models.Index(fields=['is_suspicious']),
        ]
    
    def __str__(self):
        return f"{self.item_name} - {self.quantity} units"
    
    def save(self, *args, **kwargs):
        """Auto-calculate total_amount"""
        self.total_amount = self.quantity * self.unit_price
        super().save(*args, **kwargs)


class PriceReference(models.Model):
    """Market price database for price verification"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product_name = models.CharField(max_length=255, db_index=True)
    category = models.CharField(max_length=50)
    average_market_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    price_range_min = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    price_range_max = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    
    # Data source
    source = models.CharField(max_length=100)  # e.g., 'Amazon', 'Local Market', etc
    last_updated = models.DateTimeField(auto_now=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-last_updated']
        indexes = [
            models.Index(fields=['product_name']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return f"{self.product_name} - ${self.average_market_price}"


class FraudDetectionLog(models.Model):
    """Log of all fraud detection activities"""
    
    FRAUD_TYPE = (
        ('overpriced', 'Overpriced Item'),
        ('duplicate', 'Duplicate Expense'),
        ('fake_receipt', 'Suspicious Receipt'),
        ('unusual_pattern', 'Unusual Spending Pattern'),
        ('location_mismatch', 'Location Mismatch'),
        ('other', 'Other'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    expense = models.ForeignKey(
        Expense, 
        on_delete=models.CASCADE, 
        related_name='fraud_logs'
    )
    fraud_type = models.CharField(max_length=50, choices=FRAUD_TYPE)
    fraud_score = models.FloatField(validators=[MinValueValidator(0)])
    description = models.TextField()
    ai_model_used = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        help_text="Which ML model detected this"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.fraud_type} - {self.expense.item_name}"


class PublicReport(models.Model):
    """Public reports on suspicious spending"""
    
    STATUS_CHOICES = (
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('addressed', 'Addressed'),
        ('dismissed', 'Dismissed'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    expense = models.ForeignKey(
        Expense, 
        on_delete=models.CASCADE, 
        related_name='public_reports'
    )
    
    # Report details
    reporter_name = models.CharField(max_length=255, blank=True, null=True)
    reporter_email = models.EmailField(blank=True, null=True)
    description = models.TextField()
    evidence = models.URLField(blank=True, null=True)
    
    # Review
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    reviewed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='reviews'
    )
    admin_response = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Report on {self.expense.item_name}"


class ImpactReport(models.Model):
    """Impact reports submitted by charities"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campaign = models.ForeignKey(
        Campaign, 
        on_delete=models.CASCADE, 
        related_name='impact_reports'
    )
    
    # Impact metrics
    beneficiaries_count = models.IntegerField(validators=[MinValueValidator(1)])
    location = models.CharField(max_length=255)
    description = models.TextField()
    
    # Documentation
    photo_url = models.URLField(blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    
    report_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-report_date']
    
    def __str__(self):
        return f"Impact Report - {self.campaign.title}"


class CharityRating(models.Model):
    """Donor ratings for charities"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    charity = models.ForeignKey(
        CharityOrganization, 
        on_delete=models.CASCADE, 
        related_name='ratings'
    )
    donor = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='charity_ratings'
    )
    campaign = models.ForeignKey(
        Campaign, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='ratings'
    )
    
    # Ratings
    transparency_rating = models.IntegerField(
        validators=[MinValueValidator(1), validators.MaxValueValidator(5)]
    )
    impact_rating = models.IntegerField(
        validators=[MinValueValidator(1), validators.MaxValueValidator(5)]
    )
    trust_rating = models.IntegerField(
        validators=[MinValueValidator(1), validators.MaxValueValidator(5)]
    )
    overall_rating = models.FloatField(
        validators=[MinValueValidator(1), validators.MaxValueValidator(5)]
    )
    
    comment = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ('charity', 'donor', 'campaign')
    
    def __str__(self):
        return f"Rating for {self.charity.organization_name}"
    
    def save(self, *args, **kwargs):
        """Auto-calculate overall rating"""
        self.overall_rating = (
            self.transparency_rating + 
            self.impact_rating + 
            self.trust_rating
        ) / 3
        super().save(*args, **kwargs)


class DonationNotification(models.Model):
    """Notifications sent to donors"""
    
    NOTIFICATION_TYPE = (
        ('funds_spent', 'Funds Spent'),
        ('purchase_made', 'Purchase Made'),
        ('project_completed', 'Project Completed'),
        ('rating_request', 'Rating Request'),
        ('suspicious_activity', 'Suspicious Activity'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    donor = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    campaign = models.ForeignKey(
        Campaign, 
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPE)
    title = models.CharField(max_length=255)
    message = models.TextField()
    
    # Related objects
    expense = models.ForeignKey(
        Expense, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class BlockchainLedger(models.Model):
    """Blockchain transaction ledger"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    donation = models.OneToOneField(
        Donation, 
        on_delete=models.CASCADE,
        related_name='blockchain_record'
    )
    
    # Blockchain details
    blockchain_network = models.CharField(max_length=50)  # ethereum, polygon, etc
    contract_address = models.CharField(max_length=255)
    transaction_hash = models.CharField(max_length=255, unique=True)
    from_address = models.CharField(max_length=255)
    to_address = models.CharField(max_length=255)
    
    # Transaction data
    amount_in_wei = models.CharField(max_length=100)
    gas_used = models.CharField(max_length=100)
    gas_price = models.CharField(max_length=100)
    
    # Status
    is_confirmed = models.BooleanField(default=False)
    confirmation_blocks = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Blockchain: {self.transaction_hash[:10]}..."


class OCRExtraction(models.Model):
    """OCR data extracted from receipts"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    expense = models.OneToOneField(
        Expense, 
        on_delete=models.CASCADE,
        related_name='ocr_data'
    )
    
    # Extracted text
    raw_text = models.TextField()
    extracted_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True
    )
    extracted_vendor = models.CharField(max_length=255, blank=True, null=True)
    extracted_date = models.DateField(blank=True, null=True)
    
    # Validation
    matches_submitted_amount = models.BooleanField(default=False)
    confidence_score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0), validators.MaxValueValidator(1)]
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"OCR for {self.expense.item_name}"


# Import validators at top if needed
from django.core import validators