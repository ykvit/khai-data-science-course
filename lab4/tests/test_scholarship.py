# tests/test_scholarship.py
import pytest
import pandas as pd
import numpy as np
import math

from src.config import AppConfig
from src.scholarship import ScholarshipDeterminer

@pytest.fixture
def test_config():
    return AppConfig(
        subject_score_columns=['Math', 'Physics'],
        gpa_column='GPA',
        scholarship_column='Scholarship',
        scholarship_marker='*',
        scholarship_percentage=0.60 # 60%
    )

@pytest.fixture
def students_dataframe():
    # 5 студентів, очікуємо ceil(5 * 0.6) = ceil(3.0) = 3 стипендії
    return pd.DataFrame({
        'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
        'Math':     [100, 90, 80, 70, 60],
        'Physics': [90,  80, 70, 60, 50] # Eve's Physics < 60, але для GPA рахуємо як є
    })

@pytest.fixture
def students_with_nan_dataframe():
    # 4 студенти, 1 з NaN. Очікуємо ceil(4 * 0.6) = ceil(2.4) = 3 стипендії
    return pd.DataFrame({
        'Name': ['Alice', 'Bob', 'Charlie', 'David'],
        'Math':     [100, 90, np.nan, 70],
        'Physics': [90,  80, 70, 60]
    })
    
@pytest.fixture
def students_with_ties_dataframe():
    # 6 студентів. Очікуємо ceil(6 * 0.6) = ceil(3.6) = 4 стипендії.
    # Є "нічия" за 4-те місце. nlargest(4, keep='first') візьме тільки першого.
    return pd.DataFrame({
        'Name': ['A', 'B', 'C', 'D', 'E', 'F'],
        'Math':     [100, 95, 90, 85, 85, 80], # GPA: 100, 95, 90, 85, 85, 80
        'Physics': [100, 95, 90, 85, 85, 80]
    })

# --- Тести ---

def test_determine_scholarships_gpa_calculation(test_config, students_dataframe):
    """Перевіряє правильність розрахунку GPA."""
    result_df = ScholarshipDeterminer.determine_scholarships(students_dataframe.copy(), test_config)
    expected_gpa = [95.0, 85.0, 75.0, 65.0, 55.0] # (100+90)/2, (90+80)/2, ...
    pd.testing.assert_series_equal(result_df[test_config.gpa_column], pd.Series(expected_gpa, name=test_config.gpa_column), check_dtype=False)

def test_determine_scholarships_gpa_with_nan(test_config, students_with_nan_dataframe):
    """Перевіряє розрахунок GPA при наявності NaN."""
    result_df = ScholarshipDeterminer.determine_scholarships(students_with_nan_dataframe.copy(), test_config)
    # Alice: (100+90)/2 = 95
    # Bob: (90+80)/2 = 85
    # Charlie: (NaN+70)/1 = 70 (mean ігнорує NaN)
    # David: (70+60)/2 = 65
    expected_gpa = [95.0, 85.0, 70.0, 65.0]
    pd.testing.assert_series_equal(result_df[test_config.gpa_column], pd.Series(expected_gpa, name=test_config.gpa_column), check_dtype=False)

def test_determine_scholarships_assignment(test_config, students_dataframe):
    """Перевіряє призначення стипендій (без нічиїх)."""
    result_df = ScholarshipDeterminer.determine_scholarships(students_dataframe.copy(), test_config)
    num_expected_scholarships = math.ceil(len(students_dataframe) * test_config.scholarship_percentage) # 3
    
    assert (result_df[test_config.scholarship_column] == test_config.scholarship_marker).sum() == num_expected_scholarships
    
    # Топ 3 - Alice, Bob, Charlie
    assert result_df.loc[result_df['Name'] == 'Alice', test_config.scholarship_column].iloc[0] == '*'
    assert result_df.loc[result_df['Name'] == 'Bob', test_config.scholarship_column].iloc[0] == '*'
    assert result_df.loc[result_df['Name'] == 'Charlie', test_config.scholarship_column].iloc[0] == '*'
    assert result_df.loc[result_df['Name'] == 'David', test_config.scholarship_column].iloc[0] == ''
    assert result_df.loc[result_df['Name'] == 'Eve', test_config.scholarship_column].iloc[0] == ''
    
def test_determine_scholarships_assignment_with_ties(test_config, students_with_ties_dataframe):
    """Перевіряє призначення стипендій при однакових GPA на межі."""
    result_df = ScholarshipDeterminer.determine_scholarships(students_with_ties_dataframe.copy(), test_config)
    num_expected_scholarships = math.ceil(len(students_with_ties_dataframe) * test_config.scholarship_percentage) # 4
    
    # ВИПРАВЛЕННЯ: nlargest(4, keep='first') поверне 4 індекси. Очікуємо 4 стипендії.
    assert (result_df[test_config.scholarship_column] == test_config.scholarship_marker).sum() == 4 

    assert result_df.loc[result_df['Name'] == 'A', test_config.scholarship_column].iloc[0] == '*'
    assert result_df.loc[result_df['Name'] == 'B', test_config.scholarship_column].iloc[0] == '*'
    assert result_df.loc[result_df['Name'] == 'C', test_config.scholarship_column].iloc[0] == '*'
    # ВИПРАВЛЕННЯ: D отримує стипендію (перший з однаковим балом на межі)
    assert result_df.loc[result_df['Name'] == 'D', test_config.scholarship_column].iloc[0] == '*' 
    # ВИПРАВЛЕННЯ: E не отримує стипендію (другий з однаковим балом)
    assert result_df.loc[result_df['Name'] == 'E', test_config.scholarship_column].iloc[0] == '' 
    assert result_df.loc[result_df['Name'] == 'F', test_config.scholarship_column].iloc[0] == ''

def test_determine_scholarships_no_valid_gpa(test_config):
    """Перевіряє випадок, коли немає валідних GPA для розрахунку."""
    df = pd.DataFrame({'Name': ['A'], 'Math': [np.nan], 'Physics': [np.nan]})
    result_df = ScholarshipDeterminer.determine_scholarships(df.copy(), test_config)
    assert pd.isna(result_df[test_config.gpa_column].iloc[0])
    assert (result_df[test_config.scholarship_column] == test_config.scholarship_marker).sum() == 0