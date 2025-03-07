import os
import time
import random
import logging
import requests
import urllib.parse
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException, 
    StaleElementReferenceException,
    ElementClickInterceptedException
)

# Set up logging
logger = logging.getLogger(__name__)

class TinderScraper:
    """Core Tinder scraping functionality.
    
    This class handles the interaction with Tinder website to scrape profiles
    and download images. It uses Selenium WebDriver for browser automation.
    """
    
    def __init__(self, 
                 email: str, 
                 password: str, 
                 output_dir: str = "tinder_images",
                 headless: bool = False,
                 min_images_per_profile: int = 5,
                 profiles_per_location: int = 20,
                 wait_time_between_actions: Tuple[float, float] = (0.5, 2.0),
                 google_sheets_integration=None):
        """Initialize the TinderScraper.
        
        Args:
            email: Tinder account email
            password: Tinder account password
            output_dir: Directory to save scraped images
            headless: Whether to run browser in headless mode
            min_images_per_profile: Minimum images required per profile
            profiles_per_location: Number of profiles to scrape per location
            wait_time_between_actions: Range (min, max) of seconds to wait between actions
            google_sheets_integration: Google Sheets Integration instance
        """
        self.email = email
        self.password = password
        self.output_dir = output_dir
        self.headless = headless
        self.min_images_per_profile = min_images_per_profile
        self.profiles_per_location = profiles_per_location
        self.wait_time_between_actions = wait_time_between_actions
        self.google_sheets = google_sheets_integration
        
        self.driver = None
        self.is_logged_in = False
        self.current_location = None
        self.profiles_scraped_in_current_location = 0
        self.total_profiles_scraped = 0
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
    
    def initialize_driver(self) -> bool:
        """Initialize the Selenium WebDriver.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            options = webdriver.ChromeOptions()
            
            if self.headless:
                options.add_argument("--headless")
            
            # Common options for stability
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            
            # Set user agent to appear as a regular browser
            options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
            
            # Initialize the driver
            self.driver = webdriver.Chrome(options=options)
            
            # Set page load timeout
            self.driver.set_page_load_timeout(30)
            
            logger.info("WebDriver initialized successfully")
            
            if self.google_sheets:
                self.google_sheets.log_extraction(
                    "N/A", "N/A", "SYSTEM", "WebDriver initialized successfully")
            
            return True
        
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {e}")
            
            if self.google_sheets:
                self.google_sheets.log_error(
                    "System", f"WebDriver initialization failed: {e}", "N/A")
            
            return False
    
    def _random_wait(self) -> None:
        """Wait for a random amount of time between actions to appear more human-like."""
        min_wait, max_wait = self.wait_time_between_actions
        wait_time = random.uniform(min_wait, max_wait)
        time.sleep(wait_time)
    
    def login(self) -> bool:
        """Log in to Tinder using provided credentials.
        
        Returns:
            bool: True if login was successful, False otherwise
        """
        if not self.driver:
            logger.error("Cannot login: WebDriver not initialized")
            return False
        
        try:
            # Navigate to Tinder
            self.driver.get("https://tinder.com/")
            logger.info("Navigated to Tinder homepage")
            
            # Wait for the login button to appear and click it
            WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//div[text()='Log in']"))
            ).click()
            logger.info("Clicked on Login button")
            
            self._random_wait()
            
            # Look for the login with email button and click it
            try:
                email_login_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Log in with email')]"))
                )
                email_login_button.click()
                logger.info("Selected email login method")
            except TimeoutException:
                # Try alternative login methods if email login is not immediately visible
                more_options_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'More Options')]"))
                )
                more_options_button.click()
                logger.info("Clicked 'More Options' for login")
                
                self._random_wait()
                
                email_login_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Log in with email')]"))
                )
                email_login_button.click()
                logger.info("Selected email login method")
            
            self._random_wait()
            
            # Enter email
            email_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@name='email']"))
            )
            email_input.clear()
            email_input.send_keys(self.email)
            logger.info("Entered email")
            
            self._random_wait()
            
            # Enter password
            password_input = self.driver.find_element(By.XPATH, "//input[@name='password']")
            password_input.clear()
            password_input.send_keys(self.password)
            logger.info("Entered password")
            
            self._random_wait()
            
            # Click login button
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            logger.info("Submitted login form")
            
            # Wait for successful login by looking for the main app interface
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'App__body')]"))
            )
            
            # Handle potential popups that might appear after login
            self._handle_post_login_popups()
            
            self.is_logged_in = True
            logger.info("Successfully logged in to Tinder")
            
            if self.google_sheets:
                self.google_sheets.log_extraction(
                    "N/A", "N/A", "SYSTEM", "Successfully logged in to Tinder")
            
            return True
            
        except TimeoutException as e:
            logger.error(f"Timeout during login process: {e}")
            
            if self.google_sheets:
                self.google_sheets.log_error(
                    "Login", f"Timeout during login: {e}", "N/A")
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to login to Tinder: {e}")
            
            if self.google_sheets:
                self.google_sheets.log_error(
                    "Login", f"Login failed: {e}", "N/A")
            
            return False
    
    def _handle_post_login_popups(self) -> None:
        """Handle various popups that might appear after login."""
        try:
            # Check for and dismiss various popups (allow location, notifications, etc.)
            popups = [
                # Location access popup
                "//button[contains(text(), 'Allow')]",
                # Notification popup
                "//button[contains(text(), 'Not interested')]",
                # Cookie consent
                "//button[contains(text(), 'I accept')]",
                # Tinder Plus offers
                "//button[contains(text(), 'No Thanks')]",
                "//button[contains(text(), 'Maybe Later')]",
                # Other generic close buttons
                "//button[contains(@aria-label, 'Close')]"
            ]
            
            for popup_xpath in popups:
                try:
                    popup_btn = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, popup_xpath))
                    )
                    popup_btn.click()
                    logger.info(f"Dismissed popup: {popup_xpath}")
                    self._random_wait()
                except TimeoutException:
                    # Popup not found, continue to the next one
                    continue
                except Exception as e:
                    logger.warning(f"Error handling popup {popup_xpath}: {e}")
                    continue
        
        except Exception as e:
            logger.warning(f"Error during popup handling: {e}")
    
    def change_location(self, location: str) -> bool:
        """Change the current location in Tinder.
        
        Args:
            location: Name of the location to set
            
        Returns:
            bool: True if location change was successful, False otherwise
        """
        if not self.driver or not self.is_logged_in:
            logger.error("Cannot change location: Not logged in")
            return False
        
        try:
            # Reset the counter for profiles scraped in current location
            self.profiles_scraped_in_current_location = 0
            
            # Navigate to the settings page
            self.driver.get("https://tinder.com/app/settings")
            logger.info("Navigated to settings page")
            
            self._random_wait()
            
            # Click on the "Discovery" section
            discovery_section = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Discovery') or contains(text(), 'Location')]"))
            )
            discovery_section.click()
            logger.info("Clicked on Discovery/Location section")
            
            self._random_wait()
            
            # Click on the location edit button
            try:
                # Try to find the location button with various possible selectors
                location_selectors = [
                    "//button[contains(@aria-label, 'Location')]",
                    "//button[contains(., 'Location')]",
                    "//div[contains(text(), 'Location')]/following-sibling::button",
                    "//div[contains(text(), 'My Location')]/parent::div/parent::button"
                ]
                
                location_button = None
                for selector in location_selectors:
                    try:
                        location_button = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                        break
                    except:
                        continue
                
                if location_button:
                    location_button.click()
                    logger.info("Clicked on location button")
                else:
                    raise Exception("Could not find location button")
                
                self._random_wait()
                
                # Enter the new location in the search input
                search_input = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Search']"))
                )
                search_input.clear()
                
                # Type the location slowly to simulate human typing
                for char in location:
                    search_input.send_keys(char)
                    time.sleep(random.uniform(0.05, 0.2))
                
                logger.info(f"Entered location: {location}")
                
                self._random_wait()
                
                # Wait for location suggestions and click the first one
                suggestion = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'location-result')]"))
                )
                suggestion.click()
                logger.info("Selected location from suggestions")
                
                self._random_wait()
                
                # Click the apply or done button
                done_button_selectors = [
                    "//button[contains(text(), 'Apply')]",
                    "//button[contains(text(), 'Done')]",
                    "//button[contains(text(), 'Save')]"
                ]
                
                done_button = None
                for selector in done_button_selectors:
                    try:
                        done_button = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                        break
                    except:
                        continue
                
                if done_button:
                    done_button.click()
                    logger.info("Confirmed location change")
                else:
                    raise Exception("Could not find apply/done button")
                
                # Wait for the location change to take effect
                time.sleep(5)
                
                # Navigate back to the main swipe page
                self.driver.get("https://tinder.com/app/recs")
                
                # Update current location
                self.current_location = location
                
                logger.info(f"Successfully changed location to: {location}")
                
                if self.google_sheets:
                    self.google_sheets.log_extraction(
                        "N/A", location, "LOCATION_CHANGE", f"Changed location to {location}")
                
                return True
            
            except Exception as e:
                logger.error(f"Error changing location: {e}")
                
                if self.google_sheets:
                    self.google_sheets.log_error(
                        "Location Change", f"Failed to change location to {location}: {e}", location)
                
                return False
        
        except Exception as e:
            logger.error(f"Failed to access location settings: {e}")
            
            if self.google_sheets:
                self.google_sheets.log_error(
                    "Location Change", f"Failed to access location settings: {e}", location)
            
            return False
    
    def _extract_profile_info(self) -> Optional[Dict[str, Any]]:
        """Extract information from the current profile.
        
        Returns:
            Optional[Dict[str, Any]]: Profile information or None if extraction failed
        """
        try:
            # Wait for profile card to be visible
            profile_card = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'profileCard')]"))
            )
            
            # Extract basic profile information
            try:
                # Try to get name and age
                name_age_elem = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'profileCard__nameAge')]"))
                )
                name_age_text = name_age_elem.text
                
                # Parse name and age (usually in format "Name, Age")
                name_parts = name_age_text.split(',')
                name = name_parts[0].strip()
                age = int(name_parts[1].strip()) if len(name_parts) > 1 and name_parts[1].strip().isdigit() else None
            except:
                # If we can't get structured info, just try to get any name we can find
                try:
                    name_elem = WebDriverWait(self.driver, 3).until(
                        EC.presence_of_element_located((By.XPATH, "//h1"))
                    )
                    name = name_elem.text
                    age = None
                except:
                    name = "Unknown"
                    age = None
            
            # Try to extract bio
            try:
                bio_elem = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'profileCard__bio')]"))
                )
                bio = bio_elem.text
            except:
                bio = ""
            
            # Generate profile ID (timestamp-based)
            timestamp = int(time.time())
            profile_id = f"{timestamp}-{self.total_profiles_scraped + 1:05d}"
            
            # Create profile data structure
            profile_data = {
                "profile_id": profile_id,
                "name": name,
                "age": age,
                "bio": bio,
                "location": self.current_location,
                "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "images": []
            }
            
            return profile_data
        
        except Exception as e:
            logger.error(f"Failed to extract profile information: {e}")
            return None
    
    def _expand_profile(self) -> bool:
        """Click on the profile to expand it and view full details.
        
        Returns:
            bool: True if profile was expanded successfully, False otherwise
        """
        try:
            # Try clicking on the profile card
            profile_card = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'profileCard')]"))
            )
            profile_card.click()
            
            # Wait for expanded profile to appear
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'profileContent')]"))
            )
            
            logger.info("Successfully expanded profile view")
            return True
        
        except TimeoutException:
            logger.warning("Timeout while expanding profile")
            return False
        
        except Exception as e:
            logger.error(f"Failed to expand profile: {e}")
            return False
    
    def _extract_profile_images(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and download images from the expanded profile.
        
        Args:
            profile_data: Dictionary containing profile information
            
        Returns:
            Dict[str, Any]: Updated profile data with image information
        """
        try:
            # Find the profile carousel/slider with images
            carousel = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'profileCard__slider')]"))
            )
            
            # Get all image elements that are currently visible
            images = carousel.find_elements(By.XPATH, ".//div[contains(@aria-label, 'Profile slider')]/div/div/img")
            
            if not images:
                # Try alternative selectors if the images aren't found with the first selector
                images = carousel.find_elements(By.XPATH, ".//div[contains(@class, 'keen-slider')]/div/div/img")
            
            if not images:
                logger.warning(f"Could not find image elements for profile {profile_data['profile_id']}")
                return profile_data
            
            logger.info(f"Found {len(images)} initial image elements")
            
            # Tinder loads images as you click through them, so we need to iterate through the images
            # Get the first image's src
            image_srcs = set()
            
            if len(images) > 0 and images[0].get_attribute("src"):
                image_srcs.add(images[0].get_attribute("src"))
            
            # Click through the carousel to load more images
            try:
                next_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'keen-slider-next')]"))
                )
                
                # Click next until we've gone through all images or hit a limit
                max_clicks = 15  # Safety to prevent infinite loops
                click_count = 0
                
                while click_count < max_clicks:
                    self._random_wait()
                    
                    try:
                        next_button.click()
                        click_count += 1
                        
                        # Get the currently visible image after clicking next
                        image = WebDriverWait(self.driver, 3).until(
                            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'profileCard__slider')]//img[contains(@draggable, 'false')]"))
                        )
                        
                        if image and image.get_attribute("src"):
                            image_srcs.add(image.get_attribute("src"))
                        
                        # Check if we've reached the end of the carousel
                        try:
                            # This will throw an exception if the next button is disabled or not clickable
                            WebDriverWait(self.driver, 1).until(
                                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'keen-slider-next') and not(@disabled)]"))
                            )
                        except:
                            logger.info("Reached end of image carousel")
                            break
                    
                    except (ElementClickInterceptedException, StaleElementReferenceException):
                        logger.warning("Error clicking next in image carousel, trying again")
                        
                        # Refresh the next button element reference
                        try:
                            next_button = WebDriverWait(self.driver, 5).until(
                                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'keen-slider-next')]"))
                            )
                        except:
                            logger.warning("Could not refresh next button, breaking carousel loop")
                            break
            
            except TimeoutException:
                logger.warning("Couldn't find next button in carousel, profile might have only one image")
            
            except Exception as e:
                logger.warning(f"Error navigating image carousel: {e}")
            
            logger.info(f"Found {len(image_srcs)} total unique images")
            
            # If we don't have enough images, return the data without images
            if len(image_srcs) < self.min_images_per_profile:
                logger.info(f"Profile {profile_data['profile_id']} has only {len(image_srcs)} images, skipping")
                
                if self.google_sheets:
                    self.google_sheets.log_extraction(
                        profile_data['profile_id'], 
                        profile_data['location'], 
                        "SKIPPED", 
                        f"Insufficient images: found {len(image_srcs)}, required {self.min_images_per_profile}"
                    )
                
                return profile_data
            
            # Download the images
            image_count = 0
            
            for img_url in image_srcs:
                # Skip data URLs, empty URLs, or placeholder images
                if not img_url or img_url.startswith('data:') or 'placeholder' in img_url:
                    continue
                
                # Create clean city name for filename
                city_name = self.current_location.split(',')[0].strip().lower().replace(' ', '-')
                
                # Create filename according to convention: imageId-cityName-profileId.jpg
                image_id = f"{image_count + 1:06d}"
                filename = f"{image_id}-{city_name}-{profile_data['profile_id']}.jpg"
                file_path = os.path.join(self.output_dir, filename)
                
                # Download the image
                try:
                    response = requests.get(img_url, stream=True, timeout=30)
                    
                    if response.status_code == 200:
                        with open(file_path, 'wb') as file:
                            for chunk in response.iter_content(1024):
                                file.write(chunk)
                        
                        # Add to profile data
                        profile_data['images'].append({
                            'image_id': image_id,
                            'filename': filename,
                            'path': file_path,
                            'url': img_url
                        })
                        
                        image_count += 1
                        logger.info(f"Downloaded image {image_count}: {filename}")
                    
                    else:
                        logger.warning(f"Failed to download image {image_count}: Status code {response.status_code}")
                
                except Exception as e:
                    logger.error(f"Error downloading image {image_count} for profile {profile_data['profile_id']}: {e}")
                    
                    if self.google_sheets:
                        self.google_sheets.log_error(
                            "Image Download", 
                            f"Failed to download image: {e}", 
                            profile_data['location'], 
                            profile_data['profile_id']
                        )
            
            logger.info(f"Successfully downloaded {image_count} images for profile {profile_data['profile_id']}")
            
            if self.google_sheets:
                self.google_sheets.log_extraction(
                    profile_data['profile_id'], 
                    profile_data['location'], 
                    "SCRAPED", 
                    f"Successfully scraped {image_count} images"
                )
            
            return profile_data
        
        except Exception as e:
            logger.error(f"Failed to extract profile images: {e}")
            
            if self.google_sheets:
                self.google_sheets.log_error(
                    "Image Extraction", 
                    f"Failed to extract images: {e}", 
                    profile_data['location'], 
                    profile_data['profile_id']
                )
            
            return profile_data
    
    def _close_expanded_profile(self) -> bool:
        """Close the expanded profile view.
        
        Returns:
            bool: True if profile was closed successfully, False otherwise
        """
        try:
            # Find and click the close button
            close_selectors = [
                "//button[contains(@aria-label, 'Close')]",
                "//button[contains(@class, 'closeButton')]",
                "//button[contains(@title, 'Back to Tinder')]"
            ]
            
            close_button = None
            for selector in close_selectors:
                try:
                    close_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    break
                except:
                    continue
            
            if close_button:
                close_button.click()
                logger.info("Closed expanded profile view")
                return True
            
            # If we couldn't find a close button, try pressing Escape key
            webdriver.ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
            logger.info("Attempted to close profile with Escape key")
            
            # Wait a moment to let the profile close
            time.sleep(2)
            
            return True
        
        except Exception as e:
            logger.error(f"Failed to close expanded profile: {e}")
            return False
    
    def swipe_left(self) -> bool:
        """Swipe left (Nope) on the current profile.
        
        Returns:
            bool: True if swipe was successful, False otherwise
        """
        try:
            # Try to find and click the Nope button
            nope_selectors = [
                "//button[contains(@aria-label, 'Nope')]",
                "//button[contains(@class, 'nope')]",
                "//button[contains(@title, 'Nope')]"
            ]
            
            nope_button = None
            for selector in nope_selectors:
                try:
                    nope_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    break
                except:
                    continue
            
            if nope_button:
                nope_button.click()
                logger.info("Swiped left (Nope)")
                
                # Wait for the swipe animation to complete
                time.sleep(1)
                
                return True
            
            # If we couldn't find a Nope button, try using keyboard shortcut
            webdriver.ActionChains(self.driver).send_keys(Keys.ARROW_LEFT).perform()
            logger.info("Attempted to swipe left with left arrow key")
            
            # Wait for the swipe animation to complete
            time.sleep(1)
            
            return True
        
        except Exception as e:
            logger.error(f"Failed to swipe left: {e}")
            return False
    
    def _handle_popups(self) -> None:
        """Handle various popups that might appear during swiping."""
        try:
            # List of common popup selectors and their respective actions
            popups = [
                # Match notification
                {"selector": "//div[contains(text(), 'It's a Match!')]", "action": "close"},
                # Super Like popup
                {"selector": "//div[contains(text(), 'Super Like')]", "action": "close"},
                # Out of likes popup
                {"selector": "//div[contains(text(), 'Out of Likes')]", "action": "close"},
                # Add to Home Screen
                {"selector": "//div[contains(text(), 'Add to Home Screen')]", "action": "close"},
                # Get Tinder Plus offer
                {"selector": "//div[contains(text(), 'Get Tinder Plus')]", "action": "close"},
                # Generic popups with close buttons
                {"selector": "//button[contains(@aria-label, 'Close')]", "action": "click"}
            ]
            
            for popup in popups:
                try:
                    # Check if the popup is present with a short timeout
                    element = WebDriverWait(self.driver, 3).until(
                        EC.presence_of_element_located((By.XPATH, popup["selector"]))
                    )
                    
                    logger.info(f"Detected popup: {popup['selector']}")
                    
                    # Handle based on the action type
                    if popup["action"] == "close":
                        # Find and click the close button
                        close_button = WebDriverWait(self.driver, 3).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label, 'Close')]"))
                        )
                        close_button.click()
                        logger.info("Closed popup")
                    
                    elif popup["action"] == "click":
                        # Click the element directly
                        element.click()
                        logger.info("Clicked popup element")
                
                except TimeoutException:
                    # Popup not found, continue to the next one
                    continue
                
                except Exception as e:
                    logger.warning(f"Error handling popup {popup['selector']}: {e}")
                    continue
                
                # Wait a moment after handling a popup
                time.sleep(1)
        
        except Exception as e:
            logger.warning(f"Error during popup handling: {e}")
    
    def scrape_profile(self) -> Optional[Dict[str, Any]]:
        """Scrape the current profile.
        
        Returns:
            Optional[Dict[str, Any]]: Scraped profile data or None if scraping failed
        """
        if not self.driver or not self.is_logged_in:
            logger.error("Cannot scrape profile: Not logged in")
            return None
        
        try:
            # Handle any popups that might be present
            self._handle_popups()
            
            # Extract basic profile information
            profile_data = self._extract_profile_info()
            
            if not profile_data:
                logger.warning("Failed to extract profile information")
                return None
            
            # Expand the profile to see all details and images
            if not self._expand_profile():
                logger.warning("Failed to expand profile")
                return profile_data
            
            # Extract and download profile images
            profile_data = self._extract_profile_images(profile_data)
            
            # Close the expanded profile view
            self._close_expanded_profile()
            
            # Check if we got enough images
            if len(profile_data.get('images', [])) < self.min_images_per_profile:
                logger.info(f"Profile {profile_data['profile_id']} doesn't have enough images, skipping")
                return None
            
            # Update counters
            self.profiles_scraped_in_current_location += 1
            self.total_profiles_scraped += 1
            
            logger.info(f"Successfully scraped profile {profile_data['profile_id']} with {len(profile_data['images'])} images")
            
            return profile_data
        
        except Exception as e:
            logger.error(f"Failed to scrape profile: {e}")
            
            if self.google_sheets:
                self.google_sheets.log_error(
                    "Profile Scraping", 
                    f"Failed to scrape profile: {e}", 
                    self.current_location or "Unknown"
                )
            
            return None
    
    def run_scraping_session(self, target_profiles: int, locations: List[str]) -> int:
        """Run a complete scraping session across multiple locations.
        
        Args:
            target_profiles: Total number of profiles to scrape
            locations: List of locations to scrape from
            
        Returns:
            int: Number of profiles successfully scraped
        """
        if not self.initialize_driver():
            logger.error("Failed to initialize WebDriver")
            return 0
        
        try:
            # Login to Tinder
            if not self.login():
                logger.error("Failed to login to Tinder")
                return 0
            
            profiles_scraped = 0
            location_index = 0
            
            # Continue scraping until we reach the target or run out of locations
            while profiles_scraped < target_profiles and location_index < len(locations):
                current_location = locations[location_index]
                
                # Check if we need to change location
                if self.current_location != current_location or self.profiles_scraped_in_current_location >= self.profiles_per_location:
                    if not self.change_location(current_location):
                        logger.warning(f"Failed to change location to {current_location}, trying next location")
                        location_index += 1
                        continue
                
                # Scrape a profile
                profile_data = self.scrape_profile()
                
                if profile_data and len(profile_data.get('images', [])) >= self.min_images_per_profile:
                    # Save profile data to Google Sheets if available
                    if self.google_sheets:
                        self.google_sheets.save_extracted_data(profile_data)
                    
                    profiles_scraped += 1
                    logger.info(f"Successfully processed profile {profiles_scraped}/{target_profiles}")
                
                # Swipe left to go to the next profile
                self.swipe_left()
                
                # Check if we need to move to the next location
                if self.profiles_scraped_in_current_location >= self.profiles_per_location:
                    logger.info(f"Reached profile limit for location {current_location}, moving to next location")
                    location_index += 1
                
                # Add a small delay between profiles to avoid rate limiting
                self._random_wait()
                
                # Handle popups that might appear during swiping
                self._handle_popups()
            
            logger.info(f"Scraping session completed. Scraped {profiles_scraped}/{target_profiles} profiles")
            
            return profiles_scraped
        
        except Exception as e:
            logger.error(f"Error in scraping session: {e}")
            
            if self.google_sheets:
                self.google_sheets.log_error(
                    "Scraping Session", 
                    f"Session error: {e}", 
                    self.current_location or "Multiple"
                )
            
            return profiles_scraped
        
        finally:
            # Always close the driver
            if self.driver:
                self.driver.quit()
                logger.info("WebDriver closed")
