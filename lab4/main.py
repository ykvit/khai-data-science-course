# main.py
import logging
from src.config import AppConfig
from src.analysis import DataAnalyzer
from src.data_loader import DataLoaderError # Import from data_loader.py
from src.report_saver import ReportSaverError # Import from report_saver.py

# --- Configuration ---
# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(module)s - %(message)s')

# --- Main Execution ---
def main():
    """Main function to run the student performance analysis."""
    logging.info("Starting Student Performance Analysis Application")
    
    try:
        # 1. Initialize Configuration (Can be loaded from file/env vars later)
        config = AppConfig() 
        # !!! ВАЖЛИВО: Переконайся, що AppConfig має правильні назви колонок 
        #            та `target_group` встановлено для твоєї групи !!!
        logging.info(f"Configuration loaded: Input='{config.input_file}', Output='{config.output_file}', Target Group='{config.target_group}'")

        # 2. Initialize Analyzer
        analyzer = DataAnalyzer(config)
        
        # 3. Process Data
        analyzer.process_data() # This orchestrates load, clean, calculate, scholarhips
        
        # 4. Get Overall Statistics (Optional, but good for overview)
        overall_stats = analyzer.get_overall_stats()
        logging.info("\n--- Overall Statistics ---")
        logging.info(f"Total students processed: {overall_stats.get('total_students')}")
        logging.info(f"Highest GPA student (overall): {overall_stats.get('highest_gpa_student')}")
        logging.info(f"Lowest GPA student (overall): {overall_stats.get('lowest_gpa_student')}")
        logging.info(f"Total scholarship recipients: {overall_stats.get('scholarship_recipients_count')}")
        logging.info(f"Average GPA (overall): {overall_stats.get('average_gpa_overall', 'N/A'):.2f}")


        # 5. Get Statistics for the Target Group (as required by LW3 task)
        logging.info(f"\n--- Statistics for Target Group: {config.target_group} ---")
        try:
             group_stats = analyzer.get_group_stats() # Uses config.target_group by default
             logging.info(f"Number of students in group: {group_stats.get('students_in_group')}")
             logging.info(f"Highest GPA student in group: {group_stats.get('highest_gpa_student_in_group')}")
             logging.info(f"Lowest GPA student in group: {group_stats.get('lowest_gpa_student_in_group')}")
             logging.info(f"Number of scholarship recipients in group: {group_stats.get('scholarship_recipients_in_group')}")
             logging.info(f"Average GPA in group: {group_stats.get('average_gpa_in_group', 'N/A'):.2f}")
             
             # --- Вивід для звіту з лабораторної роботи ---
             print("\n--- Результати для звіту (Група: {config.target_group}) ---")
             print(f"ПІБ студента з найвищим балом: {group_stats.get('highest_gpa_student_in_group', 'Не знайдено')}")
             print(f"ПІБ студента з найнижчим балом: {group_stats.get('lowest_gpa_student_in_group', 'Не знайдено')}")
             print(f"Кількість студентів, що отримують стипендію: {group_stats.get('scholarship_recipients_in_group', 0)}")
             
        except ValueError as e:
             logging.error(f"Could not get stats for group '{config.target_group}': {e}")
             print(f"\nПомилка: Не вдалося отримати статистику для групи '{config.target_group}'. Перевірте наявність групи у файлі.")


        # 6. Save Processed Data
        analyzer.save_processed_data()
        
        logging.info("\nAnalysis finished successfully.")
        
    # Catch specific errors from our components first
    except (DataLoaderError, ReportSaverError, KeyError, ValueError, RuntimeError) as e:
         logging.error(f"An application error occurred: {e}", exc_info=True) # Log traceback for debug
         print(f"\nПомилка виконання: {e}")
         print("Будь ласка, перевірте конфігурацію (src/config.py), вхідний файл та права доступу.")
    except FileNotFoundError as e:
         logging.error(f"A required file was not found: {e}", exc_info=True)
         print(f"\nПомилка: Не знайдено файл '{e.filename}'. Перевірте шлях у конфігурації.")
    except Exception as e:
        # Catch-all for unexpected errors
        logging.critical(f"An unexpected critical error occurred: {e}", exc_info=True)
        print(f"\nКритична непередбачена помилка: {e}")
        print("Роботу програми буде перервано.")

if __name__ == "__main__":
    main()