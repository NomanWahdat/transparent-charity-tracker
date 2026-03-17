"""
Donation URLs - Manual Routing (No Router Conflicts)
Location: donations/urls.py
"""

from django.urls import path
from donations.views import DonationViewSet, DonationStatsViewSet

# ============================================
# Donation Routes
# ============================================

urlpatterns = [
    # Donation CRUD
    path('create/', 
         DonationViewSet.as_view({'post': 'create'}), 
         name='donation-create'),
    
    path('my-donations/', 
         DonationViewSet.as_view({'get': 'my_donations'}), 
         name='donation-my-donations'),
    
    path('campaign/<str:campaign_id>/', 
         DonationViewSet.as_view({'get': 'campaign_donations'}), 
         name='donation-campaign-donations'),
    
    path('<str:pk>/', 
         DonationViewSet.as_view({'get': 'detail'}), 
         name='donation-detail'),
    
    path('<str:pk>/verify/', 
         DonationViewSet.as_view({'post': 'verify'}), 
         name='donation-verify'),
    
    # Donation Statistics
    path('stats/total/', 
         DonationStatsViewSet.as_view({'get': 'total'}), 
         name='donation-stats-total'),
    
    path('stats/by-campaign/', 
         DonationStatsViewSet.as_view({'get': 'by_campaign'}), 
         name='donation-stats-by-campaign'),
    
    path('stats/top-donors/', 
         DonationStatsViewSet.as_view({'get': 'top_donors'}), 
         name='donation-stats-top-donors'),
]