# tests/test_analysis.py
import pytest
import pandas as pd
import numpy as np

from src.config import AppConfig
from src.analysis import DataAnalyzer
# Імпортуємо помилки для перевірки
from src.data_loader import DataLoaderError
from src.report_saver import ReportSaverError

# --- Фікстури ---

@pytest.fixture
def test_config():
    # Повна конфігурація для тестів аналізатора
    return AppConfig(
        input_file='fake_input.xlsx',
        output_file='fake_output.xlsx',
        name_column='Name',
        group_column='Group',
        subject_score_columns=['Math', 'Physics'],
        min_score=60,
        max_score=100,
        gpa_column='GPA',
        scholarship_column='Scholarship',
        scholarship_marker='*',
        scholarship_percentage=0.5, # 50% для простоти
        target_group='GroupA'
    )

@pytest.fixture
def processed_dataframe_fixture(test_config):
    # Готовий DataFrame, який міг би бути результатом process_data
    # GPA: A=95, B=85, C=75, D=95 (tie), E=65
    # Scholars (50% -> ceil(5*0.5)=3): A, B, D (тому що D=95) -> 3 стипендії
    return pd.DataFrame({
        test_config.name_column: ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
        test_config.group_column: ['GroupA', 'GroupB', 'GroupA', 'GroupB', 'GroupA'],
        'Math': [100, 90, 80, 100, 70],
        'Physics': [90, 80, 70, 90, 60],
        test_config.gpa_column: [95.0, 85.0, 75.0, 95.0, 65.0],
        test_config.scholarship_column: ['*', '*', '', '*', ''] 
        # Додамо колонки нац. шкали (для повноти, хоча вони тут не тестуються)
        # 'Math_Scale': ['Відмінно', 'Відмінно', 'Добре', 'Відмінно', 'Задовільно'],
        # 'Physics_Scale': ['Відмінно', 'Добре', 'Задовільно', 'Відмінно', 'Задовільно']
    })

@pytest.fixture
def analyzer_with_data(test_config, processed_dataframe_fixture):
    """Створює екземпляр аналізатора з вже "обробленими" даними."""
    analyzer = DataAnalyzer(test_config)
    analyzer.processed_df = processed_dataframe_fixture.copy()
    analyzer._is_processed = True # Позначаємо як оброблений
    return analyzer

# --- Тести ---

def test_analyzer_init(test_config):
    """Перевіряє ініціалізацію аналізатора."""
    analyzer = DataAnalyzer(test_config)
    assert analyzer.config == test_config
    assert analyzer.raw_df is None
    assert analyzer.processed_df is None
    assert not analyzer._is_processed

# Мокуємо компоненти, щоб перевірити пайплайн process_data
def test_process_data_pipeline(mocker, test_config):
    """Перевіряє, що process_data викликає компоненти у правильному порядку."""
    mock_load = mocker.patch('src.data_loader.DataLoader.load_data', return_value=pd.DataFrame({'Name': ['A']}))
    mock_clean = mocker.patch('src.data_cleaner.DataCleaner.clean_data', return_value=pd.DataFrame({'Name': ['A']}))
    mock_grade = mocker.patch('src.grade_calculator.GradeCalculator.calculate_national_scale', return_value=pd.DataFrame({'Name': ['A']}))
    mock_scholar = mocker.patch('src.scholarship.ScholarshipDeterminer.determine_scholarships', return_value=pd.DataFrame({'Name': ['A'], 'Scholarship': ['*']}))

    analyzer = DataAnalyzer(test_config)
    analyzer.process_data()

    mock_load.assert_called_once_with(test_config)
    mock_clean.assert_called_once()
    mock_grade.assert_called_once()
    mock_scholar.assert_called_once()
    assert analyzer._is_processed
    assert analyzer.processed_df is not None

def test_process_data_raises_on_component_error(mocker, test_config):
    """Перевіряє, що помилка компонента прокидається наверх."""
    mocker.patch('src.data_loader.DataLoader.load_data', side_effect=DataLoaderError("Load failed"))
    analyzer = DataAnalyzer(test_config)
    with pytest.raises(DataLoaderError, match="Load failed"):
        analyzer.process_data()
    assert not analyzer._is_processed

def test_get_overall_stats(analyzer_with_data, test_config):
    """Перевіряє розрахунок загальної статистики."""
    stats = analyzer_with_data.get_overall_stats()
    
    assert stats['total_students'] == 5
    # Найвищі GPA у Alice та David (95.0)
    assert stats['highest_gpa_student'] in ['Alice', 'David'] 
    assert stats['lowest_gpa_student'] == 'Eve' # GPA 65.0
    assert stats['scholarship_recipients_count'] == 3
    # (95+85+75+95+65)/5 = 415/5 = 83.0
    assert stats['average_gpa_overall'] == pytest.approx(83.0)

def test_get_overall_stats_before_processing(test_config):
    """Перевіряє помилку при виклику статистики до обробки."""
    analyzer = DataAnalyzer(test_config)
    with pytest.raises(RuntimeError, match="Data must be processed before getting statistics"):
        analyzer.get_overall_stats()

def test_get_group_stats_target_group(analyzer_with_data, test_config):
    """Перевіряє статистику для цільової групи з конфігурації (GroupA)."""
    stats = analyzer_with_data.get_group_stats() # Використовує config.target_group

    # Студенти в GroupA: Alice (95, *), Charlie (75, ''), Eve (65, '')
    assert stats['group_id'] == 'GroupA'
    assert stats['students_in_group'] == 3
    assert stats['highest_gpa_student_in_group'] == 'Alice'
    assert stats['lowest_gpa_student_in_group'] == 'Eve'
    assert stats['scholarship_recipients_in_group'] == 1 # Тільки Alice
    # (95 + 75 + 65) / 3 = 235 / 3 = 78.333...
    assert stats['average_gpa_in_group'] == pytest.approx(235 / 3)

def test_get_group_stats_specific_group(analyzer_with_data, test_config):
    """Перевіряє статистику для явно вказаної групи (GroupB)."""
    stats = analyzer_with_data.get_group_stats(group_id='GroupB')

    # Студенти в GroupB: Bob (85, *), David (95, *)
    assert stats['group_id'] == 'GroupB'
    assert stats['students_in_group'] == 2
    assert stats['highest_gpa_student_in_group'] == 'David'
    assert stats['lowest_gpa_student_in_group'] == 'Bob'
    assert stats['scholarship_recipients_in_group'] == 2 
    # (85 + 95) / 2 = 180 / 2 = 90.0
    assert stats['average_gpa_in_group'] == pytest.approx(90.0)

def test_get_group_stats_non_existent_group(analyzer_with_data, test_config):
    """Перевіряє помилку при запиті статистики для неіснуючої групи."""
    with pytest.raises(ValueError, match="Group 'GroupC' not found"):
        analyzer_with_data.get_group_stats(group_id='GroupC')

def test_find_student_by_name(analyzer_with_data, test_config):
    """Перевіряє пошук студента за іменем."""
    # Повний збіг
    result_alice = analyzer_with_data.find_student_by_name('Alice')
    assert isinstance(result_alice, pd.DataFrame)
    assert len(result_alice) == 1
    assert result_alice.iloc[0][test_config.name_column] == 'Alice'

    # Частковий збіг, інший регістр
    result_li = analyzer_with_data.find_student_by_name('li') # Alice, Charlie
    assert isinstance(result_li, pd.DataFrame)
    assert len(result_li) == 2
    assert 'Alice' in result_li[test_config.name_column].tolist()
    assert 'Charlie' in result_li[test_config.name_column].tolist()

    # Не знайдено
    result_none = analyzer_with_data.find_student_by_name('Zoe')
    assert result_none is None

def test_get_scholarship_students(analyzer_with_data, test_config):
    """Перевіряє отримання списку стипендіатів."""
    scholars_df = analyzer_with_data.get_scholarship_students()
    assert isinstance(scholars_df, pd.DataFrame)
    assert len(scholars_df) == 3
    expected_scholars = ['Alice', 'Bob', 'David']
    assert sorted(scholars_df[test_config.name_column].tolist()) == sorted(expected_scholars)
    
    # Перевірка, якщо немає стипендіатів
    analyzer_with_data.processed_df[test_config.scholarship_column] = ''
    no_scholars_df = analyzer_with_data.get_scholarship_students()
    assert no_scholars_df is None

def test_save_processed_data(mocker, analyzer_with_data, test_config):
    """Перевіряє виклик ReportSaver."""
    mock_save = mocker.patch('src.report_saver.ReportSaver.save_results')
    analyzer_with_data.save_processed_data()
    mock_save.assert_called_once_with(analyzer_with_data.processed_df, test_config)

def test_save_processed_data_before_processing(test_config):
    """Перевіряє помилку збереження до обробки."""
    analyzer = DataAnalyzer(test_config)
    with pytest.raises(RuntimeError, match="Data must be processed successfully before saving"):
        analyzer.save_processed_data()

def test_save_processed_data_saver_error(mocker, analyzer_with_data, test_config):
    """Перевіряє прокидання помилки від ReportSaver."""
    mocker.patch('src.report_saver.ReportSaver.save_results', side_effect=ReportSaverError("Cannot write"))
    with pytest.raises(ReportSaverError, match="Cannot write"):
        analyzer_with_data.save_processed_data()