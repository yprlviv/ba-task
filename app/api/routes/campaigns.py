"""
Campaign management API routes
"""

from fastapi import APIRouter, HTTPException, Query, Path
from typing import Optional
import logging
import uuid
from datetime import datetime

from app.models.campaign import (
    CampaignCreateRequest, 
    CampaignUpdateRequest, 
    CampaignResponse, 
    CampaignListResponse,
    CampaignSyncStatus
)
from app.services.facebook_api import facebook_service, FacebookAPIError, RateLimitExceeded

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=CampaignResponse)
async def create_campaign(campaign_data: CampaignCreateRequest):
    """
    Create a new campaign in both our system and Facebook Ads Manager
    
    This endpoint:
    1. Validates the request data
    2. Creates the campaign in Facebook Ads Manager
    3. Stores the campaign data in our system
    4. Returns the created campaign details
    """
    try:
        logger.info(f"Creating campaign: {campaign_data.name}")
        
        # Validate ad account first
        validation = await facebook_service.validate_ad_account(campaign_data.ad_account_id)
        if not validation.is_valid:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid ad account: {', '.join(validation.validation_errors or [])}"
            )
        
        # Create campaign in Facebook
        facebook_response = await facebook_service.create_campaign(campaign_data)
        facebook_campaign_id = facebook_response.get('id')
        
        # In a real implementation, you would save to database here
        # For this demo, we'll return a mock response with the Facebook data
        
        campaign_response = CampaignResponse(
            id=str(uuid.uuid4()),
            name=campaign_data.name,
            objective=campaign_data.objective,
            status="PAUSED",  # Facebook campaigns start paused
            start_time=campaign_data.start_time,
            stop_time=campaign_data.stop_time,
            budget_type=campaign_data.budget_type,
            budget_amount=campaign_data.budget_amount,
            ad_account_id=campaign_data.ad_account_id,
            facebook_campaign_id=facebook_campaign_id,
            frequency_cap=campaign_data.frequency_cap,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            sync_status="synced",
            last_sync_at=datetime.utcnow(),
            facebook_data=facebook_response
        )
        
        logger.info(f"Campaign created successfully: {facebook_campaign_id}")
        return campaign_response
        
    except RateLimitExceeded:
        raise HTTPException(
            status_code=429,
            detail="Facebook API rate limit exceeded. Please try again later."
        )
    except FacebookAPIError as e:
        logger.error(f"Facebook API error: {e.message}")
        raise HTTPException(
            status_code=400,
            detail=f"Facebook API error: {e.message}"
        )
    except Exception as e:
        logger.error(f"Unexpected error creating campaign: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while creating campaign"
        )


@router.get("/", response_model=CampaignListResponse)
async def list_campaigns(
    ad_account_id: Optional[str] = Query(None, description="Filter by ad account ID"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(25, ge=1, le=100, description="Items per page")
):
    """
    List campaigns with optional filtering and pagination
    """
    try:
        # In a real implementation, you would query your database here
        # For this demo, we'll return mock data
        
        campaigns = []
        
        # If ad_account_id is provided, fetch from Facebook
        if ad_account_id:
            facebook_response = await facebook_service.list_campaigns(
                ad_account_id, 
                limit=page_size
            )
            
            # Convert Facebook campaigns to our format
            for fb_campaign in facebook_response.get('data', []):
                campaign = CampaignResponse(
                    id=str(uuid.uuid4()),
                    name=fb_campaign.get('name', ''),
                    objective=fb_campaign.get('objective', 'OUTCOME_TRAFFIC'),
                    status=fb_campaign.get('status', 'PAUSED'),
                    start_time=datetime.fromisoformat(fb_campaign.get('start_time', '').replace('Z', '+00:00')),
                    stop_time=datetime.fromisoformat(fb_campaign.get('stop_time', '').replace('Z', '+00:00')) if fb_campaign.get('stop_time') else None,
                    budget_type="daily_budget" if fb_campaign.get('daily_budget') else "lifetime_budget",
                    budget_amount=int(fb_campaign.get('daily_budget', fb_campaign.get('lifetime_budget', 0))),
                    ad_account_id=ad_account_id,
                    facebook_campaign_id=fb_campaign.get('id'),
                    created_at=datetime.fromisoformat(fb_campaign.get('created_time', '').replace('Z', '+00:00')),
                    updated_at=datetime.fromisoformat(fb_campaign.get('updated_time', '').replace('Z', '+00:00')),
                    sync_status="synced",
                    last_sync_at=datetime.utcnow(),
                    facebook_data=fb_campaign
                )
                campaigns.append(campaign)
        
        return CampaignListResponse(
            campaigns=campaigns,
            total=len(campaigns),
            page=page,
            page_size=page_size,
            has_next=False
        )
        
    except FacebookAPIError as e:
        logger.error(f"Facebook API error: {e.message}")
        raise HTTPException(
            status_code=400,
            detail=f"Facebook API error: {e.message}"
        )
    except Exception as e:
        logger.error(f"Error listing campaigns: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while listing campaigns"
        )


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(campaign_id: str = Path(..., description="Campaign ID")):
    """
    Get campaign details by ID
    """
    try:
        # In a real implementation, you would first check your database
        # For this demo, we'll assume the campaign_id is a Facebook campaign ID
        
        facebook_response = await facebook_service.get_campaign(campaign_id)
        
        campaign = CampaignResponse(
            id=str(uuid.uuid4()),
            name=facebook_response.get('name', ''),
            objective=facebook_response.get('objective', 'OUTCOME_TRAFFIC'),
            status=facebook_response.get('status', 'PAUSED'),
            start_time=datetime.fromisoformat(facebook_response.get('start_time', '').replace('Z', '+00:00')),
            stop_time=datetime.fromisoformat(facebook_response.get('stop_time', '').replace('Z', '+00:00')) if facebook_response.get('stop_time') else None,
            budget_type="daily_budget" if facebook_response.get('daily_budget') else "lifetime_budget",
            budget_amount=int(facebook_response.get('daily_budget', facebook_response.get('lifetime_budget', 0))),
            ad_account_id="",  # Would be retrieved from database
            facebook_campaign_id=campaign_id,
            created_at=datetime.fromisoformat(facebook_response.get('created_time', '').replace('Z', '+00:00')),
            updated_at=datetime.fromisoformat(facebook_response.get('updated_time', '').replace('Z', '+00:00')),
            sync_status="synced",
            last_sync_at=datetime.utcnow(),
            facebook_data=facebook_response
        )
        
        return campaign
        
    except FacebookAPIError as e:
        if e.status_code == 404:
            raise HTTPException(status_code=404, detail="Campaign not found")
        logger.error(f"Facebook API error: {e.message}")
        raise HTTPException(
            status_code=400,
            detail=f"Facebook API error: {e.message}"
        )
    except Exception as e:
        logger.error(f"Error getting campaign: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while getting campaign"
        )


@router.put("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: str = Path(..., description="Campaign ID"),
    update_data: CampaignUpdateRequest = ...
):
    """
    Update campaign settings
    """
    try:
        # Prepare update data for Facebook API
        facebook_update_data = {}
        
        if update_data.name is not None:
            facebook_update_data['name'] = update_data.name
        if update_data.status is not None:
            facebook_update_data['status'] = update_data.status.value
        if update_data.start_time is not None:
            facebook_update_data['start_time'] = update_data.start_time.isoformat()
        if update_data.stop_time is not None:
            facebook_update_data['stop_time'] = update_data.stop_time.isoformat()
        if update_data.budget_amount is not None and update_data.budget_type is not None:
            facebook_update_data[update_data.budget_type.value] = update_data.budget_amount
        
        # Update in Facebook
        facebook_response = await facebook_service.update_campaign(campaign_id, facebook_update_data)
        
        # Get updated campaign details
        updated_campaign = await facebook_service.get_campaign(campaign_id)
        
        campaign = CampaignResponse(
            id=str(uuid.uuid4()),
            name=updated_campaign.get('name', ''),
            objective=updated_campaign.get('objective', 'OUTCOME_TRAFFIC'),
            status=updated_campaign.get('status', 'PAUSED'),
            start_time=datetime.fromisoformat(updated_campaign.get('start_time', '').replace('Z', '+00:00')),
            stop_time=datetime.fromisoformat(updated_campaign.get('stop_time', '').replace('Z', '+00:00')) if updated_campaign.get('stop_time') else None,
            budget_type="daily_budget" if updated_campaign.get('daily_budget') else "lifetime_budget",
            budget_amount=int(updated_campaign.get('daily_budget', updated_campaign.get('lifetime_budget', 0))),
            ad_account_id="",  # Would be retrieved from database
            facebook_campaign_id=campaign_id,
            created_at=datetime.fromisoformat(updated_campaign.get('created_time', '').replace('Z', '+00:00')),
            updated_at=datetime.utcnow(),
            sync_status="synced",
            last_sync_at=datetime.utcnow(),
            facebook_data=updated_campaign
        )
        
        logger.info(f"Campaign updated successfully: {campaign_id}")
        return campaign
        
    except FacebookAPIError as e:
        if e.status_code == 404:
            raise HTTPException(status_code=404, detail="Campaign not found")
        logger.error(f"Facebook API error: {e.message}")
        raise HTTPException(
            status_code=400,
            detail=f"Facebook API error: {e.message}"
        )
    except Exception as e:
        logger.error(f"Error updating campaign: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while updating campaign"
        )


@router.delete("/{campaign_id}")
async def delete_campaign(campaign_id: str = Path(..., description="Campaign ID")):
    """
    Delete campaign (sets status to DELETED in Facebook)
    """
    try:
        # Delete in Facebook (sets status to DELETED)
        await facebook_service.delete_campaign(campaign_id)
        
        # In a real implementation, you would also update your database
        
        logger.info(f"Campaign deleted successfully: {campaign_id}")
        return {"message": "Campaign deleted successfully", "campaign_id": campaign_id}
        
    except FacebookAPIError as e:
        if e.status_code == 404:
            raise HTTPException(status_code=404, detail="Campaign not found")
        logger.error(f"Facebook API error: {e.message}")
        raise HTTPException(
            status_code=400,
            detail=f"Facebook API error: {e.message}"
        )
    except Exception as e:
        logger.error(f"Error deleting campaign: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while deleting campaign"
        )


@router.get("/{campaign_id}/sync-status", response_model=CampaignSyncStatus)
async def get_campaign_sync_status(campaign_id: str = Path(..., description="Campaign ID")):
    """
    Get campaign synchronization status with Facebook
    """
    try:
        # Check if campaign exists in Facebook
        facebook_response = await facebook_service.get_campaign(campaign_id)
        
        return CampaignSyncStatus(
            campaign_id=campaign_id,
            facebook_campaign_id=campaign_id,
            sync_status="synced",
            last_sync_at=datetime.utcnow(),
            facebook_status=facebook_response.get('status')
        )
        
    except FacebookAPIError as e:
        if e.status_code == 404:
            return CampaignSyncStatus(
                campaign_id=campaign_id,
                facebook_campaign_id=None,
                sync_status="not_found",
                last_sync_at=datetime.utcnow(),
                sync_errors=["Campaign not found in Facebook"]
            )
        else:
            return CampaignSyncStatus(
                campaign_id=campaign_id,
                facebook_campaign_id=None,
                sync_status="error",
                last_sync_at=datetime.utcnow(),
                sync_errors=[f"Sync error: {e.message}"]
            )
    except Exception as e:
        logger.error(f"Error checking sync status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while checking sync status"
        )
