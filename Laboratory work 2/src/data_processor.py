"""Module for processing and validating person-related data."""

import re
import json
from typing import List, Dict, Optional
from pathlib import Path

from .models import Person


class DataProcessor:
    """
    Handles data processing operations for person-related information.
    
    Provides functionality for reading, parsing, cleaning,
    and saving data about individuals' physical characteristics.
    """
    
    def __init__(self, input_encoding: str = 'utf-8'):
        """Initialize with specified encoding for input files."""
        self.input_encoding = input_encoding
    
    def parse_data(self, filename: Path) -> List[Dict]:
        """
        Read and parse data from an input file containing person information.
        
        Args:
            filename: Path object pointing to the input file.
            
        Returns:
            List of dictionaries containing parsed person data.
            
        Raises:
            FileNotFoundError: If the input file doesn't exist.
            ValueError: If the file cannot be read with supported encodings.
        """
        try:
            with open(filename, 'r', encoding=self.input_encoding) as file:
                lines = file.readlines()
                print(f"Read {len(lines)} lines from {filename}")
                
                parsed_data = []
                for i, line in enumerate(lines, 1):
                    if line.strip():
                        entry = self._parse_line(line)
                        if entry:
                            parsed_data.append(entry)
                        else:
                            print(f"Warning: Could not parse line {i}: {line.strip()}")
                
                print(f"Successfully parsed {len(parsed_data)} entries")
                return parsed_data
                
        except UnicodeDecodeError:
            print("Error: File encoding issue. Trying alternative encodings...")
            
            for encoding in ['cp1251', 'windows-1251', 'ascii']:
                try:
                    with open(filename, 'r', encoding=encoding) as file:
                        lines = file.readlines()
                        print(f"Successfully read file with {encoding} encoding")
                        return [
                            self._parse_line(line)
                            for line in lines
                            if line.strip()
                        ]
                except UnicodeDecodeError:
                    continue
            
            raise ValueError("Could not read file with any supported encoding")
    
    def _parse_line(self, line: str) -> Dict:
        """Parse a single line of input data."""
        line = line.strip().lstrip('\ufeff')
        parts = re.split(r'\s+', line)
        
        if len(parts) >= 4:
            name_parts = parts[:-2]
            height_str = parts[-2]
            weight_str = parts[-1]
            
            return {
                'name': ' '.join(name_parts),
                'height': height_str,
                'weight': weight_str
            }
        
        print(f"Warning: Invalid line format: {line}")
        return {}
    
    def clean_data(self, data: List[Dict]) -> List[Person]:
        """
        Clean and validate input data.
        
        Args:
            data: Raw data entries.
            
        Returns:
            List of validated Person objects.
        """
        cleaned_data = []
        print(f"Starting data cleaning for {len(data)} entries")
        
        for i, entry in enumerate(data, 1):
            try:
                person = self._validate_and_create_person(entry)
                if person:
                    cleaned_data.append(person)
                else:
                    print(f"Warning: Entry {i} failed validation: {entry}")
            except (ValueError, KeyError) as e:
                print(f"Error processing entry {i}: {entry}")
                print(f"Error details: {str(e)}")
                continue
        
        print(f"Successfully cleaned {len(cleaned_data)} entries")
        return cleaned_data
    
    def _validate_and_create_person(self, entry: Dict) -> Optional[Person]:
        """Validate entry data and create a Person object."""
        try:
            if not entry:
                return None
            
            height = float(entry['height'].replace(',', '.'))
            weight = float(entry['weight'].replace(',', '.'))
            
            if not (140 <= height <= 210):
                print(f"Warning: Height {height} is outside valid range (140-210)")
                return None
            
            if not (45 <= weight <= 125):
                print(f"Warning: Weight {weight} is outside valid range (45-125)")
                return None
            
            name_parts = entry['name'].split()
            formatted_name = ' '.join(part.capitalize() for part in name_parts)
            
            return Person(
                name=formatted_name,
                height=height,
                weight=weight
            )
            
        except (ValueError, KeyError) as e:
            print(f"Error validating entry {entry}: {str(e)}")
            return None
    
    def save_processed_data(
        self,
        data: List[Person],
        stats: Dict,
        output_file: Path
    ) -> None:
        """
        Save processed data and statistics to JSON file.
        
        Args:
            data: Processed person data.
            stats: Statistical analysis results.
            output_file: Output file path.
        """
        output_data = {
            'processed_data': [
                {
                    'name': person.name,
                    'height': person.height,
                    'weight': person.weight,
                    'bmi': person.bmi
                }
                for person in data
            ],
            'statistics': stats
        }
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump(output_data, file, ensure_ascii=False, indent=2)
        
        print(f"Saved {len(data)} processed entries to {output_file}")