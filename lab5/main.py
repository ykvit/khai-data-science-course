import logging
from pathlib import Path

from src.config import AppConfig
from src.analysis import DataAnalyzer
from src.cli import run_cli # Import the CLI runner function
from src.data_loader import DataLoaderError
from src.report_saver import ReportSaverError


log_format = '%(asctime)s - [%(levelname)s] - %(module)s:%(lineno)d - %(message)s'
date_format = '%Y-%m-%d %H:%M:%S'

logging.basicConfig(level=logging.INFO, format=log_format, datefmt=date_format)

try:
    log_dir = Path("output")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file_path = log_dir / "student_analysis.log"

    # Create a file handler that logs even DEBUG messages
    file_handler = logging.FileHandler(log_file_path, mode='a', encoding='utf-8') # 'a' for append mode
    file_handler.setFormatter(logging.Formatter(log_format, datefmt=date_format))
    file_handler.setLevel(logging.DEBUG) # Log more detailed info to the file

    # Add the file handler to the root logger
    logging.getLogger().addHandler(file_handler)
    logging.info(f"File logging initialized. Logs will be saved to: {log_file_path}")
except Exception as log_setup_err:
    logging.error(f"Failed to configure file logging: {log_setup_err}", exc_info=True)


def main():
    """
    Main function to initialize the data analyzer, process data,
    and run the command-line interface (CLI).
    """
    # Log the start of the application run
    separator = "=" * 40
    logging.info(separator)
    logging.info("Starting Student Performance Analysis Application")
    logging.info(separator)

    analyzer = None 

    try:
        config = AppConfig()
        # Log key configuration details (avoid logging sensitive data if applicable)
        logging.info(f"Configuration loaded: Input='{config.input_file}', Output Dir='output', Target Group='{config.target_group}'")

        Path("output").mkdir(parents=True, exist_ok=True)
        logging.debug("Output directory checked/created.")

        analyzer = DataAnalyzer(config)
        logging.info("DataAnalyzer initialized successfully.")

        print("Processing student data... Please wait.") # Provide feedback to the user
        logging.info("Starting data processing pipeline...")
        analyzer.process_data() # Orchestrates the core data handling steps
        print("Data processing complete.") # Inform user upon completion
        logging.info("Data processing pipeline finished successfully.")

    except (DataLoaderError, KeyError, ValueError, RuntimeError, FileNotFoundError) as setup_err:
         logging.error(f"A critical error occurred during setup or data processing: {setup_err}", exc_info=True)
         print(f"\nCRITICAL ERROR: {setup_err}")
         print("The application cannot continue. Please check the log file ('output/student_analysis.log') for details.")
         return # Exit the application gracefully

    # Catch any other unexpected exceptions during setup
    except Exception as unexpected_setup_err:
        logging.critical(f"An unexpected critical error occurred during setup: {unexpected_setup_err}", exc_info=True)
        print(f"\nCRITICAL UNEXPECTED ERROR: {unexpected_setup_err}")
        print("The application cannot continue. Please check the log file ('output/student_analysis.log') for details.")
        return # Exit the application gracefully

    if analyzer and analyzer._is_processed:
        logging.info("Starting Command Line Interface (CLI)...")
        try:
            # Pass the ready analyzer instance to the CLI function
            run_cli(analyzer)
            logging.info("CLI finished normally.")
        except KeyboardInterrupt:
            print("\nExiting application due to user interruption (Ctrl+C).")
            logging.warning("CLI terminated by user (KeyboardInterrupt).")
        except Exception as cli_err:
            # Catch unexpected errors specifically occurring within the CLI loop
            logging.critical(f"An unexpected error occurred within the CLI: {cli_err}", exc_info=True)
            print(f"\nA critical error occurred while running the interface: {cli_err}")
            print("Exiting application. Please check the log file ('output/student_analysis.log') for details.")
    else:
         # This case should ideally be prevented by the error handling above,
         # but serves as a final safety check.
         logging.error("Analyzer was not ready or data processing failed. CLI cannot start.")
         print("Failed to initialize or process data correctly. The command-line interface cannot be started.")

    logging.info(separator)
    logging.info("Application finished.")
    logging.info(separator)

if __name__ == "__main__":
    main()