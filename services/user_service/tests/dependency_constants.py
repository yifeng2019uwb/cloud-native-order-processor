"""
Dependency constants for user_service unit tests
"""

# Patch paths (controllers import locally)
PATCH_GET_REQUEST_ID = 'controllers.auth.profile.get_request_id_from_request'
PATCH_VALIDATE_EMAIL_UNIQUENESS = 'controllers.auth.profile.validate_email_uniqueness'
PATCH_VALIDATE_AGE_REQUIREMENTS = 'controllers.auth.profile.validate_age_requirements'
PATCH_USER_PROFILE_RESPONSE = 'controllers.auth.profile.UserProfileResponse'
PATCH_VALIDATE_USER_PERMISSIONS = 'controllers.portfolio.asset_balance_controller.validate_user_permissions'
