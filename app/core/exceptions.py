"""
Custom exception classes and error handling
"""

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class FacebookAdsIntegrationError(Exception):
    """Base exception for Facebook Ads Integration errors"""
    def __init__(self, message: str, error_code: Optional[str] = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class ValidationError(FacebookAdsIntegrationError):
    """Raised when request validation fails"""
    pass


class FacebookAPIError(FacebookAdsIntegrationError):
    """Raised when Facebook API returns an error"""
    def __init__(self, message: str, error_code: Optional[str] = None, status_code: Optional[int] = None):
        super().__init__(message, error_code)
        self.status_code = status_code


class RateLimitError(FacebookAPIError):
    """Raised when Facebook API rate limit is exceeded"""
    def __init__(self, message: str = "Facebook API rate limit exceeded", retry_after: Optional[int] = None):
        super().__init__(message, "RATE_LIMIT_EXCEEDED", 429)
        self.retry_after = retry_after


class AdAccountNotFoundError(FacebookAPIError):
    """Raised when Facebook ad account is not found"""
    def __init__(self, ad_account_id: str):
        message = f"Facebook ad account '{ad_account_id}' not found or not accessible"
        super().__init__(message, "AD_ACCOUNT_NOT_FOUND", 404)
        self.ad_account_id = ad_account_id


class CampaignNotFoundError(FacebookAPIError):
    """Raised when campaign is not found"""
    def __init__(self, campaign_id: str):
        message = f"Campaign '{campaign_id}' not found"
        super().__init__(message, "CAMPAIGN_NOT_FOUND", 404)
        self.campaign_id = campaign_id


class SynchronizationError(FacebookAdsIntegrationError):
    """Raised when synchronization between systems fails"""
    pass


class ConfigurationError(FacebookAdsIntegrationError):
    """Raised when configuration is invalid or missing"""
    pass


# Error response models
def create_error_response(
    error_code: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
    status_code: int = 400
) -> JSONResponse:
    """Create standardized error response"""
    
    error_response = {
        "error": {
            "code": error_code,
            "message": message,
            "timestamp": "2025-10-13T00:00:00Z"  # In real app, use datetime.utcnow()
        }
    }
    
    if details:
        error_response["error"]["details"] = details
    
    return JSONResponse(
        status_code=status_code,
        content=error_response
    )


# Exception handlers
async def facebook_api_error_handler(request: Request, exc: FacebookAPIError) -> JSONResponse:
    """Handle Facebook API errors"""
    logger.error(f"Facebook API error: {exc.message} (Code: {exc.error_code})")
    
    return create_error_response(
        error_code=exc.error_code or "FACEBOOK_API_ERROR",
        message=exc.message,
        status_code=exc.status_code or 400
    )


async def rate_limit_error_handler(request: Request, exc: RateLimitError) -> JSONResponse:
    """Handle rate limit errors"""
    logger.warning(f"Rate limit exceeded: {exc.message}")
    
    headers = {}
    if exc.retry_after:
        headers["Retry-After"] = str(exc.retry_after)
    
    response = create_error_response(
        error_code="RATE_LIMIT_EXCEEDED",
        message=exc.message,
        details={"retry_after": exc.retry_after} if exc.retry_after else None,
        status_code=429
    )
    
    # Add headers to response
    for key, value in headers.items():
        response.headers[key] = value
    
    return response


async def validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """Handle validation errors"""
    logger.warning(f"Validation error: {exc.message}")
    
    return create_error_response(
        error_code="VALIDATION_ERROR",
        message=exc.message,
        status_code=400
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions"""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    
    return create_error_response(
        error_code="INTERNAL_SERVER_ERROR",
        message="An unexpected error occurred. Please try again later.",
        status_code=500
    )


# Error mapping for common Facebook API errors
FACEBOOK_ERROR_MAPPING = {
    "100": "Invalid parameter",
    "190": "Invalid access token",
    "200": "Permission denied",
    "613": "Rate limit exceeded",
    "803": "Some of the aliases you requested do not exist",
    "1487742": "User request limit reached",
    "80004": "There have been too many calls to this ad-account",
}


def map_facebook_error(error_code: str, error_message: str) -> str:
    """Map Facebook error codes to user-friendly messages"""
    
    if error_code in FACEBOOK_ERROR_MAPPING:
        return FACEBOOK_ERROR_MAPPING[error_code]
    
    # Handle specific error patterns
    if "rate limit" in error_message.lower():
        return "API rate limit exceeded. Please wait before making more requests."
    
    if "access token" in error_message.lower():
        return "Invalid or expired access token. Please check your API credentials."
    
    if "permission" in error_message.lower():
        return "Insufficient permissions to perform this action."
    
    if "not found" in error_message.lower():
        return "The requested resource was not found."
    
    # Return original message if no mapping found
    return error_message
