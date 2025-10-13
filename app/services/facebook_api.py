"""
Facebook Marketing API integration service
"""

import httpx
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from app.core.config import settings
from app.models.campaign import CampaignCreateRequest, CampaignObjective, BudgetType
from app.models.advertiser import AdvertiserValidationResponse


logger = logging.getLogger(__name__)


class FacebookAPIError(Exception):
    """Custom exception for Facebook API errors"""
    def __init__(self, message: str, error_code: Optional[str] = None, status_code: Optional[int] = None):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(self.message)


class RateLimitExceeded(FacebookAPIError):
    """Exception raised when rate limit is exceeded"""
    pass


class FacebookAPIService:
    """Service for interacting with Facebook Marketing API"""
    
    def __init__(self):
        self.base_url = f"{settings.FACEBOOK_API_BASE_URL}/{settings.FACEBOOK_API_VERSION}"
        self.access_token = settings.FACEBOOK_ACCESS_TOKEN
        self.rate_limit_points = settings.FACEBOOK_RATE_LIMIT_POINTS
        self.rate_limit_window = settings.FACEBOOK_RATE_LIMIT_WINDOW
        self.current_points = 0
        self.window_start = datetime.now(timezone.utc)
        
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to Facebook API with rate limiting"""
        
        # Check rate limiting
        await self._check_rate_limit(method)
        
        url = f"{self.base_url}/{endpoint}"
        
        # Add access token to parameters
        if not params:
            params = {}
        params['access_token'] = self.access_token
        
        try:
            async with httpx.AsyncClient() as client:
                if method.upper() == 'GET':
                    response = await client.get(url, params=params)
                elif method.upper() == 'POST':
                    response = await client.post(url, params=params, json=data)
                elif method.upper() == 'DELETE':
                    response = await client.delete(url, params=params)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                # Update rate limiting counters
                self._update_rate_limit_counters(method)
                
                # Handle response
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    raise RateLimitExceeded("Rate limit exceeded", status_code=429)
                else:
                    error_data = response.json() if response.content else {}
                    error_message = error_data.get('error', {}).get('message', 'Unknown error')
                    error_code = error_data.get('error', {}).get('code')
                    raise FacebookAPIError(error_message, error_code, response.status_code)
                    
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            raise FacebookAPIError(f"Request failed: {str(e)}")
    
    async def _check_rate_limit(self, method: str):
        """Check if request would exceed rate limits"""
        now = datetime.now(timezone.utc)
        
        # Reset window if needed
        if (now - self.window_start).total_seconds() >= self.rate_limit_window:
            self.current_points = 0
            self.window_start = now
        
        # Calculate points for this request
        points = 3 if method.upper() in ['POST', 'DELETE'] else 1
        
        # Check if we would exceed limit
        if self.current_points + points > self.rate_limit_points:
            wait_time = self.rate_limit_window - (now - self.window_start).total_seconds()
            if wait_time > 0:
                logger.warning(f"Rate limit would be exceeded, waiting {wait_time} seconds")
                await asyncio.sleep(wait_time)
                self.current_points = 0
                self.window_start = datetime.now(timezone.utc)
    
    def _update_rate_limit_counters(self, method: str):
        """Update rate limiting counters after successful request"""
        points = 3 if method.upper() in ['POST', 'DELETE'] else 1
        self.current_points += points
        logger.debug(f"Rate limit: {self.current_points}/{self.rate_limit_points} points used")
    
    async def validate_ad_account(self, ad_account_id: str) -> AdvertiserValidationResponse:
        """Validate Facebook ad account existence and permissions"""
        try:
            # Format ad account ID
            if not ad_account_id.startswith('act_'):
                ad_account_id = f"act_{ad_account_id}"
            
            # Get ad account details
            params = {
                'fields': 'name,account_status,currency,timezone_name,account_id'
            }
            
            response = await self._make_request('GET', ad_account_id, params=params)
            
            return AdvertiserValidationResponse(
                facebook_ad_account_id=ad_account_id,
                exists=True,
                is_valid=response.get('account_status') == 1,  # 1 = ACTIVE
                account_name=response.get('name'),
                currency=response.get('currency'),
                timezone=response.get('timezone_name'),
                status='ACTIVE' if response.get('account_status') == 1 else 'INACTIVE',
                permissions=['MANAGE_CAMPAIGNS']  # Simplified for demo
            )
            
        except FacebookAPIError as e:
            if e.status_code == 404:
                return AdvertiserValidationResponse(
                    facebook_ad_account_id=ad_account_id,
                    exists=False,
                    is_valid=False,
                    validation_errors=[f"Ad account {ad_account_id} not found"]
                )
            else:
                return AdvertiserValidationResponse(
                    facebook_ad_account_id=ad_account_id,
                    exists=False,
                    is_valid=False,
                    validation_errors=[f"Validation failed: {e.message}"]
                )
    
    async def create_campaign(self, campaign_data: CampaignCreateRequest) -> Dict[str, Any]:
        """Create a new campaign in Facebook Ads Manager"""
        
        # Format ad account ID
        ad_account_id = campaign_data.ad_account_id
        if not ad_account_id.startswith('act_'):
            ad_account_id = f"act_{ad_account_id}"
        
        # Prepare campaign data for Facebook API
        facebook_data = {
            'name': campaign_data.name,
            'objective': campaign_data.objective.value,
            'status': 'PAUSED',  # Start paused for safety
            'start_time': campaign_data.start_time.isoformat(),
        }
        
        # Add budget
        if campaign_data.budget_type == BudgetType.DAILY:
            facebook_data['daily_budget'] = campaign_data.budget_amount
        else:
            facebook_data['lifetime_budget'] = campaign_data.budget_amount
        
        # Add stop time if provided
        if campaign_data.stop_time:
            facebook_data['stop_time'] = campaign_data.stop_time.isoformat()
        
        # Create campaign
        endpoint = f"{ad_account_id}/campaigns"
        response = await self._make_request('POST', endpoint, data=facebook_data)
        
        # If frequency cap is specified, we need to create an ad set with frequency control
        if campaign_data.frequency_cap:
            await self._create_default_adset_with_frequency_cap(
                response['id'], 
                campaign_data.frequency_cap,
                campaign_data.budget_amount,
                campaign_data.budget_type
            )
        
        return response
    
    async def _create_default_adset_with_frequency_cap(
        self, 
        campaign_id: str, 
        frequency_cap, 
        budget_amount: int,
        budget_type: BudgetType
    ):
        """Create a default ad set with frequency capping for the campaign"""
        
        adset_data = {
            'name': f"Default AdSet for Campaign {campaign_id}",
            'campaign_id': campaign_id,
            'status': 'PAUSED',
            'targeting': {
                'geo_locations': {'countries': ['US']},  # Default targeting
                'age_min': 18,
                'age_max': 65
            },
            'frequency_control_specs': [{
                'event': frequency_cap.event,
                'interval_days': frequency_cap.interval_days,
                'max_frequency': frequency_cap.max_frequency
            }]
        }
        
        # Add budget to ad set level for frequency capping
        if budget_type == BudgetType.DAILY:
            adset_data['daily_budget'] = budget_amount
        else:
            adset_data['lifetime_budget'] = budget_amount
        
        endpoint = f"act_{campaign_id.split('_')[1]}/adsets"  # Extract account ID
        return await self._make_request('POST', endpoint, data=adset_data)
    
    async def get_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """Get campaign details from Facebook"""
        params = {
            'fields': 'name,objective,status,start_time,stop_time,daily_budget,lifetime_budget,created_time,updated_time'
        }
        return await self._make_request('GET', campaign_id, params=params)
    
    async def update_campaign(self, campaign_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update campaign in Facebook"""
        return await self._make_request('POST', campaign_id, data=update_data)
    
    async def delete_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """Delete campaign in Facebook (set status to DELETED)"""
        return await self._make_request('POST', campaign_id, data={'status': 'DELETED'})
    
    async def list_campaigns(self, ad_account_id: str, limit: int = 25) -> Dict[str, Any]:
        """List campaigns for an ad account"""
        if not ad_account_id.startswith('act_'):
            ad_account_id = f"act_{ad_account_id}"
        
        params = {
            'fields': 'name,objective,status,start_time,stop_time,daily_budget,lifetime_budget,created_time,updated_time',
            'limit': limit
        }
        
        endpoint = f"{ad_account_id}/campaigns"
        return await self._make_request('GET', endpoint, params=params)


# Global service instance
facebook_service = FacebookAPIService()
