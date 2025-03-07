import random
import logging
import json
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class LabelGenerator:
    """Utility class for generating and processing profile labels."""
    
    def __init__(self):
        """Initialize the label generator."""
        pass
    
    def generate_placeholder_labels(self, profile_data=None):
        """Generate placeholder labels for a profile.
        
        Args:
            profile_data: Optional profile data to influence label generation
            
        Returns:
            Dict: Dictionary containing generated labels
        """
        # Use the profile's age as a baseline if available
        age = 25
        if profile_data and 'age' in profile_data and profile_data['age']:
            try:
                age = int(profile_data['age'])
            except (ValueError, TypeError):
                pass
        
        # Generate random ranges for each attribute
        labels = {
            "celibacy": [random.randint(30, 60), random.randint(60, 90)],
            "cooperativeness": [random.randint(40, 70), random.randint(70, 95)],
            "intelligence": [random.randint(50, 75), random.randint(75, 95)],
            "weight": [random.randint(50, 60), random.randint(60, 70)],
            "waist": [random.randint(60, 70), random.randint(70, 85)],
            "bust": [random.randint(85, 90), random.randint(90, 100)],
            "hips": [random.randint(85, 95), random.randint(95, 105)],
            "gender": [
                {"name": "male", "value": [random.randint(0, 10), random.randint(5, 15)]},
                {"name": "female", "value": [random.randint(85, 95), random.randint(90, 100)]}
            ],
            "age": [max(18, age - random.randint(0, 3)), age + random.randint(0, 3)],
            "height": [random.randint(155, 165), random.randint(165, 175)],
            "face": [random.randint(60, 80), random.randint(80, 95)],
            "big_spender": [random.randint(30, 60), random.randint(60, 90)],
            "presentable": [random.randint(60, 80), random.randint(80, 95)],
            "muscle_percentage": [random.randint(10, 15), random.randint(15, 25)],
            "fat_percentage": [random.randint(15, 25), random.randint(25, 35)],
            "dominance": [random.randint(30, 60), random.randint(60, 90)],
            "power": [random.randint(40, 70), random.randint(70, 90)],
            "confidence": [random.randint(50, 75), random.randint(75, 95)]
        }
        
        # Generate ethnicity data
        labels["ethnicity"] = self._generate_ethnicity_distribution()
        
        logger.info(f"Generated placeholder labels")
        return labels
    
    def _generate_ethnicity_distribution(self):
        """Generate a random distribution of ethnicity values.
        
        Returns:
            List: List of ethnicity objects with name and value ranges
        """
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
        
        # Select a primary ethnicity
        primary_idx = random.randint(0, len(ethnicities) - 1)
        
        ethnicity_values = []
        for i, ethnicity in enumerate(ethnicities):
            if i == primary_idx:
                # Primary ethnicity gets high values
                min_val = random.randint(70, 85)
                max_val = random.randint(min_val, 95)
            else:
                # Other ethnicities get low values
                min_val = random.randint(1, 20)
                max_val = random.randint(min_val, min_val + 15)
            
            ethnicity_values.append({
                "name": ethnicity,
                "value": [min_val, max_val]
            })
        
        return ethnicity_values
    
    def validate_labels(self, labels):
        """Validate that labels meet the required format and constraints.
        
        Args:
            labels: Label dictionary to validate
            
        Returns:
            bool: True if labels are valid, False otherwise
            str: Error message if invalid, None otherwise
        """
        required_fields = [
            "celibacy", "cooperativeness", "intelligence", "weight", 
            "waist", "bust", "hips", "gender", "age", "height", 
            "face", "ethnicity", "big_spender", "presentable", 
            "muscle_percentage", "fat_percentage", "dominance", 
            "power", "confidence"
        ]
        
        # Check for required fields
        for field in required_fields:
            if field not in labels:
                return False, f"Missing required field: {field}"
        
        # Check range values (except gender and ethnicity)
        range_fields = [f for f in required_fields if f not in ["gender", "ethnicity"]]
        for field in range_fields:
            value = labels[field]
            
            # Check if it's a list with two elements
            if not isinstance(value, list) or len(value) != 2:
                return False, f"Field {field} must be a list with two values"
            
            # Check if values are numbers
            try:
                min_val, max_val = float(value[0]), float(value[1])
            except (ValueError, TypeError):
                return False, f"Field {field} must contain numeric values"
            
            # Check if min <= max
            if min_val > max_val:
                return False, f"Minimum value must be <= maximum value for {field}"
        
        # Check gender field
        gender = labels["gender"]
        if not isinstance(gender, list):
            return False, "Gender must be a list of objects"
        
        for g in gender:
            if not isinstance(g, dict) or "name" not in g or "value" not in g:
                return False, "Each gender entry must have 'name' and 'value' fields"
            
            if not isinstance(g["value"], list) or len(g["value"]) != 2:
                return False, "Gender value must be a list with two values"
        
        # Check ethnicity field
        ethnicity = labels["ethnicity"]
        if not isinstance(ethnicity, list):
            return False, "Ethnicity must be a list of objects"
        
        for e in ethnicity:
            if not isinstance(e, dict) or "name" not in e or "value" not in e:
                return False, "Each ethnicity entry must have 'name' and 'value' fields"
            
            if not isinstance(e["value"], list) or len(e["value"]) != 2:
                return False, "Ethnicity value must be a list with two values"
        
        return True, None
    
    def format_labels_for_display(self, labels):
        """Format labels for display in the UI.
        
        Args:
            labels: Raw label dictionary
            
        Returns:
            Dict: Dictionary with formatted label values for display
        """
        formatted = {}
        
        # Format range values
        for key, value in labels.items():
            if key not in ["gender", "ethnicity"]:
                if isinstance(value, list) and len(value) == 2:
                    formatted[key] = f"{value[0]} - {value[1]}"
        
        # Format gender
        if "gender" in labels:
            gender_strs = []
            for g in labels["gender"]:
                if "name" in g and "value" in g:
                    gender_strs.append(f"{g['name'].capitalize()}: {g['value'][0]}-{g['value'][1]}%")
            formatted["gender"] = ", ".join(gender_strs)
        
        # Format ethnicity - just show primary
        if "ethnicity" in labels:
            try:
                # Sort by max value
                sorted_eth = sorted(labels["ethnicity"], 
                                    key=lambda x: x["value"][1] if isinstance(x["value"], list) else 0, 
                                    reverse=True)
                if sorted_eth:
                    primary = sorted_eth[0]
                    formatted["primary_ethnicity"] = f"{primary['name']}: {primary['value'][0]}-{primary['value'][1]}%"
            except (KeyError, IndexError, TypeError):
                formatted["primary_ethnicity"] = "Unknown"
        
        return formatted