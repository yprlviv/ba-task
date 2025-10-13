# Facebook Ads Manager Integration API

A comprehensive RESTful API solution for integrating with Facebook Ads Manager, enabling automated campaign management with robust error handling and rate limiting.

## 🎯 Project Overview

This project was developed as a business analyst test task to demonstrate the feasibility and implementation approach for Facebook Ads Manager integration. It includes both a detailed business analysis and a working concept solution.

## 📋 Business Analysis Results

### ✅ Fully Implementable Requirements
- **Campaign Creation**: Complete support for all specified parameters
- **Campaign Editing**: Full update capabilities for campaign settings  
- **Campaign Verification**: Real-time synchronization status checking
- **Campaign Deletion**: Safe campaign removal with proper status management

### ⚠️ Partially Implementable Requirements
- **Campaign Time Zone**: Managed at ad account level (Facebook limitation)
- **Frequency Capping**: Implemented at ad set level with additional logic

### ❌ Implementation Challenges
- **Automatic Advertiser Creation**: Facebook doesn't allow programmatic ad account creation
- **Solution**: Manual ad account setup with automated validation

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client App    │    │   Our API       │    │  Facebook API   │
│                 │◄──►│                 │◄──►│                 │
│  - Web UI       │    │  - Campaign Mgmt│    │  - Marketing API│
│  - Mobile App   │    │  - Rate Limiting│    │  - Ad Accounts  │
│  - 3rd Party    │    │  - Error Handle │    │  - Campaigns    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Facebook Developer Account
- Facebook Marketing API Access Token

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd testtask
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your Facebook API credentials
   ```

4. **Run the application**
   ```bash
   python -m app.main
   ```

5. **Access the API**
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health
   - API Root: http://localhost:8000/

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following configuration:

```env
# Facebook API Configuration
FACEBOOK_APP_ID=your_facebook_app_id
FACEBOOK_APP_SECRET=your_facebook_app_secret  
FACEBOOK_ACCESS_TOKEN=your_facebook_access_token
FACEBOOK_API_VERSION=v18.0

# Rate Limiting
FACEBOOK_RATE_LIMIT_POINTS=9000
FACEBOOK_RATE_LIMIT_WINDOW=300
MAX_RETRY_ATTEMPTS=3

# Application Settings
DEBUG=false
LOG_LEVEL=INFO
```

### Facebook API Setup

1. **Create Facebook App**
   - Go to [Facebook Developers](https://developers.facebook.com/)
   - Create a new app with Marketing API access

2. **Get Access Token**
   - Generate a long-lived access token
   - Ensure it has the following permissions:
     - `ads_management`
     - `ads_read`
     - `business_management`

3. **Verify Ad Account Access**
   - Use the `/api/v1/advertisers/validate` endpoint
   - Ensure your token can access the target ad accounts

## 📚 API Documentation

### Core Endpoints

#### Campaign Management
- `POST /api/v1/campaigns/` - Create new campaign
- `GET /api/v1/campaigns/` - List campaigns  
- `GET /api/v1/campaigns/{id}` - Get campaign details
- `PUT /api/v1/campaigns/{id}` - Update campaign
- `DELETE /api/v1/campaigns/{id}` - Delete campaign
- `GET /api/v1/campaigns/{id}/sync-status` - Check sync status

#### Advertiser Management  
- `POST /api/v1/advertisers/validate` - Validate ad account
- `POST /api/v1/advertisers/` - Register advertiser
- `GET /api/v1/advertisers/` - List advertisers
- `GET /api/v1/advertisers/{id}` - Get advertiser details
- `PUT /api/v1/advertisers/{id}` - Update advertiser

### Example Usage

#### Create a Campaign
```bash
curl -X POST "http://localhost:8000/api/v1/campaigns/" \
  -H "Content-Type: application/json" \
  -d '{
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
    }
  }'
```

#### Validate Ad Account
```bash
curl -X POST "http://localhost:8000/api/v1/advertisers/validate" \
  -H "Content-Type: application/json" \
  -d '{
    "facebook_ad_account_id": "act_123456789"
  }'
```

## 🔒 Security Features

- **Rate Limiting**: Prevents API abuse and respects Facebook limits
- **Input Validation**: Comprehensive request validation using Pydantic
- **Error Handling**: Graceful error responses with proper HTTP status codes
- **Security Headers**: Standard security headers for API protection
- **Access Control**: CORS configuration for cross-origin requests

## 📊 Monitoring & Logging

### Logging Levels
- **INFO**: General application flow
- **WARNING**: Rate limit warnings and recoverable errors  
- **ERROR**: Facebook API errors and system failures
- **DEBUG**: Detailed request/response information

### Health Checks
- `GET /health/` - Basic health status
- `GET /health/ready` - Readiness check with dependency validation

## 🚧 Known Limitations

### Facebook API Constraints
1. **Ad Account Creation**: Cannot create ad accounts programmatically
2. **Rate Limits**: 9,000 points per 300 seconds (Standard tier)
3. **Campaign Objective**: Cannot be changed after creation
4. **Time Zone**: Set at ad account level, not campaign level
5. **Frequency Capping**: Only available at ad set level

### Workarounds Implemented
- **Pre-validation**: Check ad account existence before operations
- **Rate Limiting**: Built-in rate limit management with queuing
- **Error Mapping**: User-friendly error messages for Facebook API errors
- **Retry Logic**: Automatic retry with exponential backoff
- **Frequency Cap**: Automatic ad set creation with frequency controls

## 🧪 Testing

### Manual Testing
1. **Start the application**
   ```bash
   python -m app.main
   ```

2. **Access interactive docs**
   - Open http://localhost:8000/docs
   - Test endpoints using the built-in Swagger UI

3. **Validate ad account**
   - Use the `/advertisers/validate` endpoint first
   - Ensure your Facebook credentials are working

### Automated Testing
```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests (when implemented)
pytest tests/
```

## 📈 Performance Considerations

### Rate Limiting Strategy
- **Point System**: Tracks Facebook API points usage
- **Window Management**: 300-second rolling window
- **Automatic Throttling**: Prevents rate limit violations
- **Retry Logic**: Exponential backoff for failed requests

### Optimization Tips
1. **Batch Operations**: Group multiple operations when possible
2. **Caching**: Cache ad account validation results
3. **Async Processing**: Use background tasks for heavy operations
4. **Connection Pooling**: Reuse HTTP connections to Facebook API

## 🔄 Deployment

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app/ ./app/
EXPOSE 8000

CMD ["python", "-m", "app.main"]
```

### Environment Setup
- **Development**: Use `.env` file for local configuration
- **Production**: Use environment variables or secret management
- **Staging**: Separate Facebook app for testing

## 📞 Support & Troubleshooting

### Common Issues

1. **"Invalid Access Token" Error**
   - Verify your Facebook access token is valid
   - Check token permissions include `ads_management`
   - Ensure token hasn't expired

2. **"Ad Account Not Found" Error**  
   - Verify ad account ID format (should start with `act_`)
   - Check if your token has access to the ad account
   - Confirm ad account exists in Facebook Business Manager

3. **Rate Limit Exceeded**
   - Wait for the rate limit window to reset (5 minutes)
   - Reduce request frequency
   - Consider upgrading Facebook API access tier

### Debug Mode
Enable debug logging by setting `LOG_LEVEL=DEBUG` in your environment.

## 📄 Business Analysis Documents

This repository includes comprehensive business analysis documentation:

- **`Facebook_Ads_Integration_Analysis.md`** - Complete technical analysis
- **`Customer_Email_Analysis_Results.md`** - Professional customer communication

## 🤝 Contributing

This is a demonstration project for a business analyst test task. The code showcases:

- **API Design Best Practices**
- **Facebook Marketing API Integration Patterns**  
- **Error Handling Strategies**
- **Rate Limiting Implementation**
- **Business Requirements Analysis**

## 📝 License

This project is created for demonstration purposes as part of a business analyst assessment.

---

**Note**: This is a concept solution demonstrating Facebook Ads Manager integration feasibility. For production use, additional considerations around database persistence, authentication, authorization, and comprehensive testing would be required.
