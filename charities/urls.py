"""
Charities URLs Configuration
Location: charities/urls.py
"""

from django.urls import path
from .views import CharityViewSet

urlpatterns = [
    path('register/', CharityViewSet.as_view({'post': 'register'}), name='charity-register'),
    path('my_charity/', CharityViewSet.as_view({'get': 'my_charity'}), name='charity-my-charity'),
    path('update/', CharityViewSet.as_view({'put': 'update'}), name='charity-update'),
    path('list/', CharityViewSet.as_view({'get': 'list'}), name='charity-list'),
    path('<str:pk>/', CharityViewSet.as_view({'get': 'detail'}), name='charity-detail'),
]