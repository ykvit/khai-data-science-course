# tests/test_data_cleaner.py
import pytest
import pandas as pd
import numpy as np

from src.config import AppConfig
from src.data_cleaner import DataCleaner

@pytest.fixture
def test_config():
    # Спрощена конфігурація для тестів очищення
    return AppConfig(
        name_column='Name',
        subject_score_columns=['Score1', 'Score2'],
        min_score=60,
        max_score=100
    )

@pytest.fixture
def sample_dirty_dataframe():
    return pd.DataFrame({
        'Name': ['Alice', 'Bob', 'Alice', 'Charlie', 'David', 'Eve'],
        'Group': ['A', 'B', 'A', 'C', 'B', 'C'],
        'Score1': [90, 55, 95, 75, 105, 60], # 55 < min, 105 > max
        'Score2': [80, 85, 88, np.nan, 70, 65] 
    })

# --- Тести ---

def test_clean_data_remove_duplicates(test_config, sample_dirty_dataframe):
    """Перевіряє видалення дублікатів за іменем."""
    cleaned_df = DataCleaner.clean_data(sample_dirty_dataframe.copy(), test_config)
    # Повинна залишитись перша 'Alice'
    assert len(cleaned_df) == 5 # 6 -> 5
    assert 'Alice' in cleaned_df['Name'].tolist()
    assert cleaned_df['Name'].value_counts()['Alice'] == 1
    # Перевіряємо, що саме перша 'Alice' залишилась (за індексом або значенням Score1)
    assert cleaned_df.loc[cleaned_df['Name'] == 'Alice', 'Score1'].iloc[0] == 90 # або 95 в залежності від логіки drop_duplicates, тут має бути 90

def test_clean_data_invalidate_scores(test_config, sample_dirty_dataframe):
    """Перевіряє заміну невалідних оцінок на NaN."""
    cleaned_df = DataCleaner.clean_data(sample_dirty_dataframe.copy(), test_config)
    
    # Bob's Score1 був 55, має стати NaN
    assert pd.isna(cleaned_df.loc[cleaned_df['Name'] == 'Bob', 'Score1'].iloc[0])
    
    # David's Score1 був 105, має стати NaN
    assert pd.isna(cleaned_df.loc[cleaned_df['Name'] == 'David', 'Score1'].iloc[0])
    
    # Інші валідні оцінки не мають змінитися (крім дублікатів)
    assert cleaned_df.loc[cleaned_df['Name'] == 'Charlie', 'Score1'].iloc[0] == 75
    assert cleaned_df.loc[cleaned_df['Name'] == 'Eve', 'Score1'].iloc[0] == 60

def test_clean_data_combined(test_config, sample_dirty_dataframe):
    """Перевіряє одночасну роботу видалення дублікатів та інвалідації оцінок."""
    cleaned_df = DataCleaner.clean_data(sample_dirty_dataframe.copy(), test_config)
    
    assert len(cleaned_df) == 5
    
    # Перевіряємо і дублікат, і валідні/невалідні оцінки
    alice_row = cleaned_df[cleaned_df['Name'] == 'Alice']
    assert len(alice_row) == 1
    assert alice_row['Score1'].iloc[0] == 90 # Перший запис Alice, Score1 валідна
    assert alice_row['Score2'].iloc[0] == 80

    bob_row = cleaned_df[cleaned_df['Name'] == 'Bob']
    assert pd.isna(bob_row['Score1'].iloc[0]) # Score1 стала NaN
    assert bob_row['Score2'].iloc[0] == 85

    david_row = cleaned_df[cleaned_df['Name'] == 'David']
    assert pd.isna(david_row['Score1'].iloc[0]) # Score1 стала NaN
    assert david_row['Score2'].iloc[0] == 70

def test_clean_data_no_changes_needed(test_config):
    """Перевіряє, що чистий DataFrame залишається незмінним."""
    clean_df = pd.DataFrame({
        'Name': ['Alice', 'Bob'],
        'Group': ['A', 'B'],
        'Score1': [90, 70],
        'Score2': [85, 65]
    })
    cleaned_df = DataCleaner.clean_data(clean_df.copy(), test_config)
    pd.testing.assert_frame_equal(cleaned_df, clean_df)