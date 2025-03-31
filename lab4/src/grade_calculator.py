# src/grade_calculator.py
import pandas as pd
import numpy as np
from .config import AppConfig
import logging

class GradeCalculator:
    """Calculates national scale grades based on scores."""

    @staticmethod
    def calculate_national_scale(df: pd.DataFrame, config: AppConfig) -> pd.DataFrame:
        """
        Adds national scale grade columns to the DataFrame.

        Args:
            df: The DataFrame with score columns.
            config: The application configuration object.

        Returns:
            DataFrame with added national scale columns.
        """
        df_graded = df.copy()
        logging.info("Calculating national scale grades...")

        # Prepare bins and labels from config
        # Sort ranges to ensure correct binning
        sorted_scales = sorted(config.grade_scales.items(), key=lambda item: item[0][0]) 
        bins = [config.min_score - 1] + [upper for (lower, upper), grade in sorted_scales]
        labels = [grade for (lower, upper), grade in sorted_scales]
        
        # Ensure the upper bound matches the max possible score if needed
        if bins[-1] < config.max_score:
             # This logic might need adjustment depending on how ranges are defined
             # If 100 should be 'Відмінно', the range (90, 100) and bins work.
             # If a score of exactly 100 needs a special check, add it here.
             pass 

        logging.debug(f"Using bins: {bins}")
        logging.debug(f"Using labels: {labels}")

        for score_col in config.subject_score_columns:
            national_scale_col = config.get_national_scale_column_name(score_col)
            
            if pd.api.types.is_numeric_dtype(df_graded[score_col]):
                logging.debug(f"Calculating scale for: {score_col} -> {national_scale_col}")
                df_graded[national_scale_col] = pd.cut(
                    df_graded[score_col],
                    bins=bins,
                    labels=labels,
                    right=True,       # Intervals are closed on the right (e.g., (74, 89] -> Добре)
                    include_lowest=False # Change if min_score itself needs a specific grade
                )
                 # Handle potential NaNs in score column - they should remain NaN in grade column
                df_graded[national_scale_col] = df_graded[national_scale_col].astype('object') # To allow NaN storage if needed
                df_graded.loc[df_graded[score_col].isnull(), national_scale_col] = np.nan

            else:
                logging.warning(f"Cannot calculate national scale for non-numeric column: {score_col}. Skipping.")
                df_graded[national_scale_col] = "N/A" # Or np.nan

        logging.info("National scale calculation completed.")
        return df_graded