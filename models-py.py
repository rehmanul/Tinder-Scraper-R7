from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime

@dataclass
class Image:
    """Represents an image from a profile."""
    image_id: str
    filename: str
    path: str
    url: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    thumbnail_path: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the image
        """
        return {
            "image_id": self.image_id,
            "filename": self.filename,
            "path": self.path,
            "url": self.url,
            "width": self.width,
            "height": self.height,
            "thumbnail_path": self.thumbnail_path
        }

@dataclass
class ValueRange:
    """Represents a range of values for a label attribute."""
    min_value: float
    max_value: float
    
    def to_list(self) -> List[float]:
        """Convert to list representation.
        
        Returns:
            List[float]: [min_value, max_value]
        """
        return [self.min_value, self.max_value]

@dataclass
class CategoryValue:
    """Represents a category value with confidence range."""
    name: str
    confidence_range: ValueRange
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the category value
        """
        return {
            "name": self.name,
            "value": self.confidence_range.to_list()
        }

@dataclass
class ProfileLabels:
    """Represents the labels for a profile."""
    # Basic attributes
    age: ValueRange
    height: ValueRange
    weight: ValueRange
    celibacy: Optional[ValueRange] = None
    cooperativeness: Optional[ValueRange] = None
    intelligence: Optional[ValueRange] = None
    waist: Optional[ValueRange] = None
    bust: Optional[ValueRange] = None
    hips: Optional[ValueRange] = None
    face: Optional[ValueRange] = None
    
    # Categorical attributes
    gender: List[CategoryValue] = field(default_factory=list)
    ethnicity: List[CategoryValue] = field(default_factory=list)
    
    # Additional attributes
    big_spender: Optional[ValueRange] = None
    presentable: Optional[ValueRange] = None
    muscle_percentage: Optional[ValueRange] = None
    fat_percentage: Optional[ValueRange] = None
    dominance: Optional[ValueRange] = None
    power: Optional[ValueRange] = None
    confidence: Optional[ValueRange] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the labels
        """
        result = {
            "age": self.age.to_list(),
            "height": self.height.to_list(),
            "weight": self.weight.to_list(),
            "gender": [g.to_dict() for g in self.gender],
            "ethnicity": [e.to_dict() for e in self.ethnicity]
        }
        
        # Add optional attributes if they exist
        if self.celibacy:
            result["celibacy"] = self.celibacy.to_list()
        if self.cooperativeness:
            result["cooperativeness"] = self.cooperativeness.to_list()
        if self.intelligence:
            result["intelligence"] = self.intelligence.to_list()
        if self.waist:
            result["waist"] = self.waist.to_list()
        if self.bust:
            result["bust"] = self.bust.to_list()
        if self.hips:
            result["hips"] = self.hips.to_list()
        if self.face:
            result["face"] = self.face.to_list()
        if self.big_spender:
            result["big_spender"] = self.big_spender.to_list()
        if self.presentable:
            result["presentable"] = self.presentable.to_list()
        if self.muscle_percentage:
            result["muscle_percentage"] = self.muscle_percentage.to_list()
        if self.fat_percentage:
            result["fat_percentage"] = self.fat_percentage.to_list()
        if self.dominance:
            result["dominance"] = self.dominance.to_list()
        if self.power:
            result["power"] = self.power.to_list()
        if self.confidence:
            result["confidence"] = self.confidence.to_list()
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProfileLabels':
        """Create ProfileLabels from a dictionary.
        
        Args:
            data: Dictionary containing label data
            
        Returns:
            ProfileLabels: Created ProfileLabels instance
        """
        # Extract required attributes
        age_data = data.get('age', [25, 30])
        height_data = data.get('height', [165, 175])
        weight_data = data.get('weight', [55, 65])
        
        # Create value ranges for required attributes
        age = ValueRange(min_value=age_data[0], max_value=age_data[1])
        height = ValueRange(min_value=height_data[0], max_value=height_data[1])
        weight = ValueRange(min_value=weight_data[0], max_value=weight_data[1])
        
        # Extract gender data
        gender_data = data.get('gender', [])
        gender = []
        for g in gender_data:
            if isinstance(g, dict) and 'name' in g and 'value' in g:
                value = g['value']
                if isinstance(value, list) and len(value) == 2:
                    gender.append(CategoryValue(
                        name=g['name'],
                        confidence_range=ValueRange(min_value=value[0], max_value=value[1])
                    ))
        
        # Extract ethnicity data
        ethnicity_data = data.get('ethnicity', [])
        ethnicity = []
        for e in ethnicity_data:
            if isinstance(e, dict) and 'name' in e and 'value' in e:
                value = e['value']
                if isinstance(value, list) and len(value) == 2:
                    ethnicity.append(CategoryValue(
                        name=e['name'],
                        confidence_range=ValueRange(min_value=value[0], max_value=value[1])
                    ))
        
        # Create ProfileLabels with required attributes
        labels = cls(
            age=age,
            height=height,
            weight=weight,
            gender=gender,
            ethnicity=ethnicity
        )
        
        # Add optional attributes if they exist
        if 'celibacy' in data:
            celibacy_data = data['celibacy']
            if isinstance(celibacy_data, list) and len(celibacy_data) == 2:
                labels.celibacy = ValueRange(min_value=celibacy_data[0], max_value=celibacy_data[1])
        
        if 'cooperativeness' in data:
            coop_data = data['cooperativeness']
            if isinstance(coop_data, list) and len(coop_data) == 2:
                labels.cooperativeness = ValueRange(min_value=coop_data[0], max_value=coop_data[1])
        
        if 'intelligence' in data:
            intel_data = data['intelligence']
            if isinstance(intel_data, list) and len(intel_data) == 2:
                labels.intelligence = ValueRange(min_value=intel_data[0], max_value=intel_data[1])
        
        # Add other optional attributes similarly
        for attr in ['waist', 'bust', 'hips', 'face', 'big_spender', 'presentable', 
                     'muscle_percentage', 'fat_percentage', 'dominance', 'power', 'confidence']:
            if attr in data:
                attr_data = data[attr]
                if isinstance(attr_data, list) and len(attr_data) == 2:
                    setattr(labels, attr, ValueRange(min_value=attr_data[0], max_value=attr_data[1]))
        
        return labels

@dataclass
class Profile:
    """Represents a Tinder profile."""
    profile_id: str
    location: str
    scraped_at: datetime
    images: List[Image] = field(default_factory=list)
    labels: Optional[ProfileLabels] = None
    name: Optional[str] = None
    age: Optional[int] = None
    bio: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the profile
        """
        result = {
            "profile_id": self.profile_id,
            "location": self.location,
            "scraped_at": self.scraped_at.isoformat(),
            "images": [img.to_dict() for img in self.images]
        }
        
        if self.labels:
            result["labels"] = self.labels.to_dict()
        
        if self.name:
            result["name"] = self.name
        
        if self.age:
            result["age"] = self.age
        
        if self.bio:
            result["bio"] = self.bio
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Profile':
        """Create Profile from a dictionary.
        
        Args:
            data: Dictionary containing profile data
            
        Returns:
            Profile: Created Profile instance
        """
        # Extract required attributes
        profile_id = data.get('profile_id', '')
        location = data.get('location', '')
        
        # Parse scraped_at
        scraped_at_str = data.get('scraped_at', '')
        try:
            scraped_at = datetime.fromisoformat(scraped_at_str)
        except (ValueError, TypeError):
            scraped_at = datetime.now()
        
        # Create images
        images = []
        images_data = data.get('images', [])
        for img_data in images_data:
            if isinstance(img_data, dict):
                image = Image(
                    image_id=img_data.get('image_id', ''),
                    filename=img_data.get('filename', ''),
                    path=img_data.get('path', ''),
                    url=img_data.get('url'),
                    width=img_data.get('width'),
                    height=img_data.get('height'),
                    thumbnail_path=img_data.get('thumbnail_path')
                )
                images.append(image)
        
        # Create the profile
        profile = cls(
            profile_id=profile_id,
            location=location,
            scraped_at=scraped_at,
            images=images,
            name=data.get('name'),
            age=data.get('age'),
            bio=data.get('bio')
        )
        
        # Add labels if they exist
        if 'labels' in data and isinstance(data['labels'], dict):
            profile.labels = ProfileLabels.from_dict(data['labels'])
        
        return profile

@dataclass
class LogEntry:
    """Represents a log entry."""
    timestamp: datetime
    log_type: str  # 'extraction' or 'error'
    details: str
    location: Optional[str] = None
    profile_id: Optional[str] = None
    status: Optional[str] = None  # For extraction logs: 'SCRAPED', 'SKIPPED', 'LOCATION_CHANGE', etc.
    error_type: Optional[str] = None  # For error logs
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the log entry
        """
        result = {
            "timestamp": self.timestamp.isoformat(),
            "log_type": self.log_type,
            "details": self.details
        }
        
        if self.location:
            result["location"] = self.location
        
        if self.profile_id:
            result["profile_id"] = self.profile_id
        
        if self.status:
            result["status"] = self.status
        
        if self.error_type:
            result["error_type"] = self.error_type
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LogEntry':
        """Create LogEntry from a dictionary.
        
        Args:
            data: Dictionary containing log entry data
            
        Returns:
            LogEntry: Created LogEntry instance
        """
        # Parse timestamp
        timestamp_str = data.get('timestamp', '')
        try:
            timestamp = datetime.fromisoformat(timestamp_str)
        except (ValueError, TypeError):
            timestamp = datetime.now()
        
        return cls(
            timestamp=timestamp,
            log_type=data.get('log_type', 'extraction'),
            details=data.get('details', ''),
            location=data.get('location'),
            profile_id=data.get('profile_id'),
            status=data.get('status'),
            error_type=data.get('error_type')
        )
