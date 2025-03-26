"""Statistical analysis module for person data."""

from typing import List, Dict
from statistics import mean
from collections import Counter

from .models import Person, WeightCategory


class StatisticsCalculator:
    """Handles all statistical calculations for the dataset."""
    
    def __init__(self, data: List[Person]):
        """Initialize with list of Person objects."""
        self.data = data
    
    def calculate_statistics(self) -> Dict:
        """
        Calculate comprehensive statistics for the dataset.
        
        Returns:
            Dict containing statistical characteristics including averages and categories.
        """
        if not self.data:
            return {}
        
        return {
            **self._calculate_basic_stats(),
            **self._calculate_category_percentages()
        }
    
    def _calculate_basic_stats(self) -> Dict:
        """Calculate basic statistical measures."""
        heights = [person.height for person in self.data]
        weights = [person.weight for person in self.data]
        
        return {
            'average_height': mean(heights),
            'average_weight': mean(weights),
            'min_height': min(heights),
            'max_height': max(heights),
            'min_weight': min(weights),
            'max_weight': max(weights)
        }
    
    def _calculate_category_percentages(self) -> Dict:
        """Calculate weight category distribution."""
        categories = [
            WeightCategory.determine_category(person.bmi)
            for person in self.data
        ]
        
        category_counts = Counter(categories)
        total_count = len(self.data)
        
        return {
            'category_percentages': {
                category: (count / total_count) * 100
                for category, count in category_counts.items()
            }
        }