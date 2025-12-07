from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

# Database URL for car service - points to joose_cars database
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgresql://user:password@localhost:5432/joose_cars'
)

# Create Base class for models
Base = declarative_base()

# Initialize database components
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize database connection"""
    return engine

# Dependency to get DB session
def get_db():
    init_db()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
