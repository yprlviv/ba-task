"""
Basic API tests for the Facebook Ads Integration
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """Test basic health check endpoint"""
    response = client.get("/health/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data


def test_readiness_check():
    """Test readiness check endpoint"""
    response = client.get("/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert "checks" in data


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "Facebook Ads Manager Integration API" in data["message"]
    assert data["version"] == "1.0.0"


def test_api_docs():
    """Test API documentation is accessible"""
    response = client.get("/docs")
    assert response.status_code == 200


def test_campaign_list_without_account():
    """Test campaign listing without ad account ID"""
    response = client.get("/api/v1/campaigns/")
    assert response.status_code == 200
    data = response.json()
    assert "campaigns" in data
    assert data["total"] == 0  # No campaigns without ad account


def test_advertiser_list():
    """Test advertiser listing"""
    response = client.get("/api/v1/advertisers/")
    assert response.status_code == 200
    data = response.json()
    assert "advertisers" in data


def test_invalid_campaign_creation():
    """Test campaign creation with invalid data"""
    invalid_campaign = {
        "name": "",  # Invalid empty name
        "objective": "INVALID_OBJECTIVE",
        "start_time": "invalid-date",
        "budget_amount": -100,  # Invalid negative budget
        "ad_account_id": "invalid"
    }
    
    response = client.post("/api/v1/campaigns/", json=invalid_campaign)
    assert response.status_code == 422  # Validation error


def test_advertiser_validation_invalid_account():
    """Test advertiser validation with invalid account"""
    validation_request = {
        "facebook_ad_account_id": "invalid_account_id"
    }
    
    response = client.post("/api/v1/advertisers/validate", json=validation_request)
    assert response.status_code == 200  # Should return validation response
    data = response.json()
    assert data["exists"] is False
    assert data["is_valid"] is False


if __name__ == "__main__":
    pytest.main([__file__])
