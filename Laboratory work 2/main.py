"""Main entry point for the data processing application."""

import os
from pathlib import Path

from src.data_processor import DataProcessor
from src.statistics import StatisticsCalculator


def get_project_root() -> Path:
    """Get the absolute path to the project root directory."""
    current_file = Path(__file__).resolve()
    return current_file.parent


def main():
    """Execute the main data processing and analysis workflow."""
    project_root = get_project_root()
    
    input_file = project_root / 'data' / 'LW2.txt'
    output_file = project_root / 'output' / 'processed_data.json'
    
    data_processor = DataProcessor()
    
    try:
        if not input_file.exists():
            raise FileNotFoundError(
                f"Input file not found at: {input_file}\n"
                f"Current working directory: {os.getcwd()}\n"
                f"Project root: {project_root}"
            )
        
        raw_data = data_processor.parse_data(input_file)
        cleaned_data = data_processor.clean_data(raw_data)
        
        calculator = StatisticsCalculator(cleaned_data)
        statistics = calculator.calculate_statistics()
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        data_processor.save_processed_data(
            cleaned_data,
            statistics,
            output_file
        )
        
        print("Data processing completed successfully!")
        print(f"Results saved to: {output_file}")
        
    except Exception as e:
        print(f"Error processing data: {str(e)}")


if __name__ == "__main__":
    main()
