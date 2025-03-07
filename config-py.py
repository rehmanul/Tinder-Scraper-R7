import os
from typing import List

class Config:
    """Configuration settings for the Tinder Scraper application."""
    
    # Tinder credentials
    TINDER_EMAIL = os.environ.get('TINDER_EMAIL', '')
    TINDER_PASSWORD = os.environ.get('TINDER_PASSWORD', '')
    
    # Google Sheets integration
    GOOGLE_SHEETS_ID = os.environ.get('GOOGLE_SHEETS_ID', '1V8OfhSMltR7AgaC7g4QhRXDOU8meyePMcORF6L-0M1A')
    CREDENTIALS_FILE = os.environ.get('CREDENTIALS_FILE', 'credentials.json')
    
    # File paths
    OUTPUT_DIR = os.environ.get('OUTPUT_DIR', 'tinder_images')
    STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    
    # Scraping settings
    MIN_IMAGES_PER_PROFILE = 5
    PROFILES_PER_LOCATION = 20
    PROFILES_PER_MILESTONE = 5000
    TOTAL_TARGET_PROFILES = 25000
    
    # Locations to scrape (global cities)
    LOCATIONS: List[str] = [
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
    
    # Label attributes
    LABEL_ATTRIBUTES = {
        'numeric_ranges': [
            'celibacy', 'cooperativeness', 'intelligence', 
            'weight', 'waist', 'bust', 'hips',
            'age', 'height', 'face', 
            'big_spender', 'presentable',
            'muscle_percentage', 'fat_percentage', 
            'dominance', 'power', 'confidence'
        ],
        'categorical': [
            'gender', 'ethnicity'
        ]
    }
    
    # Google Sheets sheet names
    EXTRACTED_DATA_SHEET = 'Extracted Data'
    LOGS_SHEET = 'Extraction Process Logs'
    ERROR_LOGS_SHEET = 'Error Logs'
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'tinder-scraper-secret-key')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Image processing settings
    IMAGE_QUALITY = 85  # JPEG quality for compressed images
    MAX_IMAGE_WIDTH = 1200  # Maximum width for images
    THUMBNAIL_SIZE = (300, 300)  # Size for thumbnails
