# src/data_loader.py
import pandas as pd
from pathlib import Path
from .config import AppConfig
import logging # Use logging instead of print for better control

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DataLoaderError(Exception):
    """Custom exception for data loading errors."""
    pass

class DataLoader:
    """Handles loading data from the source file."""

    @staticmethod
    def load_data(config: AppConfig) -> pd.DataFrame:
        """
        Loads student data from the specified Excel file and sheet.

        Args:
            config: The application configuration object.

        Returns:
            A pandas DataFrame containing the student data.

        Raises:
            DataLoaderError: If the file is not found or cannot be read.
            KeyError: If essential columns specified in config are missing.
        """
        input_path = Path(config.input_file)
        if not input_path.exists():
            logging.error(f"Input file not found: {config.input_file}")
            raise DataLoaderError(f"Input file not found: {config.input_file}")

        try:
            logging.info(f"Loading data from '{config.input_file}', sheet: '{config.sheet_name}'")
            df = pd.read_excel(input_path, sheet_name=config.sheet_name)
            logging.info(f"Data loaded successfully. Shape: {df.shape}")
            
            # --- Basic Structure Validation ---
            required_columns = [config.name_column, config.group_column] + config.subject_score_columns
            missing_cols = [col for col in required_columns if col not in df.columns]
            if missing_cols:
                 logging.error(f"Missing required columns in the input file: {missing_cols}")
                 raise KeyError(f"Missing required columns: {missing_cols}. Please check config.py or the input file '{config.input_file}'.")
            
            # Check if score columns are numeric (or can be converted)
            for col in config.subject_score_columns:
                 # Attempt conversion, coerce errors to NaN
                 df[col] = pd.to_numeric(df[col], errors='coerce')
                 if df[col].isnull().all():
                      logging.warning(f"Column '{col}' contains no valid numeric data after coercion.")


            logging.info("Initial data structure validation passed.")
            return df

        except FileNotFoundError:
             logging.error(f"Input file not found during read: {config.input_file}")
             raise DataLoaderError(f"Input file not found: {config.input_file}")
        except KeyError as e:
             raise e # Re-raise the specific KeyError from validation
        except Exception as e:
            logging.error(f"Failed to load or perform initial validation on data from {config.input_file}: {e}", exc_info=True)
            raise DataLoaderError(f"Could not read or validate data from file '{config.input_file}'. Reason: {e}")