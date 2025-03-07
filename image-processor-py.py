import os
import logging
import hashlib
from typing import Dict, List, Tuple, Optional, Union
from pathlib import Path
import requests
from PIL import Image, UnidentifiedImageError, ImageOps
from io import BytesIO

logger = logging.getLogger(__name__)

class ImageProcessor:
    """Handles image verification, optimization, and storage."""
    
    def __init__(self, output_dir: str = "tinder_images", 
                 quality: int = 85, 
                 max_width: int = 1200,
                 thumbnail_size: Tuple[int, int] = (300, 300)):
        """Initialize the ImageProcessor.
        
        Args:
            output_dir: Directory to store processed images
            quality: JPEG compression quality (1-100)
            max_width: Maximum width to resize images to
            thumbnail_size: Size for thumbnail generation
        """
        self.output_dir = output_dir
        self.quality = quality
        self.max_width = max_width
        self.thumbnail_size = thumbnail_size
        self.image_hashes: Dict[str, str] = {}  # Store hashes to detect duplicates
        
        # Create output directory and thumbnail directory if they don't exist
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "thumbnails"), exist_ok=True)
    
    def download_image(self, url: str, filename: str) -> Optional[str]:
        """Download an image from a URL.
        
        Args:
            url: URL of the image to download
            filename: Filename to save the image as
            
        Returns:
            Optional[str]: Path to the downloaded image or None if download failed
        """
        try:
            # Skip data URLs, empty URLs, or placeholder images
            if not url or url.startswith('data:') or 'placeholder' in url:
                logger.warning(f"Skipping invalid URL: {url}")
                return None
            
            # Download the image
            response = requests.get(url, stream=True, timeout=30)
            
            if response.status_code != 200:
                logger.warning(f"Failed to download image {filename}: Status code {response.status_code}")
                return None
            
            # Process the image
            file_path = self.process_image(response.content, filename)
            return file_path
            
        except Exception as e:
            logger.error(f"Error downloading image {filename}: {e}")
            return None
    
    def process_image(self, image_data: bytes, filename: str) -> Optional[str]:
        """Process an image from bytes data.
        
        Args:
            image_data: Binary image data
            filename: Filename to save the processed image as
            
        Returns:
            Optional[str]: Path to the processed image or None if processing failed
        """
        try:
            # Open image from binary data
            img = Image.open(BytesIO(image_data))
            
            # Calculate image hash for duplicate detection
            img_hash = self._calculate_image_hash(img)
            
            # Check if this is a duplicate image
            if img_hash in self.image_hashes:
                logger.info(f"Detected duplicate image: {filename} matches {self.image_hashes[img_hash]}")
                return None
            
            # Store the hash to detect future duplicates
            self.image_hashes[img_hash] = filename
            
            # Verify this is a valid image
            if not self._verify_image(img):
                logger.warning(f"Invalid image: {filename}")
                return None
            
            # Process the image (resize, optimize)
            processed_img = self._optimize_image(img)
            
            # Save the processed image
            file_path = os.path.join(self.output_dir, filename)
            processed_img.save(file_path, "JPEG", quality=self.quality, optimize=True)
            
            # Generate and save thumbnail
            self._create_thumbnail(processed_img, filename)
            
            logger.info(f"Successfully processed and saved image: {filename}")
            return file_path
            
        except UnidentifiedImageError:
            logger.warning(f"Could not identify image format: {filename}")
            return None
            
        except Exception as e:
            logger.error(f"Error processing image {filename}: {e}")
            return None
    
    def _verify_image(self, img: Image.Image) -> bool:
        """Verify that an image is valid and meets requirements.
        
        Args:
            img: PIL Image object to verify
            
        Returns:
            bool: True if image is valid, False otherwise
        """
        try:
            # Check image dimensions
            width, height = img.size
            if width < 100 or height < 100:
                logger.warning(f"Image too small: {width}x{height}")
                return False
            
            # Check image mode
            if img.mode not in ['RGB', 'RGBA']:
                logger.warning(f"Unsupported image mode: {img.mode}")
                return False
            
            # Check for completely black or white images
            if self._is_blank_image(img):
                logger.warning("Image appears to be blank")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error verifying image: {e}")
            return False
    
    def _is_blank_image(self, img: Image.Image, threshold: float = 0.95) -> bool:
        """Check if an image is mostly blank (black or white).
        
        Args:
            img: PIL Image object to check
            threshold: Percentage threshold for considering the image blank
            
        Returns:
            bool: True if image is blank, False otherwise
        """
        # Convert to grayscale for simplicity
        gray_img = ImageOps.grayscale(img)
        
        # Get pixel values
        pixels = list(gray_img.getdata())
        total_pixels = len(pixels)
        
        # Count black or white pixels
        black_white_count = sum(1 for p in pixels if p < 10 or p > 245)
        
        # Calculate percentage
        blank_percentage = black_white_count / total_pixels
        
        return blank_percentage > threshold
    
    def _optimize_image(self, img: Image.Image) -> Image.Image:
        """Optimize an image by resizing and converting if needed.
        
        Args:
            img: PIL Image object to optimize
            
        Returns:
            Image.Image: Optimized PIL Image object
        """
        # Convert RGBA to RGB (JPEG doesn't support alpha)
        if img.mode == 'RGBA':
            # Create a white background
            background = Image.new('RGB', img.size, (255, 255, 255))
            # Paste the image on the background using alpha as mask
            background.paste(img, mask=img.split()[3])
            img = background
        
        # Resize if larger than max width
        width, height = img.size
        if width > self.max_width:
            # Calculate new height to maintain aspect ratio
            new_height = int(height * (self.max_width / width))
            img = img.resize((self.max_width, new_height), Image.LANCZOS)
        
        return img
    
    def _create_thumbnail(self, img: Image.Image, filename: str) -> None:
        """Create a thumbnail version of an image.
        
        Args:
            img: PIL Image object to create thumbnail from
            filename: Original filename for the image
        """
        try:
            # Create a copy to avoid modifying the original
            thumb = img.copy()
            
            # Generate thumbnail
            thumb.thumbnail(self.thumbnail_size, Image.LANCZOS)
            
            # Save thumbnail
            thumb_path = os.path.join(self.output_dir, "thumbnails", filename)
            thumb.save(thumb_path, "JPEG", quality=70)
            
        except Exception as e:
            logger.error(f"Error creating thumbnail for {filename}: {e}")
    
    def _calculate_image_hash(self, img: Image.Image) -> str:
        """Calculate a perceptual hash of an image for duplicate detection.
        
        Args:
            img: PIL Image object to hash
            
        Returns:
            str: Perceptual hash as a string
        """
        # Resize to 8x8 and convert to grayscale
        img = img.resize((8, 8), Image.LANCZOS).convert('L')
        
        # Calculate average pixel value
        pixels = list(img.getdata())
        avg = sum(pixels) / len(pixels)
        
        # Create binary hash (1 if pixel value is above average, 0 otherwise)
        bits = ''.join('1' if p > avg else '0' for p in pixels)
        
        # Convert binary to hexadecimal
        hash_hex = hex(int(bits, 2))[2:].zfill(16)
        
        return hash_hex
    
    def get_image_stats(self) -> Dict[str, int]:
        """Get statistics about processed images.
        
        Returns:
            Dict[str, int]: Statistics including total images and unique images
        """
        try:
            # Count all images in the output directory
            total_images = len([f for f in os.listdir(self.output_dir) 
                               if os.path.isfile(os.path.join(self.output_dir, f))
                               and f.lower().endswith(('.jpg', '.jpeg', '.png'))])
            
            # Count thumbnails
            thumbnail_dir = os.path.join(self.output_dir, "thumbnails")
            total_thumbnails = len([f for f in os.listdir(thumbnail_dir) 
                                   if os.path.isfile(os.path.join(thumbnail_dir, f))
                                   and f.lower().endswith(('.jpg', '.jpeg', '.png'))])
            
            # Count unique images based on our hash tracking
            unique_images = len(self.image_hashes)
            
            return {
                "total_images": total_images,
                "total_thumbnails": total_thumbnails,
                "unique_images": unique_images
            }
            
        except Exception as e:
            logger.error(f"Error getting image stats: {e}")
            return {
                "total_images": 0,
                "total_thumbnails": 0,
                "unique_images": 0
            }
