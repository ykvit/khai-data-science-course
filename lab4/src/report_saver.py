import pandas as pd
from pathlib import Path
from .config import AppConfig
import logging

class ReportSaverError(Exception):
    """Custom exception for report saving errors."""
    pass

class ReportSaver:
    """Handles saving the processed DataFrame to a file."""

    @staticmethod
    def save_results(df: pd.DataFrame, config: AppConfig):
        """
        Saves the DataFrame to the specified output Excel file.

        Args:
            df: The DataFrame to save.
            config: The application configuration object.

        Raises:
            ReportSaverError: If the output directory cannot be created or the file cannot be saved.
        """
        output_path = Path(config.output_file)
        output_dir = output_path.parent

        try:
            # Create output directory if it doesn't exist
            output_dir.mkdir(parents=True, exist_ok=True)
            logging.info(f"Ensured output directory exists: {output_dir}")

            # Save to Excel
            logging.info(f"Saving processed data to {output_path}")
            df.to_excel(output_path, index=False, engine='openpyxl') # Specify engine
            logging.info("Results saved successfully.")

        except PermissionError:
             logging.error(f"Permission denied when trying to create directory or save file: {output_path}")
             raise ReportSaverError(f"Permission denied for '{output_path}'. Check file/folder permissions.")
        except Exception as e:
            logging.error(f"Failed to save results to {output_path}: {e}", exc_info=True)
            raise ReportSaverError(f"Could not save results to '{output_path}'. Reason: {e}")