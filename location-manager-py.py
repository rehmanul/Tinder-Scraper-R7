import random
import logging
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger(__name__)

class LocationManager:
    """Manages location rotation for Tinder profile scraping.
    
    This class maintains a list of locations and handles rotation strategies
    to ensure diverse profile collection across global cities.
    """
    
    def __init__(self, locations: List[str], profiles_per_location: int = 20):
        """Initialize the LocationManager.
        
        Args:
            locations: List of locations to rotate through
            profiles_per_location: Maximum number of profiles to scrape per location
        """
        self.locations = locations
        self.profiles_per_location = profiles_per_location
        self.current_location_index = 0
        self.location_stats: Dict[str, Dict[str, int]] = {}
        
        # Initialize stats for each location
        for location in self.locations:
            self.location_stats[location] = {
                'profiles_scraped': 0,
                'profiles_skipped': 0,
                'errors': 0
            }
    
    def get_locations(self) -> List[str]:
        """Get the full list of available locations.
        
        Returns:
            List[str]: All available locations
        """
        return self.locations
    
    def get_current_location(self) -> str:
        """Get the current location.
        
        Returns:
            str: Current location
        """
        return self.locations[self.current_location_index]
    
    def next_location(self) -> str:
        """Move to the next location in the rotation.
        
        Returns:
            str: Next location
        """
        self.current_location_index = (self.current_location_index + 1) % len(self.locations)
        return self.get_current_location()
    
    def random_location(self) -> str:
        """Get a random location from the available locations.
        
        Returns:
            str: Randomly selected location
        """
        random_index = random.randint(0, len(self.locations) - 1)
        self.current_location_index = random_index
        return self.get_current_location()
    
    def get_least_used_location(self) -> str:
        """Get the location with the fewest scraped profiles.
        
        Returns:
            str: Least used location
        """
        least_used = None
        min_count = float('inf')
        
        for location, stats in self.location_stats.items():
            if stats['profiles_scraped'] < min_count:
                min_count = stats['profiles_scraped']
                least_used = location
        
        if least_used:
            # Find the index of the least used location
            self.current_location_index = self.locations.index(least_used)
            return least_used
        
        # Fallback to the first location
        self.current_location_index = 0
        return self.locations[0]
    
    def update_location_stats(self, location: str, scraped: int = 0, skipped: int = 0, errors: int = 0) -> None:
        """Update statistics for a location.
        
        Args:
            location: Location to update stats for
            scraped: Number of profiles successfully scraped
            skipped: Number of profiles skipped
            errors: Number of errors encountered
        """
        if location in self.location_stats:
            self.location_stats[location]['profiles_scraped'] += scraped
            self.location_stats[location]['profiles_skipped'] += skipped
            self.location_stats[location]['errors'] += errors
    
    def get_location_stats(self, location: Optional[str] = None) -> Dict:
        """Get statistics for a location or all locations.
        
        Args:
            location: Specific location to get stats for, or None for all locations
            
        Returns:
            Dict: Location statistics
        """
        if location:
            return self.location_stats.get(location, {})
        return self.location_stats
    
    def should_change_location(self, current_location: str) -> bool:
        """Determine if it's time to change location based on profiles scraped.
        
        Args:
            current_location: Current location being used
            
        Returns:
            bool: True if location should be changed, False otherwise
        """
        if current_location not in self.location_stats:
            return True
        
        profiles_scraped = self.location_stats[current_location]['profiles_scraped']
        return profiles_scraped >= self.profiles_per_location
    
    def get_top_locations(self, count: int = 5) -> List[Tuple[str, int]]:
        """Get the top locations with the most scraped profiles.
        
        Args:
            count: Number of top locations to return
            
        Returns:
            List[Tuple[str, int]]: List of (location, profile_count) tuples
        """
        location_counts = [(loc, stats['profiles_scraped']) for loc, stats in self.location_stats.items()]
        location_counts.sort(key=lambda x: x[1], reverse=True)
        return location_counts[:count]
