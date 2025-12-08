"""Test configuration and fixtures"""
import pytest


@pytest.fixture
def sample_car_model():
    """Sample car model data for testing"""
    return {
        "make": "Tesla",
        "model": "Model 3",
        "year": 2024,
        "battery_capacity_kwh": 75.0,
        "range_miles": 310,
    }


@pytest.fixture
def sample_car_models():
    """Sample list of car models for testing"""
    return [
        {
            "make": "Tesla",
            "model": "Model 3",
            "year": 2024,
            "battery_capacity_kwh": 75.0,
            "range_miles": 310,
        },
        {
            "make": "Nissan",
            "model": "Leaf",
            "year": 2024,
            "battery_capacity_kwh": 60.0,
            "range_miles": 226,
        },
    ]
