import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration settings for the Tinder Scraper application."""
    
    # Base directory
    BASE_DIR = Path(__file__).resolve().parent
    
    # Tinder credentials
    TINDER_EMAIL = os.getenv('TINDER_EMAIL', '')
    TINDER_PASSWORD = os.getenv('TINDER_PASSWORD', '')
    
    # Google Sheets
    GOOGLE_SHEETS_ID = os.getenv('GOOGLE_SHEETS_ID', '1V8OfhSMltR7AgaC7g4QhRXDOU8meyePMcORF6L-0M1A')
    CREDENTIALS_FILE = os.getenv('CREDENTIALS_FILE', 'credentials.json')
    
    # File storage
    OUTPUT_DIR = os.getenv('OUTPUT_DIR', 'tinder_images')
    STATIC_DIR = os.path.join(BASE_DIR, 'static')
    TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(24).hex())
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    PORT = int(os.getenv('PORT', 5000))
    
    # Scraping settings
    MIN_IMAGES_PER_PROFILE = int(os.getenv('MIN_IMAGES_PER_PROFILE', 5))
    PROFILES_PER_LOCATION = int(os.getenv('PROFILES_PER_LOCATION', 20))
    HEADLESS = os.getenv('HEADLESS', 'True').lower() == 'true'
    
    # Target profiles settings
    TOTAL_TARGET_PROFILES = 25000
    PROFILES_PER_MILESTONE = 5000
    
    # Locations for scraping
    LOCATIONS = [
        'New York, USA', 'Los Angeles, USA', 'Chicago, USA', 'Houston, USA',
        'London, UK', 'Manchester, UK', 'Paris, France', 'Berlin, Germany',
        'Madrid, Spain', 'Barcelona, Spain', 'Rome, Italy', 'Milan, Italy',
        'Toronto, Canada', 'Vancouver, Canada', 'Sydney, Australia', 'Melbourne, Australia',
        'Tokyo, Japan', 'Osaka, Japan', 'Seoul, South Korea', 'Mumbai, India',
        'Delhi, India', 'Beijing, China', 'Shanghai, China', 'Singapore',
        'Bangkok, Thailand', 'Manila, Philippines', 'Jakarta, Indonesia',
        'Cairo, Egypt', 'Lagos, Nigeria', 'Nairobi, Kenya', 'Johannesburg, South Africa',
        'Rio de Janeiro, Brazil', 'Sao Paulo, Brazil', 'Buenos Aires, Argentina',
        'Mexico City, Mexico', 'Bogota, Colombia', 'Lima, Peru'
    ]
    
    @classmethod
    def get_location_list(cls):
        """Get the list of scraping locations."""
        return cls.LOCATIONS
    
    @classmethod
    def ensure_directories(cls):
        """Ensure all required directories exist."""
        os.makedirs(cls.OUTPUT_DIR, exist_ok=True)