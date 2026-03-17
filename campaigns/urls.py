"""
Campaign URLs - Manual Routing (No Router Conflicts)
Location: campaigns/urls.py
"""

from django.urls import path
from campaigns.views import CampaignViewSet, CampaignStatsViewSet

# ============================================
# Campaign Routes
# ============================================

urlpatterns = [
    # Campaign CRUD
    path('create/', 
         CampaignViewSet.as_view({'post': 'create'}), 
         name='campaign-create'),
    
    path('list/', 
         CampaignViewSet.as_view({'get': 'list'}), 
         name='campaign-list'),
    
    path('<str:pk>/', 
         CampaignViewSet.as_view({'get': 'detail'}), 
         name='campaign-detail'),
    
    path('my-campaigns/', 
         CampaignViewSet.as_view({'get': 'my_campaigns'}), 
         name='campaign-my-campaigns'),
    
    path('<str:pk>/update/', 
         CampaignViewSet.as_view({'put': 'update_campaign'}), 
         name='campaign-update'),
    
    path('<str:pk>/delete/', 
         CampaignViewSet.as_view({'delete': 'delete_campaign'}), 
         name='campaign-delete'),
    
    # Campaign Actions
    path('<str:pk>/launch/', 
         CampaignViewSet.as_view({'post': 'launch'}), 
         name='campaign-launch'),
    
    path('<str:pk>/pause/', 
         CampaignViewSet.as_view({'post': 'pause'}), 
         name='campaign-pause'),
    
    path('<str:pk>/complete/', 
         CampaignViewSet.as_view({'post': 'complete'}), 
         name='campaign-complete'),
    
    path('<str:pk>/fail/', 
         CampaignViewSet.as_view({'post': 'fail'}), 
         name='campaign-fail'),
    
    path('<str:pk>/summary/', 
         CampaignViewSet.as_view({'get': 'summary'}), 
         name='campaign-summary'),
    
    path('charity/<str:charity_id>/', 
         CampaignViewSet.as_view({'get': 'charity_campaigns'}), 
         name='campaign-charity'),
    
    # Campaign Statistics
    path('stats/trending/', 
         CampaignStatsViewSet.as_view({'get': 'trending'}), 
         name='campaign-stats-trending'),
    
    path('stats/recent/', 
         CampaignStatsViewSet.as_view({'get': 'recent'}), 
         name='campaign-stats-recent'),
    
    path('stats/ending-soon/', 
         CampaignStatsViewSet.as_view({'get': 'ending_soon'}), 
         name='campaign-stats-ending-soon'),
    
    path('stats/by-location/', 
         CampaignStatsViewSet.as_view({'get': 'by_location'}), 
         name='campaign-stats-by-location'),
]