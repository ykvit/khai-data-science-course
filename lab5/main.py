import logging
import pandas as pd
import matplotlib.pyplot as plt 
import sys 
import tkinter as tk 
from typing import Optional
from pathlib import Path
from matplotlib.figure import Figure
from tkinter import messagebox

# --- Налаштування логування (важливо зробити це ДО імпорту інших модулів src) ---
log_format = '%(asctime)s - [%(levelname)s] - %(name)s:%(lineno)d - %(message)s'
date_format = '%Y-%m-%d %H:%M:%S'

logging.basicConfig(level=logging.INFO, format=log_format, datefmt=date_format, stream=sys.stdout)

log_file_path = None 

try:
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        base_path = Path(sys._MEIPASS) # type: ignore
        log_dir_base = Path.cwd() 
    else:
        base_path = Path(__file__).parent
        log_dir_base = base_path 

    log_dir = log_dir_base / "output" 
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file_path = log_dir / "student_analysis_gui.log"


    file_handler = logging.FileHandler(log_file_path, mode='a', encoding='utf-8')
    file_handler.setFormatter(logging.Formatter(log_format, datefmt=date_format))
    file_handler.setLevel(logging.DEBUG) 

    logging.getLogger().addHandler(file_handler)
    # logging.getLogger().removeHandler(logging.getLogger().handlers[0])

    logging.info(f"File logging initialized. Base path: {base_path}. Log file: {log_file_path}")

except Exception as log_setup_err:
    logging.error(f"Failed to configure file logging: {log_setup_err}", exc_info=True)
    print(f"[ERROR] Failed to configure file logging to '{log_file_path}': {log_setup_err}", file=sys.stderr)


# --- Import and start GUI ---
try:
    src_path = Path(__file__).parent / 'src'
    if src_path.is_dir() and str(src_path.parent) not in sys.path:
         project_root = str(src_path.parent)
         if project_root not in sys.path:
              sys.path.insert(0, project_root)
              logging.info(f"Added project root to sys.path: {project_root}")

    from src.gui import run_gui 
    logging.info("GUI module imported successfully.")

except ImportError as import_err:
     logging.critical(f"Failed to import GUI module or its dependencies: {import_err}", exc_info=True)
     try:
         root_err = tk.Tk()
         root_err.withdraw()
         messagebox.showerror("Помилка Імпорту", f"Не вдалося завантажити компоненти додатку:\n{import_err}\n\nПеревірте цілісність програми та встановлені бібліотеки.\nДодаток не може продовжити роботу.")
         root_err.destroy()
     except Exception:
          print(f"[CRITICAL] Failed to import required application components: {import_err}", file=sys.stderr)
          print("Please ensure all dependencies are installed and the application structure is correct.", file=sys.stderr)
     sys.exit(1) 


def main():
    """
    Main gui
    """
    separator = "=" * 40
    logging.info(separator)
    logging.info("Starting Student Performance Analysis GUI Application")
    logging.info(separator)

    try:
        run_gui()
        logging.info("GUI main loop finished normally.")

    except Exception as gui_err:
         logging.critical(f"An unexpected critical error occurred in the GUI main loop: {gui_err}", exc_info=True)
         try:
             root_crit = tk.Tk()
             root_crit.withdraw()
             error_msg = f"Виникла неочікувана критична помилка:\n{gui_err}\n\n"
             if log_file_path:
                  error_msg += f"Будь ласка, перевірте лог-файл для деталей:\n{log_file_path}"
             else:
                  error_msg += "Файлове логування не було налаштовано. Перевірте консоль."
             messagebox.showerror("Критична Помилка Додатку", error_msg)
             root_crit.destroy()
         except Exception as tk_err:
              print(f"[CRITICAL] An unexpected error occurred in the GUI: {gui_err}", file=sys.stderr)
              print(f"[ERROR] Could not display error message box: {tk_err}", file=sys.stderr)
              if log_file_path:
                   print(f"Please check the log file for details: {log_file_path}", file=sys.stderr)

    logging.info(separator)
    logging.info("Application finished.")
    logging.info(separator)


if __name__ == "__main__":
    main()