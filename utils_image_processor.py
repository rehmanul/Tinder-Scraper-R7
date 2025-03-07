import os
import io
import time
import logging
import requests
from PIL import Image
from pathlib import Path

logger = logging.getLogger(__name__)

class ImageProcessor:
    """Utility class for handling image processing operations."""
    
    def __init__(self, output_dir="tinder_images"):
        """Initialize the image processor.
        
        Args:
            output_dir: Directory to save processed images
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def download_image(self, image_url, filename):
        """Download an image from a URL and save it to disk.
        
        Args:
            image_url: URL of the image to download
            filename: Filename to save the image as
            
        Returns:
            bool: True if download successful, False otherwise
            str: Path to saved image if successful, None otherwise
        """
        try:
            # Create full path
            file_path = os.path.join(self.output_dir, filename)
            
            # Download image with timeout
            response = requests.get(image_url, stream=True, timeout=30)
            
            if response.status_code == 200:
                # Save image
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                
                # Verify the image is valid
                if self.validate_image(file_path):
                    logger.info(f"Successfully downloaded and validated image: {filename}")
                    return True, file_path
                else:
                    logger.warning(f"Downloaded image failed validation: {filename}")
                    os.remove(file_path)  # Remove invalid image
                    return False, None
            else:
                logger.warning(f"Failed to download image, status code {response.status_code}: {filename}")
                return False, None
                
        except Exception as e:
            logger.error(f"Error downloading image {filename}: {e}")
            return False, None
    
    def validate_image(self, file_path):
        """Validate that a file is a proper image.
        
        Args:
            file_path: Path to the image file
            
        Returns:
            bool: True if valid image, False otherwise
        """
        try:
            with Image.open(file_path) as img:
                # Check image dimensions
                width, height = img.size
                
                # Consider images too small as invalid
                if width < 100 or height < 100:
                    logger.warning(f"Image too small: {width}x{height}")
                    return False
                
                # Ensure the image has data
                img.verify()
                return True
        except Exception as e:
            logger.warning(f"Invalid image file {file_path}: {e}")
            return False
    
    def optimize_image(self, file_path, max_size=1024, quality=85):
        """Optimize an image for storage (resize if too large, compress).
        
        Args:
            file_path: Path to the image file
            max_size: Maximum dimension (width or height)
            quality: JPEG quality (0-100)
            
        Returns:
            bool: True if optimization successful, False otherwise
        """
        try:
            with Image.open(file_path) as img:
                # Check if resize is needed
                width, height = img.size
                if width > max_size or height > max_size:
                    # Calculate new dimensions
                    if width > height:
                        new_width = max_size
                        new_height = int(height * (max_size / width))
                    else:
                        new_height = max_size
                        new_width = int(width * (max_size / height))
                    
                    # Resize image
                    img = img.resize((new_width, new_height), Image.LANCZOS)
                    
                # Save with compression
                img.save(file_path, "JPEG", quality=quality, optimize=True)
                logger.info(f"Successfully optimized image: {file_path}")
                return True
                
        except Exception as e:
            logger.error(f"Error optimizing image {file_path}: {e}")
            return False
    
    def generate_filename(self, image_id, city_name, profile_id):
        """Generate a standardized filename based on the required format.
        
        Args:
            image_id: ID number of the image 
            city_name: Name of the city/location
            profile_id: ID of the profile
            
        Returns:
            str: Formatted filename
        """
        # Format: imageId-cityName-profileId.jpg
        # Clean city name by removing spaces and special characters
        clean_city = city_name.split(',')[0].strip().lower().replace(' ', '-')
        
        # Format image ID with leading zeros
        image_id_str = str(image_id).zfill(6)
        
        return f"{image_id_str}-{clean_city}-{profile_id}.jpg"