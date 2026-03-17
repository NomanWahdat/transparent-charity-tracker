"""
Main URL Configuration - charity_tracker/urls.py
Complete API with root documentation and all endpoints
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


# ============================================
# ROOT API VIEW - API DOCUMENTATION
# ============================================

class RootAPIView(APIView):
    """
    Root API endpoint - Shows all available endpoints
    Access at: http://localhost:8000/
    """
    
    def get(self, request):
        """Return comprehensive API documentation"""
        return Response({
            'success': True,
            'message': 'Welcome to Transparent Charity Tracker API',
            'version': '1.0.0',
            'status': 'Active',
            'documentation': {
                'admin_panel': 'http://127.0.0.1:8000/admin/',
                'api_base': 'http://127.0.0.1:8000/api/',
                'swagger_docs': 'http://127.0.0.1:8000/api/docs/',
                'redoc_docs': 'http://127.0.0.1:8000/api/redoc/',
            },
            
            'authentication_endpoints': {
                'register': 'POST /api/auth/register/',
                'login': 'POST /api/auth/login/',
                'refresh_token': 'POST /api/auth/refresh/',
                'profile': 'GET /api/auth/profile/profile/',
                'update_profile': 'PUT /api/auth/profile/update/',
                'change_password': 'POST /api/auth/profile/change_password/',
                'logout': 'POST /api/auth/logout/logout/',
            },
            
            'charity_endpoints': {
                'register_charity': 'POST /api/charities/register/',
                'my_charity': 'GET /api/charities/my_charity/',
                'update_charity': 'PUT /api/charities/update/',
                'list_charities': 'GET /api/charities/list/',
                'charity_detail': 'GET /api/charities/{id}/',
            },
            
            'admin_endpoints': {
                'pending_charities': 'GET /api/admin/charities/verify/pending/',
                'charity_detail': 'GET /api/admin/charities/verify/{id}/',
                'verify_charity': 'POST /api/admin/charities/verify/{id}/verify/',
                'reject_charity': 'POST /api/admin/charities/verify/{id}/reject/',
                'suspend_charity': 'POST /api/admin/charities/verify/{id}/suspend/',
                'list_users': 'GET /api/admin/users/',
                'user_detail': 'GET /api/admin/users/{id}/',
                'verify_user': 'POST /api/admin/users/{id}/verify/',
                'delete_user': 'DELETE /api/admin/users/{id}/',
            },
            
            'campaign_endpoints': {
                'create_campaign': 'POST /api/campaigns/create/',
                'list_campaigns': 'GET /api/campaigns/list/',
                'campaign_detail': 'GET /api/campaigns/{id}/',
                'my_campaigns': 'GET /api/campaigns/my-campaigns/',
                'update_campaign': 'PUT /api/campaigns/{id}/',
                'delete_campaign': 'DELETE /api/campaigns/{id}/',
                'launch_campaign': 'POST /api/campaigns/{id}/launch/',
                'pause_campaign': 'POST /api/campaigns/{id}/pause/',
                'complete_campaign': 'POST /api/campaigns/{id}/complete/',
                'fail_campaign': 'POST /api/campaigns/{id}/fail/',
                'campaign_summary': 'GET /api/campaigns/{id}/summary/',
                'charity_campaigns': 'GET /api/campaigns/charity/{id}/',
                'trending_campaigns': 'GET /api/campaigns/stats/trending/',
                'recent_campaigns': 'GET /api/campaigns/stats/recent/',
                'ending_soon': 'GET /api/campaigns/stats/ending-soon/',
                'by_location': 'GET /api/campaigns/stats/by-location/',
            },
            
            'donation_endpoints': {
                'create_donation': 'POST /api/donations/create/',
                'my_donations': 'GET /api/donations/my-donations/',
                'campaign_donations': 'GET /api/donations/campaign/{id}/',
                'donation_detail': 'GET /api/donations/{id}/',
                'verify_donation': 'POST /api/donations/{id}/verify/',
                'total_stats': 'GET /api/donations/stats/total/',
                'campaign_stats': 'GET /api/donations/stats/by-campaign/',
                'top_donors': 'GET /api/donations/stats/top-donors/',
            },
            
            'quick_start': {
                'step_1': 'Register user: POST /api/auth/register/',
                'step_2': 'Login to get tokens: POST /api/auth/login/',
                'step_3': 'Use access_token in header: Authorization: Bearer {access_token}',
                'step_4': 'Access protected endpoints',
                'step_5': 'When token expires, refresh: POST /api/auth/refresh/',
            },
            
            'authentication_notes': [
                'Content-Type: application/json (required for all requests)',
                'Authorization: Bearer {access_token} (required for protected endpoints)',
                'Access tokens expire after 1 hour',
                'Refresh tokens expire after 7 days',
                'Use refresh token to get new access token without re-logging in',
            ],
            
            'role_based_access': {
                'donor': 'Can donate, view campaigns, track donations',
                'charity': 'Can create campaigns, submit expenses, view donations',
                'admin': 'Can verify charities, manage users, view all data',
            },
            
            'http_status_codes': {
                '200': 'Success - GET/PUT requests',
                '201': 'Created - POST requests that create new resources',
                '400': 'Bad Request - Invalid data or validation error',
                '401': 'Unauthorized - Missing or invalid token',
                '403': 'Forbidden - User does not have permission',
                '404': 'Not Found - Resource does not exist',
                '500': 'Server Error - Something went wrong',
            },
            
            'useful_links': [
                'Full API Documentation: See RESPONSE_2_IMPLEMENTATION_GUIDE.md',
                'Campaign Guide: See RESPONSE_3_SEPARATED_FILES_GUIDE.md',
                'Setup Guide: See RESPONSE_1_COMPLETE_SETUP_GUIDE.md',
                'Postman Collection: Import JSON from outputs folder',
            ],
            
            'features': [
                'User authentication with JWT tokens',
                'Role-based access control (Donor, Charity, Admin)',
                'Charity verification workflow',
                'Campaign management system',
                'Donation tracking and transparency',
                'Public campaign listing',
                'Donation statistics and analytics',
                'Blockchain-ready donation records',
                'Anonymous donation support',
            ],
            
            'coming_soon': [
                'Expense tracking system (Response 4)',
                'Price verification and fraud detection (Response 4)',
                'Receipt OCR scanning (Response 4)',
                'Public transparency dashboard (Response 5)',
                'Impact reporting (Response 5)',
                'Blockchain integration (Response 6)',
                'AI fraud detection (Response 6)',
                'React frontend (Response 7)',
                'Mobile app (Future)',
            ],
            
            'support': {
                'email': 'support@transparentcharity.com',
                'documentation': 'http://127.0.0.1:8000/api/docs/',
                'github': 'https://github.com/yourusername/transparent-charity-tracker',
            }
        }, status=status.HTTP_200_OK)


# ============================================
# URL PATTERNS
# ============================================

urlpatterns = [
    # Root API Documentation
    path('', RootAPIView.as_view(), name='api-root'),
    
    # Django Admin
    path('admin/', admin.site.urls),
    
    # API Endpoints (Response 2 - Authentication & Users)
    path('api/auth/', include('users.urls')),
    
    # API Endpoints (Response 3 - Campaigns)
    path('api/campaigns/', include('campaigns.urls')),
    
    # API Endpoints (Response 3 - Donations)
    path('api/donations/', include('donations.urls')),
    
    # DRF Authentication (for browsable API)
    path('api-auth/', include('rest_framework.urls')),
]

# Serve media and static files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


# ============================================
# API DOCUMENTATION (Swagger & ReDoc)
# ============================================
# Uncomment below to enable Swagger/ReDoc documentation
# First install: pip install drf-yasg

try:
    from drf_yasg.views import get_schema_view
    from drf_yasg import openapi
    from rest_framework import permissions
    
    schema_view = get_schema_view(
        openapi.Info(
            title="Transparent Charity Tracker API",
            default_version='v1',
            description="""
            Complete API for transparent donation tracking and charity verification.
            
            Features:
            - User authentication with JWT tokens
            - Role-based access control (Donor, Charity, Admin)
            - Campaign management (create, launch, track)
            - Donation processing and tracking
            - Charity verification workflow
            - Public campaign listing
            - Donation statistics
            
            Authentication:
            1. Register: POST /api/auth/register/
            2. Login: POST /api/auth/login/
            3. Use access_token in Authorization header
            4. Refresh token: POST /api/auth/refresh/
            
            Roles:
            - Donor: Can donate and track donations
            - Charity: Can create campaigns and track spending
            - Admin: Can verify charities and manage users
            """,
            terms_of_service="https://www.transparentcharity.com/terms/",
            contact=openapi.Contact(
                email="support@transparentcharity.com",
                url="https://www.transparentcharity.com"
            ),
            license=openapi.License(name="MIT License"),
        ),
        public=True,
        permission_classes=[permissions.AllowAny],
    )
    
    urlpatterns += [
        # Swagger UI Documentation
        re_path(
            r'^api/docs/$',
            schema_view.with_ui('swagger', cache_timeout=0),
            name='schema-swagger-ui'
        ),
        # ReDoc Documentation
        re_path(
            r'^api/redoc/$',
            schema_view.with_ui('redoc', cache_timeout=0),
            name='schema-redoc'
        ),
        # OpenAPI Schema (JSON)
        re_path(
            r'^api/schema/$',
            schema_view.without_ui(cache_timeout=0),
            name='schema-json'
        ),
    ]
    
except ImportError:
    # drf-yasg not installed, skip documentation endpoints
    print("Warning: drf-yasg not installed. API documentation unavailable.")
    print("Install with: pip install drf-yasg")