# src/scholarship.py
import pandas as pd
import numpy as np
from .config import AppConfig
import logging
import math

class ScholarshipDeterminer:
    """Calculates GPA and determines scholarship recipients."""

    @staticmethod
    def determine_scholarships(df: pd.DataFrame, config: AppConfig) -> pd.DataFrame:
        """
        Calculates GPA and adds a scholarship marker column.

        Args:
            df: DataFrame with score columns.
            config: Application configuration.

        Returns:
            DataFrame with 'GPA' and 'Scholarship' columns added.
        """
        df_scholarship = df.copy()
        logging.info("Calculating GPA and determining scholarships...")

        # 1. Calculate GPA (Average Score)
        # Ensure we only average the numeric score columns specified
        valid_score_cols = [
            col for col in config.subject_score_columns 
            if pd.api.types.is_numeric_dtype(df_scholarship[col])
        ]
        if not valid_score_cols:
             logging.error("No valid numeric score columns found to calculate GPA.")
             # Decide how to handle this: raise error or add NaN column?
             df_scholarship[config.gpa_column] = np.nan 
        else:
             logging.info(f"Calculating GPA based on columns: {valid_score_cols}")
             # mean(axis=1) calculates row-wise mean, skipna=True ignores NaNs
             df_scholarship[config.gpa_column] = df_scholarship[valid_score_cols].mean(axis=1, skipna=True)
        
        # 2. Determine Scholarship Recipients
        # Handle cases where GPA calculation resulted in NaN (e.g., all scores were NaN)
        valid_gpa_df = df_scholarship.dropna(subset=[config.gpa_column])
        
        if valid_gpa_df.empty:
             logging.warning("No students with valid GPA found. Cannot determine scholarships.")
             df_scholarship[config.scholarship_column] = '' # Or np.nan
        else:
             # Calculate the number of scholarships to award (top X%)
             # Use ceil to ensure if fraction, we round up (or floor depending on exact rule)
             num_scholarships = math.ceil(len(valid_gpa_df) * config.scholarship_percentage) 
             logging.info(f"Total students with valid GPA: {len(valid_gpa_df)}. Awarding scholarships to top {config.scholarship_percentage*100:.1f}% ({num_scholarships} students).")

             # Find the indices of the top N students based on GPA
             # Handle ties: nlargest keeps all tied entries if they fall within the count
             top_students_indices = valid_gpa_df[config.gpa_column].nlargest(num_scholarships).index

             # Mark scholarship recipients
             df_scholarship[config.scholarship_column] = '' # Initialize column
             df_scholarship.loc[top_students_indices, config.scholarship_column] = config.scholarship_marker
             logging.info(f"Marked {len(top_students_indices)} students for scholarship.") # This might be > num_scholarships due to ties

        logging.info("Scholarship determination completed.")
        return df_scholarship