# Facebook Ads Integration API Documentation

## Overview

This API provides comprehensive integration with Facebook Ads Manager, enabling automated campaign management while handling Facebook's API limitations and constraints.

## Base URL
```
http://localhost:8000
```

## Authentication

Currently, the API uses a server-side Facebook access token configured via environment variables. In a production environment, you would implement proper authentication and authorization.

## Rate Limiting

The API implements intelligent rate limiting to respect Facebook's API constraints:
- **Standard Tier**: 9,000 points per 300 seconds
- **Point System**: Read operations (1 point), Write operations (3 points)
- **Headers**: Rate limit information included in response headers

## Error Handling

All errors follow a consistent format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "timestamp": "2025-10-13T00:00:00Z",
    "details": {
      "additional": "context"
    }
  }
}
```

### Common Error Codes
- `VALIDATION_ERROR` - Request validation failed
- `FACEBOOK_API_ERROR` - Facebook API returned an error
- `RATE_LIMIT_EXCEEDED` - API rate limit exceeded
- `AD_ACCOUNT_NOT_FOUND` - Facebook ad account not found
- `CAMPAIGN_NOT_FOUND` - Campaign not found
- `INTERNAL_SERVER_ERROR` - Unexpected server error

## Endpoints

### Health & Status

#### GET /health/
Basic health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-13T00:00:00Z",
  "service": "Facebook Ads Integration API"
}
```

#### GET /health/ready
Readiness check with dependency validation.

**Response:**
```json
{
  "status": "ready",
  "timestamp": "2025-10-13T00:00:00Z",
  "checks": {
    "database": "ok",
    "facebook_api": "ok",
    "cache": "ok"
  }
}
```

### Campaign Management

#### POST /api/v1/campaigns/
Create a new campaign in both systems.

**Request Body:**
```json
{
  "name": "Summer Sale Campaign",
  "objective": "OUTCOME_TRAFFIC",
  "start_time": "2025-06-01T00:00:00Z",
  "stop_time": "2025-08-31T23:59:59Z",
  "budget_type": "daily_budget",
  "budget_amount": 5000,
  "ad_account_id": "act_123456789",
  "frequency_cap": {
    "event": "IMPRESSIONS",
    "interval_days": 7,
    "max_frequency": 3
  },
  "timezone": "America/New_York"
}
```

**Campaign Objectives:**
- `OUTCOME_AWARENESS` - Brand awareness
- `OUTCOME_TRAFFIC` - Traffic to website/app
- `OUTCOME_ENGAGEMENT` - Post engagement
- `OUTCOME_LEADS` - Lead generation
- `OUTCOME_APP_PROMOTION` - App installs/engagement
- `OUTCOME_SALES` - Conversions/catalog sales

**Budget Types:**
- `daily_budget` - Daily budget limit
- `lifetime_budget` - Total campaign budget

**Response:**
```json
{
  "id": "uuid-string",
  "name": "Summer Sale Campaign",
  "objective": "OUTCOME_TRAFFIC",
  "status": "PAUSED",
  "start_time": "2025-06-01T00:00:00Z",
  "stop_time": "2025-08-31T23:59:59Z",
  "budget_type": "daily_budget",
  "budget_amount": 5000,
  "ad_account_id": "act_123456789",
  "facebook_campaign_id": "23847xxxxx",
  "frequency_cap": {
    "event": "IMPRESSIONS",
    "interval_days": 7,
    "max_frequency": 3
  },
  "created_at": "2025-10-13T00:00:00Z",
  "updated_at": "2025-10-13T00:00:00Z",
  "sync_status": "synced",
  "last_sync_at": "2025-10-13T00:00:00Z",
  "facebook_data": {
    "id": "23847xxxxx",
    "name": "Summer Sale Campaign",
    "status": "PAUSED"
  }
}
```

#### GET /api/v1/campaigns/
List campaigns with optional filtering.

**Query Parameters:**
- `ad_account_id` (optional) - Filter by Facebook ad account ID
- `page` (default: 1) - Page number for pagination
- `page_size` (default: 25, max: 100) - Items per page

**Response:**
```json
{
  "campaigns": [
    {
      "id": "uuid-string",
      "name": "Campaign Name",
      "objective": "OUTCOME_TRAFFIC",
      "status": "ACTIVE",
      "facebook_campaign_id": "23847xxxxx",
      "created_at": "2025-10-13T00:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 25,
  "has_next": false
}
```

#### GET /api/v1/campaigns/{campaign_id}
Get campaign details by ID.

**Path Parameters:**
- `campaign_id` - Campaign ID (can be internal ID or Facebook campaign ID)

**Response:** Same as campaign creation response.

#### PUT /api/v1/campaigns/{campaign_id}
Update campaign settings.

**Request Body:**
```json
{
  "name": "Updated Campaign Name",
  "status": "ACTIVE",
  "budget_amount": 7500,
  "stop_time": "2025-09-30T23:59:59Z"
}
```

**Note:** Campaign objective cannot be changed after creation (Facebook limitation).

#### DELETE /api/v1/campaigns/{campaign_id}
Delete campaign (sets status to DELETED in Facebook).

**Response:**
```json
{
  "message": "Campaign deleted successfully",
  "campaign_id": "23847xxxxx"
}
```

#### GET /api/v1/campaigns/{campaign_id}/sync-status
Get campaign synchronization status with Facebook.

**Response:**
```json
{
  "campaign_id": "uuid-string",
  "facebook_campaign_id": "23847xxxxx",
  "sync_status": "synced",
  "last_sync_at": "2025-10-13T00:00:00Z",
  "sync_errors": null,
  "facebook_status": "ACTIVE"
}
```

**Sync Status Values:**
- `synced` - Successfully synchronized
- `pending` - Synchronization in progress
- `error` - Synchronization failed
- `not_found` - Campaign not found in Facebook

### Advertiser Management

#### POST /api/v1/advertisers/validate
Validate Facebook ad account existence and permissions.

**Request Body:**
```json
{
  "facebook_ad_account_id": "act_123456789"
}
```

**Response:**
```json
{
  "facebook_ad_account_id": "act_123456789",
  "exists": true,
  "is_valid": true,
  "account_name": "My Business Account",
  "currency": "USD",
  "timezone": "America/New_York",
  "status": "ACTIVE",
  "permissions": ["MANAGE_CAMPAIGNS"],
  "validation_errors": null
}
```

#### POST /api/v1/advertisers/
Register an existing Facebook ad account.

**Request Body:**
```json
{
  "name": "My Business",
  "category": "ECOMMERCE",
  "facebook_ad_account_id": "act_123456789",
  "business_id": "123456789"
}
```

**Advertiser Categories:**
- `ECOMMERCE` - E-commerce business
- `TECHNOLOGY` - Technology company
- `HEALTHCARE` - Healthcare services
- `FINANCE` - Financial services
- `EDUCATION` - Educational institution
- `ENTERTAINMENT` - Entertainment/Media
- `TRAVEL` - Travel/Tourism
- `AUTOMOTIVE` - Automotive industry
- `REAL_ESTATE` - Real estate
- `OTHER` - Other category

**Response:**
```json
{
  "id": "uuid-string",
  "name": "My Business",
  "category": "ECOMMERCE",
  "status": "ACTIVE",
  "facebook_ad_account_id": "act_123456789",
  "business_id": "123456789",
  "currency": "USD",
  "timezone": "America/New_York",
  "created_at": "2025-10-13T00:00:00Z",
  "updated_at": "2025-10-13T00:00:00Z",
  "verification_status": "verified",
  "facebook_data": {
    "account_name": "My Business Account",
    "account_status": "ACTIVE",
    "permissions": ["MANAGE_CAMPAIGNS"]
  }
}
```

#### GET /api/v1/advertisers/
List registered advertisers.

**Query Parameters:**
- `page` (default: 1) - Page number
- `page_size` (default: 25, max: 100) - Items per page
- `status` (optional) - Filter by status

**Response:**
```json
{
  "advertisers": [
    {
      "id": "uuid-string",
      "name": "My Business",
      "category": "ECOMMERCE",
      "status": "ACTIVE",
      "facebook_ad_account_id": "act_123456789",
      "created_at": "2025-10-13T00:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 25,
  "has_next": false
}
```

#### GET /api/v1/advertisers/{advertiser_id}
Get advertiser details by ID.

#### PUT /api/v1/advertisers/{advertiser_id}
Update advertiser information.

#### DELETE /api/v1/advertisers/{advertiser_id}
Remove advertiser from system (Facebook ad account remains unchanged).

#### GET /api/v1/advertisers/{advertiser_id}/campaigns
Get all campaigns for a specific advertiser.

## SDK Examples

### Python Example
```python
import httpx
import asyncio

async def create_campaign():
    async with httpx.AsyncClient() as client:
        campaign_data = {
            "name": "API Test Campaign",
            "objective": "OUTCOME_TRAFFIC",
            "start_time": "2025-06-01T00:00:00Z",
            "budget_type": "daily_budget",
            "budget_amount": 1000,
            "ad_account_id": "act_123456789"
        }
        
        response = await client.post(
            "http://localhost:8000/api/v1/campaigns/",
            json=campaign_data
        )
        
        if response.status_code == 200:
            campaign = response.json()
            print(f"Campaign created: {campaign['facebook_campaign_id']}")
        else:
            error = response.json()
            print(f"Error: {error['error']['message']}")

# Run the example
asyncio.run(create_campaign())
```

### JavaScript Example
```javascript
async function createCampaign() {
    const campaignData = {
        name: "API Test Campaign",
        objective: "OUTCOME_TRAFFIC",
        start_time: "2025-06-01T00:00:00Z",
        budget_type: "daily_budget",
        budget_amount: 1000,
        ad_account_id: "act_123456789"
    };
    
    try {
        const response = await fetch('http://localhost:8000/api/v1/campaigns/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(campaignData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            console.log('Campaign created:', result.facebook_campaign_id);
        } else {
            console.error('Error:', result.error.message);
        }
    } catch (error) {
        console.error('Request failed:', error);
    }
}
```

### cURL Examples

**Validate Ad Account:**
```bash
curl -X POST "http://localhost:8000/api/v1/advertisers/validate" \
  -H "Content-Type: application/json" \
  -d '{"facebook_ad_account_id": "act_123456789"}'
```

**Create Campaign:**
```bash
curl -X POST "http://localhost:8000/api/v1/campaigns/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Campaign",
    "objective": "OUTCOME_TRAFFIC",
    "start_time": "2025-06-01T00:00:00Z",
    "budget_type": "daily_budget",
    "budget_amount": 1000,
    "ad_account_id": "act_123456789"
  }'
```

**List Campaigns:**
```bash
curl "http://localhost:8000/api/v1/campaigns/?ad_account_id=act_123456789&page=1&page_size=10"
```

**Update Campaign:**
```bash
curl -X PUT "http://localhost:8000/api/v1/campaigns/23847xxxxx" \
  -H "Content-Type: application/json" \
  -d '{"status": "ACTIVE", "budget_amount": 2000}'
```

## Best Practices

### Error Handling
Always check response status codes and handle errors appropriately:

```python
if response.status_code == 429:
    # Rate limit exceeded - wait and retry
    retry_after = int(response.headers.get('Retry-After', 60))
    await asyncio.sleep(retry_after)
elif response.status_code >= 400:
    # Handle error
    error = response.json()
    print(f"API Error: {error['error']['message']}")
```

### Rate Limiting
Monitor rate limit headers and implement backoff strategies:

```python
remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
if remaining < 10:
    # Slow down requests
    await asyncio.sleep(1)
```

### Validation
Always validate ad accounts before creating campaigns:

```python
# First validate the ad account
validation = await validate_ad_account("act_123456789")
if not validation['is_valid']:
    raise Exception(f"Invalid ad account: {validation['validation_errors']}")

# Then create campaign
campaign = await create_campaign(campaign_data)
```

## Limitations & Considerations

1. **Ad Account Creation**: Cannot create Facebook ad accounts programmatically
2. **Campaign Objectives**: Cannot be changed after creation
3. **Time Zones**: Managed at ad account level, not campaign level
4. **Frequency Capping**: Implemented at ad set level with automatic ad set creation
5. **Rate Limits**: Respect Facebook's API rate limits (9,000 points per 300 seconds)
6. **Permissions**: Requires proper Facebook API permissions and business verification

## Support

For issues or questions about this API:
1. Check the error response for specific error codes and messages
2. Verify Facebook API credentials and permissions
3. Ensure ad accounts exist and are accessible
4. Monitor rate limit usage and implement appropriate backoff strategies
