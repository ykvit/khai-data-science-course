import pandas as pd
from .config import AppConfig
from .data_loader import DataLoader, DataLoaderError 
from .report_saver import ReportSaver, ReportSaverError
from .data_cleaner import DataCleaner
from .grade_calculator import GradeCalculator
from .scholarship import ScholarshipDeterminer
import logging
from typing import Dict, Any, Optional


class DataAnalyzer:
    """
    Facade class to orchestrate the student data analysis workflow.
    It coordinates loading, cleaning, calculating, and analyzing data.
    """
    def __init__(self, config: AppConfig):
        """
        Initializes the DataAnalyzer with configuration.

        Args:
            config: The application configuration object.
        """
        self.config = config
        self.raw_df: Optional[pd.DataFrame] = None      # Loaded data
        self.processed_df: Optional[pd.DataFrame] = None # Fully processed data
        self._is_processed = False

    def process_data(self) -> None:
        """
        Executes the full data processing pipeline:
        Load -> Clean -> Calculate Grades -> Determine Scholarships.
        Stores the final DataFrame in self.processed_df.
        """
        if self._is_processed:
            logging.info("Data already processed. Skipping reprocessing.")
            return
            
        logging.info("Starting data processing pipeline...")
        try:
            # 1. Load
            self.raw_df = DataLoader.load_data(self.config)

            # 2. Clean
            cleaned_df = DataCleaner.clean_data(self.raw_df, self.config)

            # 3. Calculate National Scale
            graded_df = GradeCalculator.calculate_national_scale(cleaned_df, self.config)

            # 4. Determine Scholarships (includes GPA)
            self.processed_df = ScholarshipDeterminer.determine_scholarships(graded_df, self.config)

            self._is_processed = True
            logging.info("Data processing pipeline completed successfully.")

        except (DataLoaderError, KeyError, Exception) as e:
             # Log specific errors from components if they occur
             logging.error(f"Data processing failed: {e}", exc_info=True)
             # Decide if we should re-raise or handle/store the error state
             raise # Re-raise the exception to be caught by the caller (e.g., main.py)

    def save_processed_data(self) -> None:
        """Saves the processed data to the output file specified in config."""
        if not self._is_processed or self.processed_df is None:
            logging.error("Cannot save data. Processing has not been run successfully.")
            raise RuntimeError("Data must be processed successfully before saving.")
        
        try:
            ReportSaver.save_results(self.processed_df, self.config)
        except ReportSaverError as e:
            logging.error(f"Failed to save report: {e}")
            raise # Re-raise to inform the caller

    def get_overall_stats(self) -> Dict[str, Any]:
        """
        Calculates overall statistics from the processed data.

        Returns:
            A dictionary containing:
            - 'highest_gpa_student': Name of the student with the highest GPA.
            - 'lowest_gpa_student': Name of the student with the lowest GPA.
            - 'total_students': Total number of students processed.
            - 'scholarship_recipients_count': Number of students receiving scholarships.
            - 'average_gpa_overall': The average GPA across all students.
        
        Raises:
            RuntimeError: If data has not been processed yet.
        """
        if not self._is_processed or self.processed_df is None:
             logging.error("Cannot get overall stats. Data not processed.")
             raise RuntimeError("Data must be processed before getting statistics.")
        
        stats = {}
        df = self.processed_df.dropna(subset=[self.config.gpa_column]) # Analyze only those with valid GPA

        if df.empty:
             logging.warning("No students with valid GPA to calculate overall stats.")
             return {
                 'highest_gpa_student': None,
                 'lowest_gpa_student': None,
                 'total_students': len(self.processed_df), # Total rows loaded/processed
                 'scholarship_recipients_count': 0,
                 'average_gpa_overall': None
             }

        stats['highest_gpa_student'] = df.loc[df[self.config.gpa_column].idxmax(), self.config.name_column]
        stats['lowest_gpa_student'] = df.loc[df[self.config.gpa_column].idxmin(), self.config.name_column]
        stats['total_students'] = len(self.processed_df)
        stats['scholarship_recipients_count'] = (self.processed_df[self.config.scholarship_column] == self.config.scholarship_marker).sum()
        stats['average_gpa_overall'] = df[self.config.gpa_column].mean()

        logging.info(f"Calculated overall stats: {stats}")
        return stats

    def get_group_stats(self, group_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Filters data for a specific group (if provided, otherwise uses config's target_group) 
        and calculates statistics for that group.

        Args:
            group_id: The identifier of the group to analyze. If None, uses 
                      config.target_group.

        Returns:
            A dictionary containing stats specific to the group:
            - 'group_id': The group analyzed.
            - 'students_in_group': Number of students in this group.
            - 'highest_gpa_student_in_group': Name of the highest scorer in the group.
            - 'lowest_gpa_student_in_group': Name of the lowest scorer in the group.
            - 'scholarship_recipients_in_group': Count of scholars in the group.
            - 'average_gpa_in_group': Average GPA for the group.
        
        Raises:
            RuntimeError: If data has not been processed yet.
            ValueError: If the specified group_id is not found.
        """
        if not self._is_processed or self.processed_df is None:
            logging.error("Cannot get group stats. Data not processed.")
            raise RuntimeError("Data must be processed before getting group statistics.")

        target_group = group_id if group_id is not None else self.config.target_group
        logging.info(f"Calculating statistics for group: {target_group}")
        
        # Filter data for the target group
        group_df = self.processed_df[self.processed_df[self.config.group_column] == target_group]

        if group_df.empty:
            logging.warning(f"Group '{target_group}' not found or has no students in the processed data.")
            # Option 1: Raise an error
            raise ValueError(f"Group '{target_group}' not found in the data.")
            # Option 2: Return empty/None stats
            # return { 'group_id': target_group, 'students_in_group': 0, ... None/0 for others ... }

        # Calculate stats for the filtered group (handle potential NaNs in GPA)
        group_df_valid_gpa = group_df.dropna(subset=[self.config.gpa_column])
        
        stats = {'group_id': target_group}
        stats['students_in_group'] = len(group_df)

        if group_df_valid_gpa.empty:
             logging.warning(f"No students with valid GPA in group '{target_group}'.")
             stats['highest_gpa_student_in_group'] = None
             stats['lowest_gpa_student_in_group'] = None
             stats['average_gpa_in_group'] = None
             # Scholarship count still calculated from original marking, even if GPA is NaN now (unlikely)
             stats['scholarship_recipients_in_group'] = (group_df[self.config.scholarship_column] == self.config.scholarship_marker).sum()
        else:
             stats['highest_gpa_student_in_group'] = group_df_valid_gpa.loc[group_df_valid_gpa[self.config.gpa_column].idxmax(), self.config.name_column]
             stats['lowest_gpa_student_in_group'] = group_df_valid_gpa.loc[group_df_valid_gpa[self.config.gpa_column].idxmin(), self.config.name_column]
             stats['average_gpa_in_group'] = group_df_valid_gpa[self.config.gpa_column].mean()
             stats['scholarship_recipients_in_group'] = (group_df[self.config.scholarship_column] == self.config.scholarship_marker).sum()


        logging.info(f"Calculated stats for group '{target_group}': {stats}")
        return stats
        
    # --- Methods for Future Expansion (Placeholders) ---
    
    def find_student_by_name(self, name_substring: str) -> Optional[pd.DataFrame]:
        """Finds student(s) by full or partial name match (case-insensitive)."""
        if not self._is_processed or self.processed_df is None:
            raise RuntimeError("Data must be processed first.")
        # Use contains for partial matching
        results = self.processed_df[self.processed_df[self.config.name_column].str.contains(name_substring, case=False, na=False)]
        return results if not results.empty else None

    def get_scholarship_students(self) -> Optional[pd.DataFrame]:
         """Returns a DataFrame of all students who receive scholarships."""
         if not self._is_processed or self.processed_df is None:
            raise RuntimeError("Data must be processed first.")
         scholars = self.processed_df[self.processed_df[self.config.scholarship_column] == self.config.scholarship_marker]
         return scholars if not scholars.empty else None
         
    # get_group_data(group_id) -> returns the filtered dataframe for plotting/reporting
    def get_group_data(self, group_id: Optional[str] = None) -> Optional[pd.DataFrame]:
         """Returns the processed data filtered for a specific group."""
         if not self._is_processed or self.processed_df is None:
            raise RuntimeError("Data must be processed first.")
         
         target_group = group_id if group_id is not None else self.config.target_group
         group_df = self.processed_df[self.processed_df[self.config.group_column] == target_group]
         
         return group_df if not group_df.empty else None