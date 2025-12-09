"""
Clean car model data seeding script with curated popular UK electric vehicles
"""

import logging
import sys
import os

# Add the parent directory to the path to import from app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import SessionLocal, engine
from app.models import CarModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_existing_car_models(db: Session):
    """Remove existing seeded car models to avoid duplicates."""
    logger.info("Cleaning existing seeded car models...")

    # Delete all car models (they're all templates)
    result = db.execute(text("DELETE FROM car_models"))
    db.commit()

    logger.info(f"Deleted {result.rowcount} existing car models")

def seed_curated_car_models(db: Session):
    """Seed the database with curated popular UK electric vehicles."""

    # Curated list of popular UK electric vehicles with accurate specs
    curated_cars = [
        # Tesla Models
        {"make": "Tesla", "model": "Model 3", "year": 2024, "battery_capacity_kwh": 75.0, "max_range_km": 491, "connector_type": "CCS"},
        {"make": "Tesla", "model": "Model 3 Performance", "year": 2024, "battery_capacity_kwh": 75.0, "max_range_km": 507, "connector_type": "CCS"},
        {"make": "Tesla", "model": "Model 3 Long Range", "year": 2024, "battery_capacity_kwh": 75.0, "max_range_km": 629, "connector_type": "CCS"},
        {"make": "Tesla", "model": "Model Y", "year": 2024, "battery_capacity_kwh": 75.0, "max_range_km": 455, "connector_type": "CCS"},
        {"make": "Tesla", "model": "Model Y Long Range", "year": 2024, "battery_capacity_kwh": 75.0, "max_range_km": 533, "connector_type": "CCS"},
        {"make": "Tesla", "model": "Model Y Performance", "year": 2024, "battery_capacity_kwh": 75.0, "max_range_km": 514, "connector_type": "CCS"},
        {"make": "Tesla", "model": "Model S", "year": 2024, "battery_capacity_kwh": 100.0, "max_range_km": 634, "connector_type": "CCS"},
        {"make": "Tesla", "model": "Model S Plaid", "year": 2024, "battery_capacity_kwh": 100.0, "max_range_km": 600, "connector_type": "CCS"},
        {"make": "Tesla", "model": "Model X", "year": 2024, "battery_capacity_kwh": 100.0, "max_range_km": 563, "connector_type": "CCS"},
        {"make": "Tesla", "model": "Model X Plaid", "year": 2024, "battery_capacity_kwh": 100.0, "max_range_km": 528, "connector_type": "CCS"},

        # Mercedes-Benz
        {"make": "Mercedes-Benz", "model": "EQA 250", "year": 2024, "battery_capacity_kwh": 66.5, "max_range_km": 426, "connector_type": "CCS"},
        {"make": "Mercedes-Benz", "model": "EQB 250", "year": 2024, "battery_capacity_kwh": 66.5, "max_range_km": 419, "connector_type": "CCS"},
        {"make": "Mercedes-Benz", "model": "EQC 400", "year": 2024, "battery_capacity_kwh": 80.0, "max_range_km": 417, "connector_type": "CCS"},
        {"make": "Mercedes-Benz", "model": "EQE 350", "year": 2024, "battery_capacity_kwh": 90.6, "max_range_km": 547, "connector_type": "CCS"},
        {"make": "Mercedes-Benz", "model": "EQS 450", "year": 2024, "battery_capacity_kwh": 107.8, "max_range_km": 770, "connector_type": "CCS"},

        # BMW
        {"make": "BMW", "model": "iX3", "year": 2024, "battery_capacity_kwh": 74.0, "max_range_km": 461, "connector_type": "CCS"},
        {"make": "BMW", "model": "i4 eDrive40", "year": 2024, "battery_capacity_kwh": 83.9, "max_range_km": 590, "connector_type": "CCS"},
        {"make": "BMW", "model": "i4 M50", "year": 2024, "battery_capacity_kwh": 83.9, "max_range_km": 510, "connector_type": "CCS"},
        {"make": "BMW", "model": "iX xDrive40", "year": 2024, "battery_capacity_kwh": 76.6, "max_range_km": 425, "connector_type": "CCS"},
        {"make": "BMW", "model": "iX xDrive50", "year": 2024, "battery_capacity_kwh": 111.5, "max_range_km": 630, "connector_type": "CCS"},

        # Audi
        {"make": "Audi", "model": "e-tron GT", "year": 2024, "battery_capacity_kwh": 93.4, "max_range_km": 488, "connector_type": "CCS"},
        {"make": "Audi", "model": "e-tron 55", "year": 2024, "battery_capacity_kwh": 95.0, "max_range_km": 441, "connector_type": "CCS"},
        {"make": "Audi", "model": "Q4 e-tron 40", "year": 2024, "battery_capacity_kwh": 82.0, "max_range_km": 520, "connector_type": "CCS"},
        {"make": "Audi", "model": "Q4 e-tron 50", "year": 2024, "battery_capacity_kwh": 82.0, "max_range_km": 488, "connector_type": "CCS"},

        # Volkswagen
        {"make": "Volkswagen", "model": "ID.3 Pro", "year": 2024, "battery_capacity_kwh": 58.0, "max_range_km": 426, "connector_type": "CCS"},
        {"make": "Volkswagen", "model": "ID.3 Pro S", "year": 2024, "battery_capacity_kwh": 77.0, "max_range_km": 554, "connector_type": "CCS"},
        {"make": "Volkswagen", "model": "ID.4 Pro", "year": 2024, "battery_capacity_kwh": 77.0, "max_range_km": 520, "connector_type": "CCS"},
        {"make": "Volkswagen", "model": "ID.4 GTX", "year": 2024, "battery_capacity_kwh": 77.0, "max_range_km": 480, "connector_type": "CCS"},
        {"make": "Volkswagen", "model": "ID.5 Pro", "year": 2024, "battery_capacity_kwh": 77.0, "max_range_km": 513, "connector_type": "CCS"},

        # Nissan
        {"make": "Nissan", "model": "Leaf", "year": 2024, "battery_capacity_kwh": 40.0, "max_range_km": 270, "connector_type": "CHAdeMO"},
        {"make": "Nissan", "model": "Leaf e+", "year": 2024, "battery_capacity_kwh": 62.0, "max_range_km": 385, "connector_type": "CHAdeMO"},
        {"make": "Nissan", "model": "Ariya", "year": 2024, "battery_capacity_kwh": 87.0, "max_range_km": 533, "connector_type": "CCS"},

        # Hyundai
        {"make": "Hyundai", "model": "IONIQ 5", "year": 2024, "battery_capacity_kwh": 72.6, "max_range_km": 481, "connector_type": "CCS"},
        {"make": "Hyundai", "model": "IONIQ 6", "year": 2024, "battery_capacity_kwh": 77.4, "max_range_km": 614, "connector_type": "CCS"},
        {"make": "Hyundai", "model": "Kona Electric", "year": 2024, "battery_capacity_kwh": 64.0, "max_range_km": 484, "connector_type": "CCS"},

        # Kia
        {"make": "Kia", "model": "EV6", "year": 2024, "battery_capacity_kwh": 77.4, "max_range_km": 528, "connector_type": "CCS"},
        {"make": "Kia", "model": "EV6 GT", "year": 2024, "battery_capacity_kwh": 77.4, "max_range_km": 424, "connector_type": "CCS"},
        {"make": "Kia", "model": "e-Niro", "year": 2024, "battery_capacity_kwh": 64.8, "max_range_km": 463, "connector_type": "CCS"},
        {"make": "Kia", "model": "Soul EV", "year": 2024, "battery_capacity_kwh": 64.0, "max_range_km": 452, "connector_type": "CCS"},

        # Ford
        {"make": "Ford", "model": "Mustang Mach-E", "year": 2024, "battery_capacity_kwh": 88.0, "max_range_km": 610, "connector_type": "CCS"},
        {"make": "Ford", "model": "Mustang Mach-E GT", "year": 2024, "battery_capacity_kwh": 88.0, "max_range_km": 490, "connector_type": "CCS"},

        # Jaguar
        {"make": "Jaguar", "model": "I-PACE", "year": 2024, "battery_capacity_kwh": 90.0, "max_range_km": 470, "connector_type": "CCS"},

        # Porsche
        {"make": "Porsche", "model": "Taycan", "year": 2024, "battery_capacity_kwh": 93.4, "max_range_km": 484, "connector_type": "CCS"},
        {"make": "Porsche", "model": "Taycan Turbo", "year": 2024, "battery_capacity_kwh": 93.4, "max_range_km": 450, "connector_type": "CCS"},

        # Polestar
        {"make": "Polestar", "model": "2", "year": 2024, "battery_capacity_kwh": 78.0, "max_range_km": 540, "connector_type": "CCS"},
        {"make": "Polestar", "model": "3", "year": 2024, "battery_capacity_kwh": 111.0, "max_range_km": 610, "connector_type": "CCS"},

        # Volvo
        {"make": "Volvo", "model": "XC40 Recharge", "year": 2024, "battery_capacity_kwh": 78.0, "max_range_km": 418, "connector_type": "CCS"},
        {"make": "Volvo", "model": "C40 Recharge", "year": 2024, "battery_capacity_kwh": 78.0, "max_range_km": 444, "connector_type": "CCS"},

        # Mini
        {"make": "Mini", "model": "Cooper SE", "year": 2024, "battery_capacity_kwh": 32.6, "max_range_km": 233, "connector_type": "CCS"},

        # Genesis
        {"make": "Genesis", "model": "Electrified GV70", "year": 2024, "battery_capacity_kwh": 77.4, "max_range_km": 440, "connector_type": "CCS"},
        {"make": "Genesis", "model": "GV60", "year": 2024, "battery_capacity_kwh": 77.4, "max_range_km": 466, "connector_type": "CCS"},

        # Lucid (luxury)
        {"make": "Lucid", "model": "Air Dream Edition", "year": 2024, "battery_capacity_kwh": 118.0, "max_range_km": 837, "connector_type": "CCS"},

        # BYD
        {"make": "BYD", "model": "Atto 3", "year": 2024, "battery_capacity_kwh": 60.5, "max_range_km": 420, "connector_type": "CCS"},

        # MG
        {"make": "MG", "model": "4 EV", "year": 2024, "battery_capacity_kwh": 64.0, "max_range_km": 450, "connector_type": "CCS"},
        {"make": "MG", "model": "ZS EV", "year": 2024, "battery_capacity_kwh": 51.0, "max_range_km": 320, "connector_type": "CCS"},

        # Peugeot
        {"make": "Peugeot", "model": "e-208", "year": 2024, "battery_capacity_kwh": 50.0, "max_range_km": 362, "connector_type": "CCS"},
        {"make": "Peugeot", "model": "e-2008", "year": 2024, "battery_capacity_kwh": 50.0, "max_range_km": 345, "connector_type": "CCS"},

        # Renault
        {"make": "Renault", "model": "Zoe", "year": 2024, "battery_capacity_kwh": 52.0, "max_range_km": 395, "connector_type": "Type 2"},
        {"make": "Renault", "model": "Megane E-Tech", "year": 2024, "battery_capacity_kwh": 60.0, "max_range_km": 450, "connector_type": "CCS"},

        # Skoda
        {"make": "Skoda", "model": "Enyaq iV 60", "year": 2024, "battery_capacity_kwh": 62.0, "max_range_km": 390, "connector_type": "CCS"},
        {"make": "Skoda", "model": "Enyaq iV 80", "year": 2024, "battery_capacity_kwh": 82.0, "max_range_km": 520, "connector_type": "CCS"},

        # Cupra
        {"make": "Cupra", "model": "Born", "year": 2024, "battery_capacity_kwh": 77.0, "max_range_km": 548, "connector_type": "CCS"},

        # Fiat
        {"make": "Fiat", "model": "500e", "year": 2024, "battery_capacity_kwh": 42.0, "max_range_km": 320, "connector_type": "CCS"},

        # Honda
        {"make": "Honda", "model": "e", "year": 2024, "battery_capacity_kwh": 35.5, "max_range_km": 220, "connector_type": "CCS"},

        # Mazda
        {"make": "Mazda", "model": "MX-30", "year": 2024, "battery_capacity_kwh": 35.5, "max_range_km": 200, "connector_type": "CCS"},

        # Citroen
        {"make": "Citroen", "model": "e-C4", "year": 2024, "battery_capacity_kwh": 50.0, "max_range_km": 350, "connector_type": "CCS"},

        # Vauxhall
        {"make": "Vauxhall", "model": "Corsa-e", "year": 2024, "battery_capacity_kwh": 50.0, "max_range_km": 362, "connector_type": "CCS"},
        {"make": "Vauxhall", "model": "Mokka-e", "year": 2024, "battery_capacity_kwh": 50.0, "max_range_km": 338, "connector_type": "CCS"},

        # Lexus
        {"make": "Lexus", "model": "UX 300e", "year": 2024, "battery_capacity_kwh": 72.8, "max_range_km": 450, "connector_type": "CCS"},

        # DS Automobiles
        {"make": "DS", "model": "3 Crossback E-Tense", "year": 2024, "battery_capacity_kwh": 50.0, "max_range_km": 320, "connector_type": "CCS"},

        # Smart
        {"make": "Smart", "model": "EQfortwo", "year": 2024, "battery_capacity_kwh": 17.6, "max_range_km": 159, "connector_type": "CCS"},

        # Seat
        {"make": "Seat", "model": "Mii Electric", "year": 2024, "battery_capacity_kwh": 36.8, "max_range_km": 260, "connector_type": "CCS"},
    ]

    logger.info(f"Seeding {len(curated_cars)} curated car models...")

    for car_data in curated_cars:
        try:
            car_model = CarModel(**car_data)
            db.add(car_model)
            logger.debug(f"Added: {car_data['make']} {car_data['model']} ({car_data['year']})")
        except Exception as e:
            logger.error(f"Error adding car model {car_data}: {e}")
            continue

    try:
        db.commit()
        logger.info("Successfully committed all car models to the database")
    except Exception as e:
        logger.error(f"Error committing car models to database: {e}")
        db.rollback()
        raise

def main():
    """Main function to seed the database with curated car models."""
    logger.info("Starting car model seeding process...")

    db = SessionLocal()
    try:
        # Clean existing data
        clean_existing_car_models(db)

        # Seed new curated data
        seed_curated_car_models(db)

        # Verify the data
        count = db.query(CarModel).count()
        logger.info(f"Seeding completed successfully! Total car models in database: {count}")

    except Exception as e:
        logger.error(f"Error during seeding process: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
