"""
Seed script to populate the cars table with UK electric vehicles from ev-database.org
"""

import requests
from bs4 import BeautifulSoup
import re
import time
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import SessionLocal
from app.models import Car
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EVDatabaseScraper:
    def __init__(self):
        self.base_url = "https://ev-database.org/uk"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def get_car_list_page(self, page=1):
        """Fetch a page of cars from the EV database listing."""
        url = f"{self.base_url}/"
        if page > 1:
            url += f"?page={page}"

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Error fetching page {page}: {e}")
            return None

    def parse_car_listings(self, html_content):
        """Parse car listings from the main page HTML."""
        soup = BeautifulSoup(html_content, 'html.parser')
        cars = []

        # Find all car listing containers
        car_containers = soup.find_all('div', class_='list-item')
        if not car_containers:
            # Fallback: look for links with car URLs
            car_links = soup.find_all('a', href=re.compile(r'/uk/car/\d+/'))
            car_containers = []
            for link in car_links:
                # Try to find the parent container that has car info
                parent = link.find_parent('div') or link.find_parent('article')
                if parent:
                    car_containers.append(parent)

        for container in car_containers:
            try:
                car_data = self.extract_basic_car_info(container)
                if car_data:
                    cars.append(car_data)
            except Exception as e:
                logger.warning(f"Error parsing car container: {e}")
                continue

        return cars

    def extract_basic_car_info(self, container):
        """Extract basic car information from a listing container."""
        car_data = {}

        # Try to find car name/title with multiple strategies
        title_elem = (
            container.find('h2') or
            container.find('h3') or
            container.find('h1') or
            container.find('a', href=re.compile(r'/uk/car/\d+/')) or
            container.find('div', class_=re.compile(r'title|name', re.I)) or
            container.find('span', class_=re.compile(r'title|name', re.I))
        )

        if not title_elem:
            # Last resort: try to find any text that looks like a car name
            all_text = container.get_text(strip=True)
            lines = [line.strip() for line in all_text.split('\n') if line.strip()]
            if lines:
                title_text = lines[0]  # Take first non-empty line
            else:
                return None
        else:
            title_text = title_elem.get_text(strip=True)

        # Clean up title text - remove common prefixes/suffixes
        title_text = re.sub(r'^(NEW\s+|USED\s+)', '', title_text, flags=re.IGNORECASE)
        title_text = re.sub(r'\s+(available|from|starting)', '', title_text, flags=re.IGNORECASE)

        car_data['full_name'] = title_text

        # Extract make and model from title
        make_model = self.parse_make_model(title_text)
        car_data.update(make_model)

        # Try to extract specs from the container text
        container_text = container.get_text()

        # Extract range (miles)
        range_match = re.search(r'Range[*\s]*(\d+)\s*mi', container_text)
        if range_match:
            range_miles = int(range_match.group(1))
            car_data['max_range_km'] = round(range_miles * 1.60934, 1)  # Convert to km

        # Extract battery capacity
        battery_match = re.search(r'Battery[*\s]*(\d+\.?\d*)\s*kWh', container_text)
        if battery_match:
            car_data['battery_capacity_kwh'] = float(battery_match.group(1))

        # Extract year from availability info
        year_match = re.search(r'since\s+\w+\s+(\d{4})', container_text)
        if year_match:
            car_data['year'] = int(year_match.group(1))
        else:
            car_data['year'] = 2024  # Default to current year

        # Extract rapid charge info for connector hints
        rapid_charge_match = re.search(r'Rapidcharge[*\s]*(\d+)\s*kW', container_text)
        if rapid_charge_match:
            rapid_charge_kw = int(rapid_charge_match.group(1))
            # Most cars with >100kW rapid charging support CCS, others might be CHAdeMO/CCS
            if rapid_charge_kw >= 100:
                car_data['connector_type'] = 'CCS'
            else:
                car_data['connector_type'] = 'CCS/CHAdeMO'

        return car_data

    def parse_make_model(self, title):
        """Parse make and model from car title with improved logic."""
        # Clean up the title - remove duplicates and normalize
        original_title = title

        # Remove parentheses content like (2025)
        title = re.sub(r'\([^)]*\)', '', title).strip()

        # Remove extra whitespace and normalize
        title = re.sub(r'\s+', ' ', title).strip()

        # Handle obvious duplications like "Mercedes-BenzCLA 250+Mercedes-Benz CLA 250+"
        # Split on manufacturer name repetitions
        if title.count('Mercedes-Benz') > 1:
            # Take the first occurrence and clean it
            parts = title.split('Mercedes-Benz', 1)
            if len(parts) > 1:
                title = f"Mercedes-Benz{parts[1]}"

        # Handle other common duplications
        common_makes = ['Tesla', 'BMW', 'Audi', 'Volkswagen', 'Nissan', 'Hyundai', 'Kia', 'Ford', 'Porsche', 'Volvo']
        for make in common_makes:
            if title.count(make) > 1:
                parts = title.split(make, 1)
                if len(parts) > 1:
                    title = f"{make}{parts[1]}"

        # Remove special characters that might cause concatenation
        title = re.sub(r'[+\-_]+', ' ', title)
        title = re.sub(r'\s+', ' ', title).strip()

        # Comprehensive manufacturer mapping with improved parsing
        manufacturer_patterns = {
            r'^(Mercedes-Benz|Mercedes)\s*': 'Mercedes-Benz',
            r'^(BMW)\s*': 'BMW',
            r'^(Audi)\s*': 'Audi',
            r'^(Volkswagen|VW)\s*': 'Volkswagen',
            r'^(Tesla)\s*': 'Tesla',
            r'^(Nissan)\s*': 'Nissan',
            r'^(Hyundai)\s*': 'Hyundai',
            r'^(Kia)\s*': 'Kia',
            r'^(Ford)\s*': 'Ford',
            r'^(Porsche)\s*': 'Porsche',
            r'^(Volvo)\s*': 'Volvo',
            r'^(Jaguar)\s*': 'Jaguar',
            r'^(Land Rover)\s*': 'Land Rover',
            r'^(Mini)\s*': 'Mini',
            r'^(Polestar)\s*': 'Polestar',
            r'^(Lucid)\s*': 'Lucid',
            r'^(Genesis)\s*': 'Genesis',
            r'^(Lexus)\s*': 'Lexus',
            r'^(Infiniti)\s*': 'Infiniti',
            r'^(Acura)\s*': 'Acura',
            r'^(Cadillac)\s*': 'Cadillac',
            r'^(Chevrolet|Chevy)\s*': 'Chevrolet',
            r'^(GMC)\s*': 'GMC',
            r'^(Rivian)\s*': 'Rivian',
            r'^(Fisker)\s*': 'Fisker',
            r'^(MG)\s*': 'MG',
            r'^(BYD)\s*': 'BYD',
            r'^(Peugeot)\s*': 'Peugeot',
            r'^(Citroën|Citroen)\s*': 'Citroën',
            r'^(Renault)\s*': 'Renault',
            r'^(Dacia)\s*': 'Dacia',
            r'^(Skoda|Škoda)\s*': 'Škoda',
            r'^(SEAT)\s*': 'SEAT',
            r'^(Cupra)\s*': 'Cupra',
            r'^(Fiat)\s*': 'Fiat',
            r'^(Alfa Romeo)\s*': 'Alfa Romeo',
            r'^(Maserati)\s*': 'Maserati',
            r'^(Ferrari)\s*': 'Ferrari',
            r'^(Lamborghini)\s*': 'Lamborghini',
            r'^(Bentley)\s*': 'Bentley',
            r'^(Rolls-Royce)\s*': 'Rolls-Royce',
            r'^(Vauxhall)\s*': 'Vauxhall',
            r'^(Opel)\s*': 'Opel',
            r'^(Jeep)\s*': 'Jeep',
            r'^(DS Automobiles|DS)\s*': 'DS Automobiles',
            r'^(Smart)\s*': 'Smart',
            r'^(Mazda)\s*': 'Mazda',
            r'^(Subaru)\s*': 'Subaru',
            r'^(Toyota)\s*': 'Toyota',
            r'^(Honda)\s*': 'Honda',
            r'^(Mitsubishi)\s*': 'Mitsubishi',
            r'^(Isuzu)\s*': 'Isuzu',
            r'^(Alpine)\s*': 'Alpine',
        }

        make = None
        model = title

        # Try to match manufacturer patterns
        for pattern, manufacturer in manufacturer_patterns.items():
            match = re.match(pattern, title, re.IGNORECASE)
            if match:
                make = manufacturer
                # Extract model by removing the matched manufacturer
                model = title[match.end():].strip()
                break

        # If no manufacturer found, try simple word splitting
        if not make:
            parts = title.split(' ', 1)
            if len(parts) >= 2:
                make = parts[0].title()  # Capitalize first letter
                model = parts[1]
            else:
                make = 'Unknown'
                model = title

        # Clean up the model name
        if model:
            # Remove any remaining manufacturer references
            model = re.sub(rf'^{re.escape(make)}\s*', '', model, flags=re.IGNORECASE).strip()
            # Remove duplicate words and normalize
            model_words = model.split()
            seen_words = set()
            clean_words = []
            for word in model_words:
                word_lower = word.lower()
                if word_lower not in seen_words:
                    clean_words.append(word)
                    seen_words.add(word_lower)
            model = ' '.join(clean_words)

        # Fallback if model is empty
        if not model or model.strip() == '':
            model = 'Unknown'

        logger.debug(f"Parsed '{original_title}' -> Make: '{make}', Model: '{model}'")
        return {'make': make, 'model': model}

    def scrape_cars(self, max_pages=5):
        """Scrape cars from multiple pages."""
        all_cars = []

        for page in range(1, max_pages + 1):
            logger.info(f"Scraping page {page}...")

            html = self.get_car_list_page(page)
            if not html:
                logger.warning(f"Failed to fetch page {page}")
                continue

            cars = self.parse_car_listings(html)
            if not cars:
                logger.info(f"No cars found on page {page}, stopping.")
                break

            all_cars.extend(cars)
            logger.info(f"Found {len(cars)} cars on page {page}")

            # Be respectful to the server
            time.sleep(2)

        return all_cars

def clean_existing_cars(db: Session):
    """Remove existing seeded cars to avoid duplicates."""
    logger.info("Cleaning existing seeded cars...")

    # Delete cars that don't have a user_id (seeded cars)
    result = db.execute(text("DELETE FROM cars WHERE user_id IS NULL"))
    db.commit()

    logger.info(f"Removed {result.rowcount} existing seeded cars")

def seed_cars_from_scraper():
    """Main function to scrape and seed cars."""
    db = SessionLocal()

    try:
        logger.info("Starting EV database scraping...")

        # Clean existing seeded data
        clean_existing_cars(db)

        # Initialize scraper
        scraper = EVDatabaseScraper()

        # Scrape cars (limit to 3 pages for initial seed)
        cars_data = scraper.scrape_cars(max_pages=3)

        if not cars_data:
            logger.error("No cars found to seed!")
            return

        logger.info(f"Found {len(cars_data)} cars to seed")

        # Insert cars into database
        cars_inserted = 0
        for car_data in cars_data:
            try:
                # Create car instance (user_id=None for seeded cars)
                car = Car(
                    user_id=None,  # Seeded cars don't belong to users
                    make=car_data.get('make', 'Unknown'),
                    model=car_data.get('model', 'Unknown'),
                    year=car_data.get('year', 2024),
                    battery_capacity_kwh=car_data.get('battery_capacity_kwh'),
                    max_range_km=car_data.get('max_range_km'),
                    connector_type=car_data.get('connector_type'),
                    nickname=car_data.get('full_name', ''),  # Store full name as nickname
                    is_active=True
                )

                db.add(car)
                cars_inserted += 1

                if cars_inserted % 10 == 0:
                    db.commit()  # Commit in batches
                    logger.info(f"Inserted {cars_inserted} cars...")

            except Exception as e:
                logger.error(f"Error inserting car {car_data}: {e}")
                continue

        # Final commit
        db.commit()
        logger.info(f"Successfully seeded {cars_inserted} cars!")

        # Show sample of seeded cars
        sample_cars = db.query(Car).filter(Car.user_id.is_(None)).limit(5).all()
        logger.info("Sample seeded cars:")
        for car in sample_cars:
            logger.info(f"  {car.make} {car.model} ({car.year}) - Range: {car.max_range_km}km, Battery: {car.battery_capacity_kwh}kWh")

    except Exception as e:
        logger.error(f"Error during seeding: {e}")
        db.rollback()
    finally:
        db.close()

def add_manual_popular_cars(db: Session):
    """Add some popular UK EVs manually in case scraping doesn't get them all."""

    popular_cars = [
        {
            'make': 'Tesla', 'model': 'Model 3', 'year': 2024,
            'battery_capacity_kwh': 75.0, 'max_range_km': 491, 'connector_type': 'CCS'
        },
        {
            'make': 'Tesla', 'model': 'Model Y', 'year': 2024,
            'battery_capacity_kwh': 75.0, 'max_range_km': 533, 'connector_type': 'CCS'
        },
        {
            'make': 'Nissan', 'model': 'Leaf', 'year': 2024,
            'battery_capacity_kwh': 62.0, 'max_range_km': 385, 'connector_type': 'CHAdeMO'
        },
        {
            'make': 'Hyundai', 'model': 'Ioniq 5', 'year': 2024,
            'battery_capacity_kwh': 77.4, 'max_range_km': 507, 'connector_type': 'CCS'
        },
        {
            'make': 'Kia', 'model': 'EV6', 'year': 2024,
            'battery_capacity_kwh': 77.4, 'max_range_km': 528, 'connector_type': 'CCS'
        },
        {
            'make': 'Volkswagen', 'model': 'ID.4', 'year': 2024,
            'battery_capacity_kwh': 77.0, 'max_range_km': 520, 'connector_type': 'CCS'
        },
        {
            'make': 'BMW', 'model': 'iX3', 'year': 2024,
            'battery_capacity_kwh': 80.0, 'max_range_km': 460, 'connector_type': 'CCS'
        },
        {
            'make': 'Audi', 'model': 'e-tron GT', 'year': 2024,
            'battery_capacity_kwh': 93.4, 'max_range_km': 488, 'connector_type': 'CCS'
        },
        {
            'make': 'Polestar', 'model': '2', 'year': 2024,
            'battery_capacity_kwh': 78.0, 'max_range_km': 540, 'connector_type': 'CCS'
        },
        {
            'make': 'MG', 'model': 'ZS EV', 'year': 2024,
            'battery_capacity_kwh': 72.6, 'max_range_km': 440, 'connector_type': 'CCS'
        }
    ]

    logger.info("Adding popular UK EVs manually...")

    for car_data in popular_cars:
        # Check if this car already exists
        existing = db.query(Car).filter(
            Car.make == car_data['make'],
            Car.model == car_data['model'],
            Car.user_id.is_(None)
        ).first()

        if not existing:
            car = Car(user_id=None, **car_data, is_active=True)
            db.add(car)

    db.commit()
    logger.info("Added popular UK EVs")

if __name__ == "__main__":
    logger.info("Starting car seeding process...")

    try:
        # Try scraping first
        seed_cars_from_scraper()

        # Add manual popular cars as backup/supplement
        db = SessionLocal()
        add_manual_popular_cars(db)
        db.close()

        logger.info("Car seeding completed successfully!")

    except Exception as e:
        logger.error(f"Car seeding failed: {e}")
        raise
