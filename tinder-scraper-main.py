import os
import json
import time
import random
import logging
import requests
import pandas as pd
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from flask import Flask, render_template, request, jsonify
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("tinder_scraper.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
CONFIG = {
    'tinder_credentials': {
        'email': '',  # Fill in with your Tinder premium account email
        'password': ''  # Fill in with your Tinder premium account password
    },
    'google_sheets': {
        'sheet_id': '1V8OfhSMltR7AgaC7g4QhRXDOU8meyePMcORF6L-0M1A',
        'extracted_data_sheet': 'Extracted Data',
        'logs_sheet': 'Extraction Process Logs',
        'errors_sheet': 'Error Logs'
    },
    'locations': [
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
    ],
    'image_storage_path': 'tinder_images',
    'profiles_per_milestone': 5000,
    'profiles_per_location': 20,
    'min_images_per_profile': 5
}

# Create necessary directories
os.makedirs(CONFIG['image_storage_path'], exist_ok=True)

class GoogleSheetsIntegration:
    """Handles integration with Google Sheets for data storage and logging."""
    
    def __init__(self, sheet_id):
        self.sheet_id = sheet_id
        self.service = self._initialize_service()
        
    def _initialize_service(self):
        """Initialize the Google Sheets API service."""
        try:
            # If using service account
            SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
            creds = Credentials.from_service_account_file(
                'credentials.json', scopes=SCOPES)
            service = build('sheets', 'v4', credentials=creds)
            return service
        except Exception as e:
            logger.error(f"Failed to initialize Google Sheets service: {e}")
            return None
    
    def append_to_sheet(self, sheet_name, values):
        """Append data to a specific sheet."""
        if not self.service:
            logger.error("Google Sheets service not initialized.")
            return False
        
        try:
            range_name = f"{sheet_name}!A:Z"
            body = {
                'values': values
            }
            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.sheet_id, 
                range=range_name,
                valueInputOption='USER_ENTERED', 
                insertDataOption='INSERT_ROWS',
                body=body).execute()
            logger.info(f"Appended {result.get('updates').get('updatedRows')} rows to {sheet_name}")
            return True
        except HttpError as error:
            logger.error(f"Google Sheets API error: {error}")
            return False
    
    def log_extraction(self, profile_id, location, status, details):
        """Log extraction process details."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        values = [[timestamp, profile_id, location, status, details]]
        return self.append_to_sheet(CONFIG['google_sheets']['logs_sheet'], values)
    
    def log_error(self, error_type, error_message, location, profile_id=None):
        """Log error details."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        values = [[timestamp, error_type, error_message, location, profile_id]]
        return self.append_to_sheet(CONFIG['google_sheets']['errors_sheet'], values)
    
    def save_extracted_data(self, profile_data):
        """Save extracted profile data to the sheet."""
        # Flatten the profile data for sheet storage
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        location = profile_data.get('location', 'Unknown')
        profile_id = profile_data.get('profile_id', 'Unknown')
        image_count = len(profile_data.get('images', []))
        
        # Extract the labels into a flat structure
        labels = profile_data.get('labels', {})
        flattened_data = [
            timestamp, 
            profile_id, 
            location, 
            image_count,
            json.dumps(labels)  # Store full labels as JSON
        ]
        
        values = [flattened_data]
        return self.append_to_sheet(CONFIG['google_sheets']['extracted_data_sheet'], values)

class TinderScraper:
    """Handles Tinder profile scraping functionality."""
    
    def __init__(self, config, sheets_integration):
        self.config = config
        self.sheets = sheets_integration
        self.driver = None
        self.current_location_index = 0
        self.profiles_scraped_at_location = 0
        self.total_profiles_scraped = 0
        
    def initialize_driver(self):
        """Initialize the Selenium WebDriver with appropriate options."""
        try:
            options = webdriver.ChromeOptions()
            options.add_argument("--headless")  # Run in headless mode
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            
            # Add user agent to appear more like a regular browser
            options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
            
            self.driver = webdriver.Chrome(options=options)
            logger.info("WebDriver initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {e}")
            self.sheets.log_error("WebDriver Initialization", str(e), "N/A")
            return False
    
    def login_to_tinder(self):
        """Log in to Tinder using provided credentials."""
        try:
            # Navigate to Tinder login page
            self.driver.get("https://tinder.com/")
            
            # Wait for login button to appear
            WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Log in')]"))
            ).click()
            
            # Handle login specifics (this is simplified and would need to be adapted)
            # Different login methods might require different handling
            
            # Assuming email login option is available
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Log in with email')]"))
            ).click()
            
            # Enter email
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@name='email']"))
            ).send_keys(self.config['tinder_credentials']['email'])
            
            # Enter password
            self.driver.find_element(By.XPATH, "//input[@name='password']").send_keys(
                self.config['tinder_credentials']['password']
            )
            
            # Click submit
            self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
            
            # Wait for login to complete (check for main Tinder interface)
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'main')]"))
            )
            
            logger.info("Successfully logged in to Tinder")
            return True
        except TimeoutException as e:
            logger.error(f"Timeout while logging in to Tinder: {e}")
            self.sheets.log_error("Login Timeout", str(e), "N/A")
            return False
        except Exception as e:
            logger.error(f"Failed to log in to Tinder: {e}")
            self.sheets.log_error("Login Error", str(e), "N/A")
            return False
    
    def change_location(self):
        """Change the current location in Tinder."""
        try:
            # Check if we need to change location based on profiles scraped
            if self.profiles_scraped_at_location >= self.config['profiles_per_location']:
                # Reset counter and move to next location
                self.profiles_scraped_at_location = 0
                self.current_location_index = (self.current_location_index + 1) % len(self.config['locations'])
            
            current_location = self.config['locations'][self.current_location_index]
            
            # Navigate to location settings
            self.driver.get("https://tinder.com/app/settings/plus")
            
            # Wait for location change option (Passport)
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Location')]"))
            ).click()
            
            # Enter new location
            location_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Search']"))
            )
            location_input.clear()
            location_input.send_keys(current_location)
            
            # Wait for location suggestions and click the first one
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'location-result')]"))
            ).click()
            
            # Confirm location change
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Apply')]"))
            ).click()
            
            # Wait for location change to take effect
            time.sleep(5)
            
            logger.info(f"Location changed to: {current_location}")
            self.sheets.log_extraction("N/A", current_location, "LOCATION_CHANGE", f"Changed location to {current_location}")
            return current_location
        except Exception as e:
            logger.error(f"Failed to change location: {e}")
            self.sheets.log_error("Location Change", str(e), "N/A")
            return None
    
    def scrape_profile(self):
        """Scrape the current visible profile."""
        try:
            # Get current location
            current_location = self.config['locations'][self.current_location_index]
            city_name = current_location.split(',')[0].replace(' ', '').lower()
            
            # Extract profile information
            profile_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'profileCard')]"))
            )
            
            # Extract name and age
            name_age = self.driver.find_element(By.XPATH, "//div[contains(@class, 'profileCard__nameAge')]").text
            name = name_age.split(',')[0]
            
            # Generate profile ID
            profile_id = f"{str(self.total_profiles_scraped + 1).zfill(5)}"
            
            # Extract bio if available
            try:
                bio = self.driver.find_element(By.XPATH, "//div[contains(@class, 'profileCard__bio')]").text
            except NoSuchElementException:
                bio = ""
            
            # Create profile data structure
            profile_data = {
                'profile_id': profile_id,
                'location': current_location,
                'name': name,
                'bio': bio,
                'images': [],
                'labels': {}  # Will be filled by the labeling process
            }
            
            # Click to see profile details and images
            profile_element.click()
            
            # Wait for profile details to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'profileContent')]"))
            )
            
            # Find all image elements
            image_elements = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'profileCard__slider')]/div/div/img")
            
            # If we don't have enough images, skip this profile
            if len(image_elements) < self.config['min_images_per_profile']:
                logger.info(f"Profile {profile_id} has fewer than {self.config['min_images_per_profile']} images, skipping")
                self.sheets.log_extraction(profile_id, current_location, "SKIPPED", f"Insufficient images: {len(image_elements)}")
                
                # Close profile details
                self.driver.find_element(By.XPATH, "//button[contains(@class, 'close')]").click()
                return None
            
            # Download images
            for i, img_element in enumerate(image_elements):
                img_url = img_element.get_attribute('src')
                if img_url:
                    # Create filename according to convention: imageId-cityName-profileId
                    image_id = str(i + 1).zfill(6)
                    filename = f"{image_id}-{city_name}-{profile_id}.jpg"
                    file_path = os.path.join(self.config['image_storage_path'], filename)
                    
                    # Download the image
                    try:
                        response = requests.get(img_url, stream=True)
                        if response.status_code == 200:
                            with open(file_path, 'wb') as file:
                                for chunk in response.iter_content(1024):
                                    file.write(chunk)
                            profile_data['images'].append({
                                'image_id': image_id,
                                'filename': filename,
                                'path': file_path
                            })
                            logger.info(f"Downloaded image: {filename}")
                        else:
                            logger.warning(f"Failed to download image {i+1} for profile {profile_id}: Status code {response.status_code}")
                    except Exception as e:
                        logger.error(f"Error downloading image {i+1} for profile {profile_id}: {e}")
                        self.sheets.log_error("Image Download", str(e), current_location, profile_id)
            
            # Close profile details
            self.driver.find_element(By.XPATH, "//button[contains(@class, 'close')]").click()
            
            # Update counters
            self.profiles_scraped_at_location += 1
            self.total_profiles_scraped += 1
            
            logger.info(f"Successfully scraped profile {profile_id} with {len(profile_data['images'])} images")
            self.sheets.log_extraction(profile_id, current_location, "SCRAPED", f"Scraped {len(profile_data['images'])} images")
            
            return profile_data
        except Exception as e:
            logger.error(f"Error scraping profile: {e}")
            self.sheets.log_error("Profile Scraping", str(e), current_location)
            return None
    
    def label_profile(self, profile_data):
        """Generate AI-based labels for the profile."""
        try:
            # In a real implementation, this would involve either:
            # 1. Making API calls to an AI service for automated labeling
            # 2. Storing the profile for manual labeling
            
            # For this implementation, we'll create placeholder labels
            # In a real scenario, these would be derived from the images and profile data
            
            # Basic demographic estimates (random for demo purposes)
            age_min = random.randint(18, 35)
            age_max = age_min + random.randint(0, 5)
            height_min = random.randint(150, 175)
            height_max = height_min + random.randint(0, 10)
            
            # Create the label structure as shown in the example
            labels = {
                "celibacy": [random.randint(0, 50), random.randint(50, 100)],
                "cooperativeness": [random.randint(30, 70), random.randint(70, 100)],
                "intelligence": [random.randint(50, 80), random.randint(80, 100)],
                "weight": [random.randint(45, 70), random.randint(50, 75)],
                "waist": [random.randint(60, 90), random.randint(65, 95)],
                "bust": [random.randint(80, 95), random.randint(85, 100)],
                "hips": [random.randint(85, 100), random.randint(90, 105)],
                "gender": [
                    {"name": "male", "value": [random.randint(0, 10), random.randint(5, 15)]},
                    {"name": "female", "value": [random.randint(85, 95), random.randint(90, 100)]}
                ],
                "age": [age_min, age_max],
                "height": [height_min, height_max],
                "face": [random.randint(50, 80), random.randint(70, 90)],
                "ethnicity": self._generate_ethnicity_labels(),
                "big_spender": [random.randint(20, 60), random.randint(50, 90)],
                "presentable": [random.randint(50, 80), random.randint(70, 100)],
                "muscle_percentage": [random.randint(5, 20), random.randint(10, 25)],
                "fat_percentage": [random.randint(10, 25), random.randint(15, 30)],
                "dominance": [random.randint(30, 70), random.randint(50, 90)],
                "power": [random.randint(30, 70), random.randint(50, 90)],
                "confidence": [random.randint(40, 80), random.randint(60, 95)]
            }
            
            profile_data['labels'] = labels
            logger.info(f"Generated labels for profile {profile_data['profile_id']}")
            return profile_data
        except Exception as e:
            logger.error(f"Error labeling profile {profile_data['profile_id']}: {e}")
            self.sheets.log_error("Profile Labeling", str(e), profile_data.get('location', 'Unknown'), profile_data.get('profile_id', 'Unknown'))
            return profile_data
    
    def _generate_ethnicity_labels(self):
        """Generate random ethnicity labels."""
        ethnicities = [
            "Sub-Saharan African",
            "North African/Middle Eastern",
            "European",
            "East Asian",
            "South Asian",
            "Southeast Asian",
            "Central Asian",
            "Pacific Islander",
            "Indigenous Peoples of the Americas",
            "Melanesian",
            "Afro-Caribbean/Afro-Latinx",
            "Mixed/Multiracial"
        ]
        
        # Create a list of ethnicity labels with random values
        ethnicity_labels = []
        
        # Randomly select a primary ethnicity with higher values
        primary_ethnicity = random.choice(ethnicities)
        primary_min = random.randint(70, 85)
        primary_max = random.randint(primary_min, 95)
        
        for ethnicity in ethnicities:
            if ethnicity == primary_ethnicity:
                ethnicity_labels.append({
                    "name": ethnicity,
                    "value": [primary_min, primary_max]
                })
            else:
                # Other ethnicities get lower values
                min_val = random.randint(1, 20)
                max_val = random.randint(min_val, min_val + 10)
                ethnicity_labels.append({
                    "name": ethnicity,
                    "value": [min_val, max_val]
                })
        
        return ethnicity_labels
    
    def swipe_left(self):
        """Swipe left on the current profile."""
        try:
            # Find and click the "Nope" button
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'nope')]"))
            ).click()
            logger.debug("Swiped left")
            return True
        except Exception as e:
            logger.error(f"Error swiping left: {e}")
            return False
    
    def run_scraping_session(self, target_profiles=100):
        """Run a complete scraping session."""
        if not self.initialize_driver():
            return False
        
        try:
            # Login to Tinder
            if not self.login_to_tinder():
                return False
            
            # Initial location change
            current_location = self.change_location()
            if not current_location:
                return False
            
            # Scrape profiles until target is reached
            profiles_scraped = 0
            
            while profiles_scraped < target_profiles:
                # Check if we need to change location
                if self.profiles_scraped_at_location >= self.config['profiles_per_location']:
                    current_location = self.change_location()
                    if not current_location:
                        logger.warning("Failed to change location, continuing with current location")
                
                # Scrape the current profile
                profile_data = self.scrape_profile()
                
                if profile_data and len(profile_data['images']) >= self.config['min_images_per_profile']:
                    # Label the profile
                    profile_data = self.label_profile(profile_data)
                    
                    # Save to Google Sheets
                    self.sheets.save_extracted_data(profile_data)
                    
                    profiles_scraped += 1
                
                # Swipe left and move to next profile
                self.swipe_left()
                
                # Add a small delay to avoid hitting rate limits
                time.sleep(random.uniform(1, 3))
            
            logger.info(f"Scraping session completed. Scraped {profiles_scraped} profiles.")
            return True
        except Exception as e:
            logger.error(f"Error in scraping session: {e}")
            self.sheets.log_error("Scraping Session", str(e), "Multiple")
            return False
        finally:
            # Always close the WebDriver
            if self.driver:
                self.driver.quit()

# Flask web application for the UI
app = Flask(__name__)

# Create instances
sheets_integration = GoogleSheetsIntegration(CONFIG['google_sheets']['sheet_id'])
tinder_scraper = TinderScraper(CONFIG, sheets_integration)

@app.route('/')
def index():
    """Render the main dashboard."""
    return render_template('index.html')

@app.route('/data-center')
def data_center():
    """Render the data center page."""
    return render_template('data_center.html')

@app.route('/logs')
def logs():
    """Render the logs page."""
    return render_template('logs.html')

@app.route('/stryke-center')
def stryke_center():
    """Render the statistics and reports page."""
    return render_template('stryke_center.html')

@app.route('/api/start-scraping', methods=['POST'])
def start_scraping():
    """API endpoint to start a scraping session."""
    data = request.json
    target_profiles = data.get('target_profiles', 100)
    
    # Start scraping in a separate thread
    import threading
    thread = threading.Thread(target=tinder_scraper.run_scraping_session, args=(target_profiles,))
    thread.daemon = True
    thread.start()
    
    return jsonify({"status": "success", "message": f"Started scraping session for {target_profiles} profiles"})

@app.route('/api/get-stats')
def get_stats():
    """API endpoint to get scraping statistics."""
    # In a real implementation, this would fetch actual statistics from the database
    return jsonify({
        "totalProfiles": tinder_scraper.total_profiles_scraped,
        "currentMilestone": min(5, tinder_scraper.total_profiles_scraped // CONFIG['profiles_per_milestone'] + 1),
        "profilesInCurrentMilestone": tinder_scraper.total_profiles_scraped % CONFIG['profiles_per_milestone'],
        "currentLocation": CONFIG['locations'][tinder_scraper.current_location_index],
        "profilesAtCurrentLocation": tinder_scraper.profiles_scraped_at_location
    })

@app.route('/api/get-recent-profiles')
def get_recent_profiles():
    """API endpoint to get recently scraped profiles."""
    # In a real implementation, this would fetch data from the database
    # Mocking data for demonstration
    return jsonify({
        "profiles": [
            {
                "profile_id": "00001",
                "location": "New York, USA",
                "image_count": 6,
                "scraped_at": "2025-03-07 10:15:22"
            },
            {
                "profile_id": "00002",
                "location": "New York, USA",
                "image_count": 5,
                "scraped_at": "2025-03-07 10:18:45"
            }
        ]
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
