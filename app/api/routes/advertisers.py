"""
Advertiser (Ad Account) management API routes
"""

from fastapi import APIRouter, HTTPException, Query, Path
from typing import Optional
import logging
import uuid
from datetime import datetime

from app.models.advertiser import (
    AdvertiserCreateRequest,
    AdvertiserUpdateRequest,
    AdvertiserResponse,
    AdvertiserListResponse,
    AdvertiserValidationRequest,
    AdvertiserValidationResponse
)
from app.services.facebook_api import facebook_service, FacebookAPIError

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/validate", response_model=AdvertiserValidationResponse)
async def validate_advertiser(validation_request: AdvertiserValidationRequest):
    """
    Validate Facebook ad account existence and permissions
    
    This endpoint checks if a Facebook ad account exists and is accessible
    with the current API credentials. This is essential before creating
    campaigns as ad accounts cannot be created programmatically.
    """
    try:
        logger.info(f"Validating ad account: {validation_request.facebook_ad_account_id}")
        
        validation_response = await facebook_service.validate_ad_account(
            validation_request.facebook_ad_account_id
        )
        
        logger.info(f"Ad account validation result: {validation_response.is_valid}")
        return validation_response
        
    except FacebookAPIError as e:
        logger.error(f"Facebook API error during validation: {e.message}")
        return AdvertiserValidationResponse(
            facebook_ad_account_id=validation_request.facebook_ad_account_id,
            exists=False,
            is_valid=False,
            validation_errors=[f"Validation failed: {e.message}"]
        )
    except Exception as e:
        logger.error(f"Unexpected error during validation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during ad account validation"
        )


@router.post("/", response_model=AdvertiserResponse)
async def create_advertiser(advertiser_data: AdvertiserCreateRequest):
    """
    Register an existing Facebook ad account as an advertiser in our system
    
    Note: This does not create a new ad account in Facebook (not possible via API).
    Instead, it registers an existing ad account for use in our system.
    """
    try:
        logger.info(f"Registering advertiser: {advertiser_data.name}")
        
        # First validate the ad account exists and is accessible
        validation = await facebook_service.validate_ad_account(
            advertiser_data.facebook_ad_account_id
        )
        
        if not validation.exists:
            raise HTTPException(
                status_code=404,
                detail=f"Facebook ad account {advertiser_data.facebook_ad_account_id} not found"
            )
        
        if not validation.is_valid:
            raise HTTPException(
                status_code=400,
                detail=f"Facebook ad account is not valid: {', '.join(validation.validation_errors or [])}"
            )
        
        # In a real implementation, you would save this to your database
        # For this demo, we'll return a mock response
        
        advertiser_response = AdvertiserResponse(
            id=str(uuid.uuid4()),
            name=advertiser_data.name,
            category=advertiser_data.category,
            status="ACTIVE",
            facebook_ad_account_id=advertiser_data.facebook_ad_account_id,
            business_id=advertiser_data.business_id,
            currency=validation.currency,
            timezone=validation.timezone,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            verification_status="verified",
            facebook_data={
                "account_name": validation.account_name,
                "account_status": validation.status,
                "permissions": validation.permissions
            }
        )
        
        logger.info(f"Advertiser registered successfully: {advertiser_response.id}")
        return advertiser_response
        
    except HTTPException:
        raise
    except FacebookAPIError as e:
        logger.error(f"Facebook API error: {e.message}")
        raise HTTPException(
            status_code=400,
            detail=f"Facebook API error: {e.message}"
        )
    except Exception as e:
        logger.error(f"Unexpected error creating advertiser: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while registering advertiser"
        )


@router.get("/", response_model=AdvertiserListResponse)
async def list_advertisers(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(25, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, description="Filter by status")
):
    """
    List registered advertisers with optional filtering and pagination
    """
    try:
        # In a real implementation, you would query your database here
        # For this demo, we'll return mock data
        
        advertisers = []
        
        # Mock advertiser data
        mock_advertiser = AdvertiserResponse(
            id=str(uuid.uuid4()),
            name="Demo Advertiser",
            category="ECOMMERCE",
            status="ACTIVE",
            facebook_ad_account_id="act_123456789",
            currency="USD",
            timezone="America/New_York",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            verification_status="verified"
        )
        
        if not status or mock_advertiser.status.lower() == status.lower():
            advertisers.append(mock_advertiser)
        
        return AdvertiserListResponse(
            advertisers=advertisers,
            total=len(advertisers),
            page=page,
            page_size=page_size,
            has_next=False
        )
        
    except Exception as e:
        logger.error(f"Error listing advertisers: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while listing advertisers"
        )


@router.get("/{advertiser_id}", response_model=AdvertiserResponse)
async def get_advertiser(advertiser_id: str = Path(..., description="Advertiser ID")):
    """
    Get advertiser details by ID
    """
    try:
        # In a real implementation, you would query your database
        # For this demo, we'll return mock data
        
        advertiser = AdvertiserResponse(
            id=advertiser_id,
            name="Demo Advertiser",
            category="ECOMMERCE",
            status="ACTIVE",
            facebook_ad_account_id="act_123456789",
            currency="USD",
            timezone="America/New_York",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            verification_status="verified"
        )
        
        return advertiser
        
    except Exception as e:
        logger.error(f"Error getting advertiser: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while getting advertiser"
        )


@router.put("/{advertiser_id}", response_model=AdvertiserResponse)
async def update_advertiser(
    advertiser_id: str = Path(..., description="Advertiser ID"),
    update_data: AdvertiserUpdateRequest = ...
):
    """
    Update advertiser information
    
    Note: This only updates information in our system.
    Facebook ad account details cannot be modified via API.
    """
    try:
        # In a real implementation, you would update your database
        # For this demo, we'll return updated mock data
        
        advertiser = AdvertiserResponse(
            id=advertiser_id,
            name=update_data.name or "Updated Advertiser Name",
            category=update_data.category or "ECOMMERCE",
            status=update_data.status or "ACTIVE",
            facebook_ad_account_id="act_123456789",
            currency="USD",
            timezone="America/New_York",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            verification_status="verified"
        )
        
        logger.info(f"Advertiser updated successfully: {advertiser_id}")
        return advertiser
        
    except Exception as e:
        logger.error(f"Error updating advertiser: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while updating advertiser"
        )


@router.delete("/{advertiser_id}")
async def delete_advertiser(advertiser_id: str = Path(..., description="Advertiser ID")):
    """
    Delete advertiser from our system
    
    Note: This only removes the advertiser from our system.
    The Facebook ad account remains unchanged.
    """
    try:
        # In a real implementation, you would delete from your database
        # and potentially check for active campaigns first
        
        logger.info(f"Advertiser deleted successfully: {advertiser_id}")
        return {
            "message": "Advertiser deleted successfully",
            "advertiser_id": advertiser_id,
            "note": "Facebook ad account remains unchanged"
        }
        
    except Exception as e:
        logger.error(f"Error deleting advertiser: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while deleting advertiser"
        )


@router.get("/{advertiser_id}/campaigns")
async def get_advertiser_campaigns(
    advertiser_id: str = Path(..., description="Advertiser ID"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(25, ge=1, le=100, description="Items per page")
):
    """
    Get all campaigns for a specific advertiser
    """
    try:
        # In a real implementation, you would:
        # 1. Get advertiser details from database
        # 2. Use the Facebook ad account ID to fetch campaigns
        # 3. Return paginated results
        
        # For this demo, we'll return empty results
        return {
            "campaigns": [],
            "total": 0,
            "page": page,
            "page_size": page_size,
            "has_next": False,
            "advertiser_id": advertiser_id
        }
        
    except Exception as e:
        logger.error(f"Error getting advertiser campaigns: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while getting advertiser campaigns"
        )
