import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
from pathlib import Path

from src.config import AppConfig
from src.data_loader import DataLoader, DataLoaderError

@pytest.fixture
def test_config():
    return AppConfig(
        input_file='dummy/path/test.xlsx',
        sheet_name=0,
        name_column='Student Name',
        group_column='Group',
        subject_score_columns=['Math', 'Physics']
    )

@pytest.fixture
def sample_input_dataframe(): 
    return pd.DataFrame({
        'Student Name': ['Alice', 'Bob'],
        'Group': ['A', 'B'],
        'Math': [90, 75],
        'Physics': [88, '65'] 
    })

@pytest.fixture
def expected_loaded_dataframe(): 
    return pd.DataFrame({
        'Student Name': ['Alice', 'Bob'],
        'Group': ['A', 'B'],
        'Math': [90, 75],
        'Physics': [88, 65] 
    }).astype({'Math': 'int64', 'Physics': 'int64'}) 

def test_load_data_success(mocker, test_config, sample_input_dataframe, expected_loaded_dataframe):
    """Тестуємо успішне завантаження та базову перевірку колонок."""
    mocker.patch.object(Path, 'exists', return_value=True)
    mock_read_excel = mocker.patch('pandas.read_excel', return_value=sample_input_dataframe.copy()) 

    df = DataLoader.load_data(test_config) 

    mock_read_excel.assert_called_once_with(Path(test_config.input_file), sheet_name=test_config.sheet_name)

    pd.testing.assert_frame_equal(df, expected_loaded_dataframe, check_dtype=True) 

def test_load_data_file_not_found(mocker, test_config):
    """Тестуємо випадок, коли файл не знайдено."""
    mocker.patch.object(Path, 'exists', return_value=False)
    mock_read_excel = mocker.patch('pandas.read_excel')

    with pytest.raises(DataLoaderError, match="Input file not found"):
        DataLoader.load_data(test_config)
    
    mock_read_excel.assert_not_called()

def test_load_data_missing_column(mocker, test_config, sample_input_dataframe): 
    """Тестуємо випадок, коли відсутня необхідна колонка."""
    df_missing_col = sample_input_dataframe.drop(columns=['Group'])
    mocker.patch.object(Path, 'exists', return_value=True)
    mocker.patch('pandas.read_excel', return_value=df_missing_col)

    with pytest.raises(KeyError, match=r"Missing required columns: \['Group'\]"):
        DataLoader.load_data(test_config)

def test_load_data_read_exception(mocker, test_config):
    """Тестуємо випадок помилки під час читання Excel."""
    mocker.patch.object(Path, 'exists', return_value=True)
    mocker.patch('pandas.read_excel', side_effect=Exception("Cannot read file"))

    with pytest.raises(DataLoaderError, match="Could not read or validate data"):
        DataLoader.load_data(test_config)