# src/data_cleaner.py
import pandas as pd
import numpy as np
from .config import AppConfig
import logging

class DataCleaner:
    """Handles cleaning operations on the student DataFrame."""

    @staticmethod
    def clean_data(df: pd.DataFrame, config: AppConfig) -> pd.DataFrame:
        """
        Cleans the DataFrame by handling duplicates and invalid scores.

        Args:
            df: The DataFrame to clean.
            config: The application configuration object.

        Returns:
            A cleaned pandas DataFrame.
        """
        df_cleaned = df.copy()

        # 1. Handle Duplicates based on Name Column
        initial_rows = len(df_cleaned)
        duplicates = df_cleaned[df_cleaned.duplicated(subset=[config.name_column], keep=False)]
        if not duplicates.empty:
            logging.warning(f"Found {len(duplicates)} rows with duplicate names based on column '{config.name_column}'. Keeping first occurrence.")
            # Optional: Log the names of duplicates
            # logging.debug(f"Duplicate names: {duplicates[config.name_column].tolist()}")
            df_cleaned = df_cleaned.drop_duplicates(subset=[config.name_column], keep='first')
            logging.info(f"Removed {initial_rows - len(df_cleaned)} duplicate rows.")
        else:
            logging.info("No duplicate names found.")

        # 2. Validate Score Ranges for Subject Columns
        logging.info(f"Validating scores in columns: {config.subject_score_columns} (Range: {config.min_score}-{config.max_score})")
        for col in config.subject_score_columns:
            # Ensure column is numeric first (might have been object if loading failed subtly)
            if not pd.api.types.is_numeric_dtype(df_cleaned[col]):
                 logging.warning(f"Skipping score validation for non-numeric column: {col}")
                 continue
                 
            # Find scores outside the valid range [min_score, max_score]
            invalid_mask = (df_cleaned[col] < config.min_score) | (df_cleaned[col] > config.max_score)
            invalid_count = invalid_mask.sum()

            if invalid_count > 0:
                logging.warning(f"Found {invalid_count} scores in column '{col}' outside the valid range ({config.min_score}-{config.max_score}). Setting them to NaN.")
                # Optional: Log details of students with invalid scores
                # invalid_students = df_cleaned.loc[invalid_mask, config.name_column].tolist()
                # logging.debug(f"Students with invalid scores in {col}: {invalid_students}")
                df_cleaned.loc[invalid_mask, col] = np.nan # Set invalid scores to NaN

        # 3. Optional: Handle rows where ALL scores might be NaN after cleaning
        # df_cleaned = df_cleaned.dropna(subset=config.subject_score_columns, how='all')
        # logging.info("Removed rows where all subject scores were invalid/NaN.")
        # Decide if this step is needed based on requirements.

        logging.info("Data cleaning completed.")
        return df_cleaned