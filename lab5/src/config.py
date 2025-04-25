import pandas as pd
from pathlib import Path
import logging

class AppConfig:
    """Holds application configuration settings."""

    def __init__(self):
        """Initializes configuration settings."""
        logging.debug("Initializing AppConfig...")

        project_root = Path(__file__).parent.parent
        self.input_file = project_root / "data" / "LW3.xlsx"
        logging.debug(f"Input file path constructed as: {self.input_file.resolve()}")

        if not self.input_file.exists():
             logging.error(f"CRITICAL: Input file not found at resolved path: {self.input_file.resolve()}")
             raise FileNotFoundError(f"Input file not found: {self.input_file}")
        else:
             logging.info(f"Input file found at: {self.input_file.resolve()}")

        self.sheet_name = 0
        logging.info(f"Configured to read the first sheet (sheet_name=0)")

        self.output_dir = project_root / "output"
        self.output_file = self.output_dir / "processed_students.xlsx"
        logging.debug(f"Output directory set to: {self.output_dir.resolve()}")

        self.name_column = "Студент (2020)"
        self.group_column = "Група"
        self.subject_score_columns = [
            'Дискретна математика (бали)',
            'Вища математика (бали)',
            'Англійська мова (Бали)',
            'Вибіркова дисципліна 1 (бали)',
            'Вибіркова дисципліна 2 (бали)'
        ]

        if not self.subject_score_columns:
            logging.warning("Subject score columns list is empty in config.")

        self.national_scale_suffix = " (Нац. шкала)"
        self.gpa_column = "GPA"
        self.scholarship_column = "Стипендія"

        # --- Score & Grade Settings ---
        self.min_score = 0
        self.max_score = 100
        self.grade_scales = {
            (59, 74): "Задовільно",
            (74, 89): "Добре",
            (89, 100): "Відмінно",
            (-1, 59): "Незадовільно"
        }

        # --- Scholarship Settings ---
        self.scholarship_percentage = 0.60
        self.scholarship_marker = "Рекомендовано"

        # --- Target group ---
        self.target_group = "536ст"
        logging.debug("AppConfig initialized successfully.")


    # ... решта методів класу ...
    def get_national_scale_column_name(self, score_column_name: str) -> str:
        import re
        base_name = re.sub(r'\s*\((?:бали|Бали)\)\s*', '', score_column_name, flags=re.IGNORECASE).strip()
        return f"{base_name}{self.national_scale_suffix}"

    def get_all_national_scale_columns(self) -> list[str]:
         return [self.get_national_scale_column_name(col) for col in self.subject_score_columns]