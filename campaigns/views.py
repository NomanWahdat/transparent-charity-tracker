"""
Campaign Management Views
Campaign CRUD, status management, and public listing
"""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from django.db import transaction
from campaigns.models import Campaign
from utils.permissions import IsCharityUser, IsCharityOwner, IsVerifiedCharity
from .serializers import (
    CampaignSerializer, CampaignCreateSerializer, CampaignUpdateSerializer,
    CampaignStatusChangeSerializer, CampaignDonationSummarySerializer,
    CampaignListSerializer, CampaignDetailedSerializer
)


class CampaignViewSet(viewsets.ViewSet):
    """
    Campaign Management
    
    POST   /api/campaigns/create/              Create new campaign
    GET    /api/campaigns/list/                List all campaigns (public)
    GET    /api/campaigns/{id}/                Get campaign details
    GET    /api/campaigns/my-campaigns/        Get my campaigns (charity)
    PUT    /api/campaigns/{id}/                Update campaign
    DELETE /api/campaigns/{id}/                Delete campaign
    POST   /api/campaigns/{id}/launch/         Launch campaign (active)
    POST   /api/campaigns/{id}/pause/          Pause campaign
    POST   /api/campaigns/{id}/complete/       Complete campaign
    POST   /api/campaigns/{id}/fail/           Mark as failed
    GET    /api/campaigns/{id}/summary/        Get campaign summary
    GET    /api/campaigns/charity/{charity_id}/ Get charity's campaigns
    """
    
    permission_classes = [AllowAny]
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['create', 'update_campaign', 'delete_campaign', 'launch', 'pause', 'complete', 'fail']:
            return [IsAuthenticated(), IsCharityUser()]
        elif self.action == 'my_campaigns':
            return [IsAuthenticated(), IsCharityUser()]
        return [AllowAny()]
    
    @action(detail=False, methods=['post'])
    def create(self, request):
        """Create new campaign"""
        serializer = CampaignCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            campaign = serializer.save()
            return Response({
                'success': True,
                'message': 'Campaign created in draft status!',
                'data': CampaignSerializer(campaign).data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def list(self, request):
        """List all active campaigns (public)"""
        campaigns = Campaign.objects.filter(
            status='active'
        ).order_by('-created_at')
        
        # Pagination
        page = request.query_params.get('page', 1)
        per_page = request.query_params.get('per_page', 10)
        
        try:
            start = (int(page) - 1) * int(per_page)
            end = start + int(per_page)
            campaigns = campaigns[start:end]
        except:
            pass
        
        serializer = CampaignListSerializer(campaigns, many=True)
        
        return Response({
            'success': True,
            'count': len(campaigns),
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'])
    def detail(self, request, pk=None):
        """Get campaign details"""
        try:
            campaign = Campaign.objects.get(id=pk)
            
            # Don't show draft campaigns to public
            if campaign.status == 'draft' and campaign.charity.user != request.user:
                return Response({
                    'success': False,
                    'message': 'Campaign not found.'
                }, status=status.HTTP_404_NOT_FOUND)
            
            serializer = CampaignDetailedSerializer(campaign)
            
            return Response({
                'success': True,
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        
        except Campaign.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Campaign not found.'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def my_campaigns(self, request):
        """Get current charity's campaigns"""
        try:
            charity = request.user.charity
            campaigns = Campaign.objects.filter(
                charity=charity
            ).order_by('-created_at')
            
            serializer = CampaignListSerializer(campaigns, many=True)
            
            return Response({
                'success': True,
                'count': campaigns.count(),
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        
        except:
            return Response({
                'success': False,
                'message': 'You do not have a verified charity.'
            }, status=status.HTTP_403_FORBIDDEN)
    
    @action(detail=True, methods=['put'])
    def update_campaign(self, request, pk=None):
        """Update campaign (only draft campaigns)"""
        try:
            campaign = Campaign.objects.get(id=pk)
            
            # Check ownership
            if campaign.charity.user != request.user:
                return Response({
                    'success': False,
                    'message': 'You can only update your own campaigns.'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Only draft campaigns can be updated
            if campaign.status != 'draft':
                return Response({
                    'success': False,
                    'message': f'Cannot update {campaign.status} campaigns.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = CampaignUpdateSerializer(
                campaign,
                data=request.data,
                partial=True
            )
            
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'success': True,
                    'message': 'Campaign updated successfully!',
                    'data': CampaignSerializer(campaign).data
                }, status=status.HTTP_200_OK)
            
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Campaign.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Campaign not found.'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['delete'])
    def delete_campaign(self, request, pk=None):
        """Delete campaign (only draft campaigns)"""
        try:
            campaign = Campaign.objects.get(id=pk)
            
            # Check ownership
            if campaign.charity.user != request.user:
                return Response({
                    'success': False,
                    'message': 'You can only delete your own campaigns.'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Only draft campaigns can be deleted
            if campaign.status != 'draft':
                return Response({
                    'success': False,
                    'message': f'Cannot delete {campaign.status} campaigns.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            title = campaign.title
            campaign.delete()
            
            return Response({
                'success': True,
                'message': f'Campaign "{title}" deleted successfully!'
            }, status=status.HTTP_200_OK)
        
        except Campaign.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Campaign not found.'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def launch(self, request, pk=None):
        """Launch campaign (draft -> active)"""
        try:
            campaign = Campaign.objects.get(id=pk)
            
            # Check ownership
            if campaign.charity.user != request.user:
                return Response({
                    'success': False,
                    'message': 'You can only launch your own campaigns.'
                }, status=status.HTTP_403_FORBIDDEN)
            
            if campaign.status != 'draft':
                return Response({
                    'success': False,
                    'message': f'Campaign is already {campaign.status}.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate campaign
            if not campaign.title or not campaign.goal_amount:
                return Response({
                    'success': False,
                    'message': 'Campaign must have title and goal amount.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            with transaction.atomic():
                campaign.status = 'active'
                campaign.start_date = timezone.now()
                campaign.save()
            
            return Response({
                'success': True,
                'message': 'Campaign launched successfully! It is now accepting donations.',
                'data': CampaignSerializer(campaign).data
            }, status=status.HTTP_200_OK)
        
        except Campaign.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Campaign not found.'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        """Pause campaign (active -> paused)"""
        try:
            campaign = Campaign.objects.get(id=pk)
            
            # Check ownership
            if campaign.charity.user != request.user:
                return Response({
                    'success': False,
                    'message': 'You can only pause your own campaigns.'
                }, status=status.HTTP_403_FORBIDDEN)
            
            if campaign.status != 'active':
                return Response({
                    'success': False,
                    'message': f'Cannot pause {campaign.status} campaign.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            with transaction.atomic():
                campaign.status = 'paused'
                campaign.save()
            
            return Response({
                'success': True,
                'message': 'Campaign paused. It will not accept new donations.',
                'data': CampaignSerializer(campaign).data
            }, status=status.HTTP_200_OK)
        
        except Campaign.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Campaign not found.'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Complete campaign (active/paused -> completed)"""
        try:
            campaign = Campaign.objects.get(id=pk)
            
            # Check ownership
            if campaign.charity.user != request.user:
                return Response({
                    'success': False,
                    'message': 'You can only complete your own campaigns.'
                }, status=status.HTTP_403_FORBIDDEN)
            
            if campaign.status not in ['active', 'paused']:
                return Response({
                    'success': False,
                    'message': f'Cannot complete {campaign.status} campaign.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            with transaction.atomic():
                campaign.status = 'completed'
                campaign.save()
            
            return Response({
                'success': True,
                'message': 'Campaign completed successfully!',
                'data': CampaignSerializer(campaign).data
            }, status=status.HTTP_200_OK)
        
        except Campaign.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Campaign not found.'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def fail(self, request, pk=None):
        """Mark campaign as failed"""
        try:
            campaign = Campaign.objects.get(id=pk)
            
            # Check ownership
            if campaign.charity.user != request.user:
                return Response({
                    'success': False,
                    'message': 'You can only mark your own campaigns as failed.'
                }, status=status.HTTP_403_FORBIDDEN)
            
            if campaign.status == 'completed':
                return Response({
                    'success': False,
                    'message': 'Completed campaigns cannot be marked as failed.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            with transaction.atomic():
                campaign.status = 'failed'
                campaign.save()
            
            return Response({
                'success': True,
                'message': 'Campaign marked as failed.',
                'data': CampaignSerializer(campaign).data
            }, status=status.HTTP_200_OK)
        
        except Campaign.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Campaign not found.'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        """Get campaign funding summary"""
        try:
            campaign = Campaign.objects.get(id=pk)
            serializer = CampaignDonationSummarySerializer(campaign)
            
            return Response({
                'success': True,
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        
        except Campaign.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Campaign not found.'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def charity_campaigns(self, request, charity_id=None):
        """Get campaigns by charity ID"""
        try:
            campaigns = Campaign.objects.filter(
                charity_id=charity_id,
                status='active'
            ).order_by('-created_at')
            
            serializer = CampaignListSerializer(campaigns, many=True)
            
            return Response({
                'success': True,
                'count': campaigns.count(),
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        
        except:
            return Response({
                'success': False,
                'message': 'Charity not found.'
            }, status=status.HTTP_404_NOT_FOUND)


class CampaignStatsViewSet(viewsets.ViewSet):
    """
    Campaign Statistics
    
    GET /api/campaigns/stats/trending/    Get trending campaigns
    GET /api/campaigns/stats/recent/      Get recently launched
    GET /api/campaigns/stats/ending-soon/ Get ending soon
    GET /api/campaigns/stats/by-category/ Get by category
    """
    
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['get'])
    def trending(self, request):
        """Get trending campaigns (most donors)"""
        campaigns = Campaign.objects.filter(
            status='active'
        ).order_by('-donor_count')[:10]
        
        serializer = CampaignListSerializer(campaigns, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recently launched campaigns"""
        campaigns = Campaign.objects.filter(
            status='active'
        ).order_by('-start_date')[:10]
        
        serializer = CampaignListSerializer(campaigns, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def ending_soon(self, request):
        """Get campaigns ending soon"""
        now = timezone.now()
        campaigns = Campaign.objects.filter(
            status='active',
            end_date__lte=now + timezone.timedelta(days=7)
        ).order_by('end_date')[:10]
        
        serializer = CampaignListSerializer(campaigns, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def by_location(self, request):
        """Get campaigns by location"""
        location = request.query_params.get('location', '')
        
        if not location:
            return Response({
                'success': False,
                'message': 'Location parameter required.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        campaigns = Campaign.objects.filter(
            status='active',
            beneficiary_location__icontains=location
        ).order_by('-created_at')
        
        serializer = CampaignListSerializer(campaigns, many=True)
        
        return Response({
            'success': True,
            'count': campaigns.count(),
            'data': serializer.data
        }, status=status.HTTP_200_OK)