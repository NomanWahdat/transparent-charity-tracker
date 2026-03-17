"""
Donation Management Views
Location: donations/views.py
"""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db import transaction
from django.db.models import Sum, Avg
from donations.models import Donation
from campaigns.models import Campaign
from donations.serializers import (
    DonationSerializer, DonationCreateSerializer, DonationListSerializer,
    DonationPublicSerializer, DonationDetailSerializer
)


class DonationViewSet(viewsets.ViewSet):
    """
    Donation Management
    
    POST   /api/donations/create/           Create donation
    GET    /api/donations/my-donations/     Get my donations
    GET    /api/donations/campaign/{id}/    Get campaign donations
    GET    /api/donations/{id}/             Get donation details
    POST   /api/donations/{id}/verify/      Verify donation
    """
    
    permission_classes = [AllowAny]
    
    def get_permissions(self):
        """Set permissions"""
        if self.action in ['create', 'my_donations']:
            return [IsAuthenticated()]
        return [AllowAny()]
    
    @action(detail=False, methods=['post'])
    def create(self, request):
        """Create new donation"""
        serializer = DonationCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            donation = serializer.save()
            
            return Response({
                'success': True,
                'message': 'Donation created successfully!',
                'data': DonationSerializer(donation).data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def my_donations(self, request):
        """Get current user's donations"""
        donations = Donation.objects.filter(
            donor=request.user
        ).order_by('-created_at')
        
        serializer = DonationListSerializer(donations, many=True)
        
        return Response({
            'success': True,
            'count': donations.count(),
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def campaign_donations(self, request, campaign_id=None):
        """Get donations for a campaign"""
        try:
            campaign = Campaign.objects.get(id=campaign_id)
            
            donations = Donation.objects.filter(
                campaign=campaign,
                status='completed'
            ).order_by('-created_at')
            
            serializer = DonationPublicSerializer(donations, many=True)
            
            return Response({
                'success': True,
                'count': donations.count(),
                'total_amount': str(campaign.current_amount),
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        
        except Campaign.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Campaign not found.'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['get'])
    def detail(self, request, pk=None):
        """Get donation details"""
        try:
            donation = Donation.objects.get(id=pk)
            
            # Privacy: show full details only to donor or charity admin
            if donation.donor != request.user and donation.campaign.charity.user != request.user:
                # Show limited info for public
                serializer = DonationPublicSerializer(donation)
            else:
                serializer = DonationDetailSerializer(donation)
            
            return Response({
                'success': True,
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        
        except Donation.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Donation not found.'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verify donation (for blockchain)"""
        try:
            donation = Donation.objects.get(id=pk)
            
            # Only donation owner can verify
            if donation.donor != request.user:
                return Response({
                    'success': False,
                    'message': 'You can only verify your own donations.'
                }, status=status.HTTP_403_FORBIDDEN)
            
            with transaction.atomic():
                donation.on_blockchain = True
                donation.save()
            
            return Response({
                'success': True,
                'message': 'Donation verified on blockchain!',
                'data': DonationSerializer(donation).data
            }, status=status.HTTP_200_OK)
        
        except Donation.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Donation not found.'
            }, status=status.HTTP_404_NOT_FOUND)


class DonationStatsViewSet(viewsets.ViewSet):
    """
    Donation Statistics
    
    GET /api/donations/stats/total/       Total donations in platform
    GET /api/donations/stats/by-campaign/ Donations by campaign
    GET /api/donations/stats/top-donors/  Top donors
    """
    
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['get'])
    def total(self, request):
        """Get total platform statistics"""
        completed_donations = Donation.objects.filter(status='completed')
        
        total_amount = completed_donations.aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        avg_amount = completed_donations.aggregate(
            avg=Avg('amount')
        )['avg'] or 0
        
        largest = completed_donations.order_by('-amount').first()
        largest_amount = largest.amount if largest else 0
        
        stats = {
            'total_donations': completed_donations.count(),
            'total_amount': str(total_amount),
            'average_donation': str(avg_amount),
            'largest_donation': str(largest_amount)
        }
        
        return Response({
            'success': True,
            'data': stats
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def top_donors(self, request):
        """Get top donors"""
        top_donors = Donation.objects.filter(
            status='completed'
        ).values('donor__username').annotate(
            total_donated=Sum('amount')
        ).order_by('-total_donated')[:10]
        
        return Response({
            'success': True,
            'data': list(top_donors)
        }, status=status.HTTP_200_OK)