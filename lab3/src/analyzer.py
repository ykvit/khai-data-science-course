import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple

class StudentPerformanceAnalyzer:
    """A class to analyze student performance data and determine scholarship ratings."""
    
    def __init__(self, input_file: str, output_file: str):
        """Initialize the analyzer with input and output file paths."""
        self.input_file = Path(input_file)
        self.output_file = Path(output_file)
        self.df = None
        self.name_column = None  # Will store the actual name column
        
        # Configuration settings
        self.grade_scales = {
            (90, 100): "Excellent",
            (75, 89): "Good",
            (60, 74): "Satisfactory"
        }
        self.scholarship_percentage = 0.6

    def _find_name_column(self) -> str:
        """Identify the column containing student names."""
        # Common variations of name column
        possible_names = ['Full Name', 'FullName', 'Name', 'Student Name', 'StudentName']
        
        # Print all columns to help with debugging
        print("\nAvailable columns in the dataset:")
        print(self.df.columns.tolist())
        
        # Try to find the name column
        for col in possible_names:
            if col in self.df.columns:
                print(f"\nFound name column: '{col}'")
                return col
                
        # If no match found, use the first string column as a fallback
        string_columns = self.df.select_dtypes(include=['object']).columns
        if len(string_columns) > 0:
            first_col = string_columns[0]
            print(f"\nUsing first text column as name column: '{first_col}'")
            return first_col
            
        raise ValueError("Could not find a suitable name column in the dataset")

    def process_data(self) -> Tuple[str, str, int]:
        """
        Main method to process student data and generate analysis results.
        
        Returns:
            Tuple containing (highest_scorer, lowest_scorer, scholarship_count)
        """
        self._load_data()
        self.name_column = self._find_name_column()  # Identify the name column
        self._clean_data()
        self._calculate_national_scale()
        self._determine_scholarships()
        
        # Get performance statistics
        stats = self._get_performance_stats()
        
        # Save results
        self._save_results()
        
        return stats

    def _load_data(self) -> None:
        """Load data from Excel file and perform initial preprocessing."""
        try:
            self.df = pd.read_excel(self.input_file)
            print("Data loaded successfully")
        except Exception as e:
            raise Exception(f"Error loading data: {str(e)}")

    def _clean_data(self) -> None:
        """Clean the data by removing duplicates and validating score ranges."""
        # Check for duplicate names
        duplicates = self.df[self.df.duplicated(subset=[self.name_column], keep=False)]
        if not duplicates.empty:
            print(f"Warning: Duplicate names found:", duplicates[self.name_column].tolist())
            self.df = self.df.drop_duplicates(subset=[self.name_column], keep='first')
        
        # Validate score ranges
        # Get only numeric columns, excluding the name column
        score_columns = self.df.select_dtypes(include=[np.number]).columns
        
        for col in score_columns:
            invalid_scores = self.df[
                (self.df[col] < 60) | (self.df[col] > 100)
            ][self.name_column].tolist()
            if invalid_scores:
                print(f"Warning: Invalid scores in {col} for:", invalid_scores)
                self.df.loc[self.df[col] < 60, col] = np.nan
                self.df.loc[self.df[col] > 100, col] = np.nan

    def _calculate_national_scale(self) -> None:
        """Calculate national scale grades for each subject."""
        score_columns = self.df.select_dtypes(include=[np.number]).columns
        
        for col in score_columns:
            scale_col = f"{col}_Scale"
            self.df[scale_col] = pd.cut(
                self.df[col],
                bins=[59, 74, 89, 100],
                labels=["Satisfactory", "Good", "Excellent"],
                right=True
            )

    def _determine_scholarships(self) -> None:
        """Determine scholarship recipients based on GPA."""
        # Calculate GPA using only numeric columns (excluding scale columns)
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        score_columns = [col for col in numeric_cols if not col.endswith('_Scale')]
        
        self.df['GPA'] = self.df[score_columns].mean(axis=1)
        
        # Sort by GPA and mark top students for scholarship
        num_scholarships = int(len(self.df) * self.scholarship_percentage)
        self.df['Scholarship'] = ''
        self.df.loc[self.df['GPA'].nlargest(num_scholarships).index, 'Scholarship'] = '*'

    def _get_performance_stats(self) -> Tuple[str, str, int]:
        """Get performance statistics."""
        highest_scorer = self.df.loc[self.df['GPA'].idxmax(), self.name_column]
        lowest_scorer = self.df.loc[self.df['GPA'].idxmin(), self.name_column]
        scholarship_count = (self.df['Scholarship'] == '*').sum()
        
        return highest_scorer, lowest_scorer, scholarship_count

    def _save_results(self) -> None:
        """Save the processed data to Excel file."""
        # Create output directory if it doesn't exist
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        self.df.to_excel(self.output_file, index=False)
        print(f"\nResults saved to {self.output_file}")