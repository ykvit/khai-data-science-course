import pytest
import pandas as pd
import numpy as np

from src.config import AppConfig
from src.grade_calculator import GradeCalculator

@pytest.fixture
def test_config():
    return AppConfig(
        subject_score_columns=['Score'],
        min_score=60,
        max_score=100,
        grade_scales={
            (90, 100): "Відмінно",
            (75, 89): "Добре",
            (60, 74): "Задовільно"
        },
        national_scale_suffix='_Grade' 
    )

@pytest.fixture
def scores_dataframe():
    return pd.DataFrame({
        'Score': [95, 100, 89, 75, 74, 60, 59, 101, np.nan]
    })

def test_calculate_national_scale_grades(test_config, scores_dataframe):
    """Перевіряє правильність призначення національних оцінок."""
    graded_df = GradeCalculator.calculate_national_scale(scores_dataframe.copy(), test_config)
    
    expected_grades = [
        "Відмінно",    # 95
        "Відмінно",    # 100
        "Добре",       # 89
        "Добре",       # 75
        "Задовільно",  # 74
        "Задовільно",  # 60
        np.nan,        # 59 (нижче min_score, але cut не має мітки для цього) -> NaN
        np.nan,        # 101 (вище max_score, cut не має мітки) -> NaN
        np.nan         # np.nan -> np.nan
    ]
    
    actual_grades = graded_df['Score_Grade'].tolist()

    assert len(actual_grades) == len(expected_grades)
    for actual, expected in zip(actual_grades, expected_grades):
        if pd.isna(expected):
            assert pd.isna(actual)
        else:
            assert actual == expected

def test_calculate_national_scale_multiple_columns(test_config):
    """Перевіряє роботу з кількома колонками оцінок."""
    test_config.subject_score_columns = ['Math_Score', 'Physics_Score']
    df = pd.DataFrame({
        'Math_Score': [90, 70],
        'Physics_Score': [78, 62]
    })
    graded_df = GradeCalculator.calculate_national_scale(df.copy(), test_config)

    assert 'Math_Score_Grade' in graded_df.columns
    assert 'Physics_Score_Grade' in graded_df.columns
    assert graded_df['Math_Score_Grade'].tolist() == ["Відмінно", "Задовільно"]
    assert graded_df['Physics_Score_Grade'].tolist() == ["Добре", "Задовільно"]