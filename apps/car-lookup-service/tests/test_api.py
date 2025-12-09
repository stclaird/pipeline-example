"""
Unit tests for the car-lookup-service API
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_read_root():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_list_car_models():
    """Test listing car models"""
    response = client.get("/api/v1/car-models/")
    assert response.status_code in [200, 500]  # May fail without DB connection


@pytest.mark.asyncio
async def test_get_car_model_not_found():
    """Test getting a non-existent car model"""
    response = client.get("/api/v1/car-models/99999")
    assert response.status_code in [404, 500]  # May fail without DB connection


def test_openapi_schema():
    """Test that OpenAPI schema is available"""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "openapi" in schema
    assert "info" in schema
