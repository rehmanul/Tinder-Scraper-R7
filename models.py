from datetime import datetime
from typing import Dict, List, Any, Optional, Union
import json

class Profile:
    """Model class for Tinder profile data."""
    
    def __init__(self, profile_id: str, location: str, name: Optional[str] = None, 
                 age: Optional[int] = None, bio: Optional[str] = None, 
                 scraped_at: Optional[str] = None, images: Optional[List[Dict]] = None,
                 labels: Optional[Dict] = None, status: str = 'unlabeled'):
        """Initialize a Profile instance.
        
        Args:
            profile_id: Unique identifier for the profile
            location: Location where the profile was scraped
            name: Name displayed on the profile
            age: Age displayed on the profile
            bio: Bio text from the profile
            scraped_at: Timestamp when the profile was scraped
            images: List of image metadata
            labels: Dictionary of profile labels
            status: Profile status ('unlabeled', 'labeled', 'skipped')
        """
        self.profile_id = profile_id
        self.location = location
        self.name = name
        self.age = age
        self.bio = bio
        self.scraped_at = scraped_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.images = images or []
        self.labels = labels or {}
        self.status = status
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary representation.
        
        Returns:
            Dict: Dictionary representation of the profile
        """
        return {
            'profile_id': self.profile_id,
            'location': self.location,
            'name': self.name,
            'age': self.age,
            'bio': self.bio,
            'scraped_at': self.scraped_at,
            'images': self.images,
            'labels': self.labels,
            'status': self.status
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Profile':
        """Create a Profile instance from a dictionary.
        
        Args:
            data: Dictionary containing profile data
            
        Returns:
            Profile: New Profile instance
        """
        return cls(
            profile_id=data.get('profile_id'),
            location=data.get('location'),
            name=data.get('name'),
            age=data.get('age'),
            bio=data.get('bio'),
            scraped_at=data.get('scraped_at'),
            images=data.get('images', []),
            labels=data.get('labels', {}),
            status=data.get('status', 'unlabeled')
        )
    
    def add_image(self, image_id: str, filename: str, path: str, url: Optional[str] = None) -> None:
        """Add an image to the profile.
        
        Args:
            image_id: Unique identifier for the image
            filename: Name of the image file
            path: Path to the stored image
            url: Original URL of the image
        """
        self.images.append({
            'image_id': image_id,
            'filename': filename,
            'path': path,
            'url': url
        })
    
    def set_labels(self, labels: Dict[str, Any]) -> None:
        """Set or update the profile labels.
        
        Args:
            labels: Dictionary of profile labels
        """
        self.labels = labels
        self.status = 'labeled'
    
    def skip(self) -> None:
        """Mark the profile as skipped."""
        self.status = 'skipped'
    
    def is_labeled(self) -> bool:
        """Check if the profile is labeled.
        
        Returns:
            bool: True if the profile is labeled, False otherwise
        """
        return self.status == 'labeled'
    
    def is_skipped(self) -> bool:
        """Check if the profile is skipped.
        
        Returns:
            bool: True if the profile is skipped, False otherwise
        """
        return self.status == 'skipped'
    
    def has_enough_images(self, min_images: int = 5) -> bool:
        """Check if the profile has enough images.
        
        Args:
            min_images: Minimum number of images required
            
        Returns:
            bool: True if the profile has enough images, False otherwise
        """
        return len(self.images) >= min_images
    
    def get_primary_ethnicity(self) -> str:
        """Get the primary ethnicity based on labels.
        
        Returns:
            str: Name of the primary ethnicity or 'Unknown'
        """
        if not self.labels or 'ethnicity' not in self.labels:
            return 'Unknown'
        
        try:
            # Sort ethnicities by max value and return the top one
            ethnicities = sorted(
                self.labels['ethnicity'],
                key=lambda x: x['value'][1] if isinstance(x['value'], list) and len(x['value']) > 1 else 0,
                reverse=True
            )
            
            if ethnicities and 'name' in ethnicities[0]:
                return ethnicities[0]['name']
        except (KeyError, IndexError, TypeError):
            pass
        
        return 'Unknown'