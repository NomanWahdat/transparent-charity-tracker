"""
Users URLs Configuration
Location: users/urls.py
"""

from django.urls import path
from .views import UserViewSet

urlpatterns = [
    path('register/', UserViewSet.as_view({'post': 'register'}), name='user-register'),
    path('login/', UserViewSet.as_view({'post': 'login'}), name='user-login'),
    path('refresh/', UserViewSet.as_view({'post': 'refresh'}), name='user-refresh'),
    path('profile/', UserViewSet.as_view({'get': 'profile'}), name='user-profile'),
    path('profile/update/', UserViewSet.as_view({'put': 'update'}), name='user-update'),
    path('profile/change_password/', UserViewSet.as_view({'post': 'change_password'}), name='user-change-password'),
    path('logout/', UserViewSet.as_view({'post': 'logout'}), name='user-logout'),
]