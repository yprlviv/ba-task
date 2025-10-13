"""
Advertiser (Ad Account) data models and schemas
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class AdvertiserStatus(str, Enum):
    """Advertiser status options"""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    PENDING = "PENDING"
    SUSPENDED = "SUSPENDED"


class AdvertiserCategory(str, Enum):
    """Advertiser business categories"""
    ECOMMERCE = "ECOMMERCE"
    TECHNOLOGY = "TECHNOLOGY"
    HEALTHCARE = "HEALTHCARE"
    FINANCE = "FINANCE"
    EDUCATION = "EDUCATION"
    ENTERTAINMENT = "ENTERTAINMENT"
    TRAVEL = "TRAVEL"
    AUTOMOTIVE = "AUTOMOTIVE"
    REAL_ESTATE = "REAL_ESTATE"
    OTHER = "OTHER"


class AdvertiserCreateRequest(BaseModel):
    """Request model for creating/registering an advertiser"""
    name: str = Field(..., min_length=1, max_length=200)
    category: AdvertiserCategory
    facebook_ad_account_id: str = Field(..., description="Existing Facebook ad account ID")
    business_id: Optional[str] = Field(None, description="Facebook Business Manager ID")
    
    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Advertiser name cannot be empty')
        return v.strip()


class AdvertiserUpdateRequest(BaseModel):
    """Request model for updating advertiser information"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    category: Optional[AdvertiserCategory] = None
    status: Optional[AdvertiserStatus] = None


class AdvertiserResponse(BaseModel):
    """Response model for advertiser data"""
    id: str
    name: str
    category: AdvertiserCategory
    status: AdvertiserStatus
    facebook_ad_account_id: str
    business_id: Optional[str] = None
    currency: Optional[str] = None
    timezone: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    verification_status: str = Field(default="pending")
    facebook_data: Optional[Dict[str, Any]] = None


class AdvertiserListResponse(BaseModel):
    """Response model for advertiser list"""
    advertisers: List[AdvertiserResponse]
    total: int
    page: int
    page_size: int
    has_next: bool


class AdvertiserValidationRequest(BaseModel):
    """Request model for validating advertiser/ad account"""
    facebook_ad_account_id: str
    
    
class AdvertiserValidationResponse(BaseModel):
    """Response model for advertiser validation"""
    facebook_ad_account_id: str
    exists: bool
    is_valid: bool
    account_name: Optional[str] = None
    currency: Optional[str] = None
    timezone: Optional[str] = None
    status: Optional[str] = None
    permissions: Optional[list[str]] = None
    validation_errors: Optional[list[str]] = None
