"""Data models for the application."""

from dataclasses import dataclass
from typing import Dict


@dataclass
class Person:
    """Represents a person's physical characteristics."""
    
    name: str
    height: float
    weight: float
    
    @property
    def bmi(self) -> float:
        """Calculate Body Mass Index (BMI)."""
        return self.weight / (self.height * self.height)


class WeightCategory:
    """Constants and methods for BMI categories."""
    
    UNDERWEIGHT_THRESHOLD = 18.5
    NORMAL_THRESHOLD = 25.0
    
    UNDERWEIGHT = "underweight"
    NORMAL = "normal"
    OVERWEIGHT = "overweight"
    
    @staticmethod
    def determine_category(bmi: float) -> str:
        """Determine weight category based on BMI value."""
        if bmi < WeightCategory.UNDERWEIGHT_THRESHOLD:
            return WeightCategory.UNDERWEIGHT
        if bmi < WeightCategory.NORMAL_THRESHOLD:
            return WeightCategory.NORMAL
        return WeightCategory.OVERWEIGHT