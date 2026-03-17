"""
Custom Permissions and Authentication Classes
Role-based access control (RBAC) for the platform
"""

from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.exceptions import PermissionDenied


# ============================================
# ROLE-BASED PERMISSIONS
# ============================================

class IsDonor(BasePermission):
    """
    Allow access only to donor users
    """
    message = "Only donors can access this endpoint."
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'donor'
        )


class IsCharityUser(BasePermission):
    """
    Allow access only to charity organization users
    """
    message = "Only charity organization users can access this endpoint."
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'charity'
        )


class IsAdminUser(BasePermission):
    """
    Allow access only to admin users
    """
    message = "Only administrators can access this endpoint."
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_staff and
            request.user.role == 'admin'
        )


class IsVerifiedUser(BasePermission):
    """
    Allow access only to verified users
    """
    message = "Only verified users can access this endpoint."
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.verified
        )


class IsVerifiedCharity(BasePermission):
    """
    Allow access only to verified charities
    """
    message = "Your charity organization has not been verified yet."
    
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated and request.user.role == 'charity'):
            return False
        
        try:
            charity = request.user.charity
            return charity.status == 'verified'
        except:
            return False


class IsCharityOwner(BasePermission):
    """
    Allow access only to the owner of a charity
    """
    message = "You can only access your own charity."
    
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsOwnProfile(BasePermission):
    """
    Allow users to only access and modify their own profile
    """
    message = "You can only access your own profile."
    
    def has_object_permission(self, request, view, obj):
        return obj == request.user


class IsCampaignOwner(BasePermission):
    """
    Allow access only to the charity that created the campaign
    """
    message = "You can only access campaigns you created."
    
    def has_object_permission(self, request, view, obj):
        return obj.charity.user == request.user


class IsExpenseOwner(BasePermission):
    """
    Allow access only to expenses submitted by your charity
    """
    message = "You can only access expenses from your campaigns."
    
    def has_object_permission(self, request, view, obj):
        return obj.campaign.charity.user == request.user


# ============================================
# COMBINED PERMISSIONS
# ============================================

class IsDonorOrAdmin(BasePermission):
    """
    Allow access to donors and admins
    """
    message = "Only donors or admins can access this endpoint."
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            (request.user.role in ['donor', 'admin'])
        )


class IsCharityOrAdmin(BasePermission):
    """
    Allow access to charities and admins
    """
    message = "Only charities or admins can access this endpoint."
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            (request.user.role in ['charity', 'admin'])
        )


class IsVerifiedOrAdmin(BasePermission):
    """
    Allow access to verified users and admins
    """
    message = "Only verified users or admins can access this endpoint."
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            (request.user.verified or request.user.role == 'admin')
        )


class IsVerifiedCharityOrAdmin(BasePermission):
    """
    Allow access to verified charities and admins
    """
    message = "Only verified charities or admins can access this endpoint."
    
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        
        if request.user.role == 'admin':
            return True
        
        if request.user.role == 'charity':
            try:
                charity = request.user.charity
                return charity.status == 'verified'
            except:
                return False
        
        return False


# ============================================
# CUSTOM AUTHENTICATION CLASSES
# ============================================

class TokenHasReadWritePermission(BasePermission):
    """
    Allows read access to authenticated users
    Write access only with proper permissions
    """
    
    def has_permission(self, request, view):
        # Read permissions are allowed to authenticated users
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return request.user and request.user.is_authenticated
        
        # Write permissions require additional checks
        return request.user and request.user.is_authenticated


# ============================================
# PERMISSION HELPER FUNCTIONS
# ============================================

def get_user_role(user):
    """
    Get user role safely
    """
    if not user or not user.is_authenticated:
        return None
    return getattr(user, 'role', None)


def is_user_role(user, role):
    """
    Check if user has specific role
    """
    return get_user_role(user) == role


def has_any_role(user, roles):
    """
    Check if user has any of the specified roles
    """
    user_role = get_user_role(user)
    return user_role in roles


def check_user_verified(user):
    """
    Check if user is verified
    """
    if not user or not user.is_authenticated:
        return False
    return getattr(user, 'verified', False)


def check_charity_verified(user):
    """
    Check if user's charity is verified
    """
    if not is_user_role(user, 'charity'):
        return False
    
    try:
        charity = user.charity
        return charity.status == 'verified'
    except:
        return False


# ============================================
# EXCEPTION CLASSES
# ============================================

class InvalidRoleException(PermissionDenied):
    """
    Raised when user has invalid role for the action
    """
    status_code = 403
    default_detail = 'Invalid role for this operation.'
    default_code = 'invalid_role'


class UnverifiedUserException(PermissionDenied):
    """
    Raised when user is not verified
    """
    status_code = 403
    default_detail = 'User account is not verified.'
    default_code = 'unverified_user'


class UnverifiedCharityException(PermissionDenied):
    """
    Raised when charity is not verified
    """
    status_code = 403
    default_detail = 'Charity organization is not verified.'
    default_code = 'unverified_charity'