"""
Campaign data models and schemas
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class CampaignObjective(str, Enum):
    """Facebook campaign objectives"""
    OUTCOME_AWARENESS = "OUTCOME_AWARENESS"
    OUTCOME_TRAFFIC = "OUTCOME_TRAFFIC"
    OUTCOME_ENGAGEMENT = "OUTCOME_ENGAGEMENT"
    OUTCOME_LEADS = "OUTCOME_LEADS"
    OUTCOME_APP_PROMOTION = "OUTCOME_APP_PROMOTION"
    OUTCOME_SALES = "OUTCOME_SALES"


class CampaignStatus(str, Enum):
    """Campaign status options"""
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    DELETED = "DELETED"
    ARCHIVED = "ARCHIVED"


class BudgetType(str, Enum):
    """Budget type options"""
    DAILY = "daily_budget"
    LIFETIME = "lifetime_budget"


class FrequencyCapSpec(BaseModel):
    """Frequency cap specification for ad sets"""
    event: str = "IMPRESSIONS"
    interval_days: int = Field(ge=1, le=90)
    max_frequency: int = Field(ge=1, le=100)


class CampaignCreateRequest(BaseModel):
    """Request model for creating a new campaign"""
    name: str = Field(..., min_length=1, max_length=400)
    objective: CampaignObjective
    start_time: datetime
    stop_time: Optional[datetime] = None
    budget_type: BudgetType = BudgetType.DAILY
    budget_amount: int = Field(..., gt=0, description="Budget in cents")
    ad_account_id: str = Field(..., description="Facebook ad account ID")
    frequency_cap: Optional[FrequencyCapSpec] = None
    timezone: Optional[str] = Field(None, description="Will use ad account timezone if not specified")
    
    @validator('stop_time')
    def validate_stop_time(cls, v, values):
        if v and 'start_time' in values and v <= values['start_time']:
            raise ValueError('Stop time must be after start time')
        return v
    
    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Campaign name cannot be empty')
        return v.strip()


class CampaignUpdateRequest(BaseModel):
    """Request model for updating an existing campaign"""
    name: Optional[str] = Field(None, min_length=1, max_length=400)
    status: Optional[CampaignStatus] = None
    start_time: Optional[datetime] = None
    stop_time: Optional[datetime] = None
    budget_type: Optional[BudgetType] = None
    budget_amount: Optional[int] = Field(None, gt=0)
    frequency_cap: Optional[FrequencyCapSpec] = None


class CampaignResponse(BaseModel):
    """Response model for campaign data"""
    id: str
    name: str
    objective: CampaignObjective
    status: CampaignStatus
    start_time: datetime
    stop_time: Optional[datetime]
    budget_type: BudgetType
    budget_amount: int
    ad_account_id: str
    facebook_campaign_id: Optional[str] = None
    frequency_cap: Optional[FrequencyCapSpec] = None
    created_at: datetime
    updated_at: datetime
    sync_status: str = Field(default="pending", description="Sync status with Facebook")
    last_sync_at: Optional[datetime] = None
    facebook_data: Optional[Dict[str, Any]] = None


class CampaignListResponse(BaseModel):
    """Response model for campaign list"""
    campaigns: List[CampaignResponse]
    total: int
    page: int
    page_size: int
    has_next: bool


class CampaignSyncStatus(BaseModel):
    """Campaign synchronization status"""
    campaign_id: str
    facebook_campaign_id: Optional[str]
    sync_status: str
    last_sync_at: Optional[datetime]
    sync_errors: Optional[list[str]] = None
    facebook_status: Optional[str] = None
