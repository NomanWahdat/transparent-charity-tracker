"""
Users Models
Location: users/models.py
"""

from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Custom user model with role-based access control
    Extends Django's AbstractUser
    """
    
    ROLE_CHOICES = (
        ('donor', 'Donor'),
        ('charity', 'Charity'),
        ('admin', 'Admin'),
    )
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='donor'
    )
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    verified = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
        ]
    
    def __str__(self):
        return self.email
    
    def is_donor(self):
        return self.role == 'donor'
    
    def is_charity(self):
        return self.role == 'charity'
    
    def is_admin(self):
        return self.role == 'admin' or self.is_staff