"""
Charities Views
Location: charities/views.py
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import CharityOrganization
from .serializers import (
    CharityRegistrationSerializer,
    CharityDetailSerializer,
    CharityListSerializer,
    CharityUpdateSerializer,
    CharityVerifySerializer,
)


class CharityViewSet(viewsets.ViewSet):
    """Charity organization management"""
    
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        """Register a new charity"""
        if not request.user.is_authenticated:
            return Response({
                'success': False,
                'message': 'You must be logged in to register a charity.'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        serializer = CharityRegistrationSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            charity = serializer.save()
            return Response({
                'success': True,
                'message': 'Charity registered! Waiting for verification.',
                'data': CharityDetailSerializer(charity).data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def my_charity(self, request):
        """Get current user's charity"""
        if not request.user.is_authenticated:
            return Response({
                'success': False,
                'message': 'Not authenticated.'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            charity = request.user.charity
            serializer = CharityDetailSerializer(charity)
            return Response({
                'success': True,
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except:
            return Response({
                'success': False,
                'message': 'You do not have a registered charity.'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['put'])
    def update(self, request):
        """Update charity details"""
        if not request.user.is_authenticated:
            return Response({
                'success': False,
                'message': 'Not authenticated.'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            charity = request.user.charity
            serializer = CharityUpdateSerializer(
                charity,
                data=request.data,
                partial=True
            )
            
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'success': True,
                    'message': 'Charity updated successfully!',
                    'data': CharityDetailSerializer(charity).data
                }, status=status.HTTP_200_OK)
            
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except:
            return Response({
                'success': False,
                'message': 'You do not have a registered charity.'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def list(self, request):
        """List verified charities"""
        charities = CharityOrganization.objects.filter(
            status='verified'
        ).order_by('-created_at')
        
        serializer = CharityListSerializer(charities, many=True)
        
        return Response({
            'success': True,
            'count': charities.count(),
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'])
    def detail(self, request, pk=None):
        """Get charity details"""
        try:
            charity = CharityOrganization.objects.get(id=pk)
            
            # Only show verified charities to public
            if charity.status != 'verified' and (not request.user.is_authenticated or charity.user != request.user):
                return Response({
                    'success': False,
                    'message': 'Charity not found.'
                }, status=status.HTTP_404_NOT_FOUND)
            
            serializer = CharityDetailSerializer(charity)
            return Response({
                'success': True,
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        
        except CharityOrganization.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Charity not found.'
            }, status=status.HTTP_404_NOT_FOUND)