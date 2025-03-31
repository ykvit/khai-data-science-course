# src/config.py
from dataclasses import dataclass, field
from typing import List, Dict, Tuple

@dataclass
class AppConfig:
    """Holds configuration settings for the student analysis application."""
    
    # --- File Paths ---
    input_file: str = 'data/LW3.xlsx'
    output_file: str = 'output/LW3_processed.xlsx'
    sheet_name: str | int = 0  # Default to the first sheet

    # --- Column Names (CRITICAL - Adjust based on actual Excel file) ---
    name_column: str = 'Студент (2020)' # Example, adjust!
    group_column: str = 'Група'         # Example, adjust!
    # Automatically find subject columns ending with '(бали)' or similar?
    # Or list them explicitly if names are fixed? Let's try explicit first.
    # If subject columns can change, we'll need a discovery mechanism.
    subject_score_columns: List[str] = field(default_factory=lambda: [
        'Дискретна математика (бали)',
        'Вища математика (бали)',
        'Англійська мова (Бали)', # Note potential inconsistency 'Бали' vs 'бали'
        'Вибіркова дисципліна 1 (бали)',
        'Вибіркова дисципліна 2 (бали)'
    ])

    # --- Calculation Parameters ---
    min_score: int = 60
    max_score: int = 100
    scholarship_percentage: float = 0.60
    
    # National grade scale mapping (score range -> grade name)
    grade_scales: Dict[Tuple[int, int], str] = field(default_factory=lambda: {
        (90, 100): "Відмінно",
        (75, 89): "Добре",
        (60, 74): "Задовільно" 
        # Add lower bound if needed, e.g., (0, 59): "Незадовільно" if relevant
    })
    
    # --- Derived Column Names ---
    gpa_column: str = 'Середній бал (GPA)'
    scholarship_column: str = 'Стипендія'
    scholarship_marker: str = '*'
    national_scale_suffix: str = ' (нац шкала)' # Suffix for new grade columns

    # --- Group Specific Analysis ---
    target_group: str = "536ст" # <<< ЗАМІНИ НА НОМЕР СВОЄЇ ГРУПИ! 
                               # Можна передавати через аргумент командного рядка пізніше

    def get_national_scale_column_name(self, score_column: str) -> str:
        """Generates the name for the national scale column based on the score column."""
        # Remove "(бали)" or similar suffix before adding the new one
        base_name = score_column.replace('(бали)', '').replace('(Бали)', '').strip()
        return f"{base_name}{self.national_scale_suffix}"