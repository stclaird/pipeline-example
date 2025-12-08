from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.routers import car_models
from app.database import engine, Base

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Joose Car Lookup Service",
    description="Microservice for EV car model reference data",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    car_models.router,
    prefix="/api/v1/car-models",
    tags=["car-models"]
)

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    logger.info("Starting Car Lookup Service...")
    logger.info("Database connection initialized")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Joose Car Lookup Service",
        "service": "Joose Car Lookup Service",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "car-lookup"
    }
