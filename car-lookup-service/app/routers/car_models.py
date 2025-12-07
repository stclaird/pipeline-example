from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging
from pydantic import BaseModel, Field

from app.database import get_db
from app.models import CarModel

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic schemas

class CarModelBase(BaseModel):
    make: str = Field(..., max_length=100)
    model: str = Field(..., max_length=100)
    year: int = Field(..., ge=1900, le=2100)
    battery_capacity_kwh: Optional[float] = Field(None, ge=0)
    max_range_km: Optional[float] = Field(None, ge=0)
    connector_type: Optional[str] = Field(None, max_length=50)

class CarModelCreate(CarModelBase):
    pass

class CarModelUpdate(BaseModel):
    make: Optional[str] = Field(None, max_length=100)
    model: Optional[str] = Field(None, max_length=100)
    year: Optional[int] = Field(None, ge=1900, le=2100)
    battery_capacity_kwh: Optional[float] = Field(None, ge=0)
    max_range_km: Optional[float] = Field(None, ge=0)
    connector_type: Optional[str] = Field(None, max_length=50)

class CarModelResponse(CarModelBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

@router.get("/health")
def health_check():
    """Health check endpoint for car models router"""
    return {"status": "healthy", "service": "car-models"}

@router.get("/", response_model=List[CarModelResponse])
def get_car_models(
    skip: int = 0,
    limit: int = 100,
    make: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all car models with optional filters."""
    logger.info(f"Fetching car models - make: {make}, search: {search}, limit: {limit}")

    query = db.query(CarModel)

    # Filter by make if specified
    if make:
        query = query.filter(CarModel.make.ilike(f"%{make}%"))

    # Filter by search term if specified (search in make and model)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (CarModel.make.ilike(search_term)) | (CarModel.model.ilike(search_term))
        )

    car_models = query.offset(skip).limit(limit).all()
    logger.info(f"Found {len(car_models)} car models")
    
    return car_models

@router.get("/{car_model_id}", response_model=CarModelResponse)
def get_car_model(car_model_id: int, db: Session = Depends(get_db)):
    """Get a specific car model by ID."""
    logger.info(f"Fetching car model with ID: {car_model_id}")
    
    car_model = db.query(CarModel).filter(CarModel.id == car_model_id).first()
    
    if not car_model:
        logger.warning(f"Car model with ID {car_model_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Car model with ID {car_model_id} not found"
        )
    
    return car_model

@router.post("/", response_model=CarModelResponse, status_code=status.HTTP_201_CREATED)
def create_car_model(
    car_model: CarModelCreate,
    db: Session = Depends(get_db)
):
    """Create a new car model (admin function)."""
    logger.info(f"Creating new car model: {car_model.make} {car_model.model}")
    
    # Check if model already exists
    existing = db.query(CarModel).filter(
        CarModel.make == car_model.make,
        CarModel.model == car_model.model,
        CarModel.year == car_model.year
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Car model {car_model.make} {car_model.model} ({car_model.year}) already exists"
        )
    
    db_car_model = CarModel(**car_model.model_dump())
    db.add(db_car_model)
    db.commit()
    db.refresh(db_car_model)
    
    logger.info(f"Successfully created car model with ID: {db_car_model.id}")
    return db_car_model

@router.put("/{car_model_id}", response_model=CarModelResponse)
def update_car_model(
    car_model_id: int,
    car_model_update: CarModelUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing car model (admin function)."""
    logger.info(f"Updating car model with ID: {car_model_id}")
    
    db_car_model = db.query(CarModel).filter(CarModel.id == car_model_id).first()
    
    if not db_car_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Car model with ID {car_model_id} not found"
        )
    
    # Update only provided fields
    update_data = car_model_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_car_model, field, value)
    
    db.commit()
    db.refresh(db_car_model)
    
    logger.info(f"Successfully updated car model with ID: {car_model_id}")
    return db_car_model

@router.delete("/{car_model_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_car_model(car_model_id: int, db: Session = Depends(get_db)):
    """Delete a car model (admin function)."""
    logger.info(f"Deleting car model with ID: {car_model_id}")
    
    db_car_model = db.query(CarModel).filter(CarModel.id == car_model_id).first()
    
    if not db_car_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Car model with ID {car_model_id} not found"
        )
    
    db.delete(db_car_model)
    db.commit()
    
    logger.info(f"Successfully deleted car model with ID: {car_model_id}")
    return None
