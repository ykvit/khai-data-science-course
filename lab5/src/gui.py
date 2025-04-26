import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import logging
from pathlib import Path
import pandas as pd
from typing import Optional

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.pyplot as plt 

from .config import AppConfig
from .analysis import DataAnalyzer, DataLoaderError
from . import plotting 
from . import pdf_reporter

class StudentAnalysisGUI:
    """
    A graphical interface for analysing student performance.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Аналіз Успішності Студентів")
        self.root.geometry("800x700")

        # --- Uploading and processing data ---
        self.analyzer = None
        self.config = None
        try:
            logging.info("GUI: Initializing configuration and analyzer...")
            self.config = AppConfig()
            if not hasattr(self.config, 'output_dir'):
                 logging.error("CRITICAL: AppConfig loaded, but 'output_dir' attribute is missing!")
                 raise AttributeError("'AppConfig' object correctly initialized but missing 'output_dir'. Check config.py definition.")

            self.analyzer = DataAnalyzer(self.config)
            logging.info("GUI: Processing data...")
            self.root.update_idletasks() 
            self.status_label = ttk.Label(root, text="Завантаження та обробка даних...")
            self.status_label.pack(pady=5)
            self.root.update_idletasks()
            self.analyzer.process_data() # Uploading and processing data
            self.status_label.config(text="Дані успішно завантажено та оброблено.")
            logging.info("GUI: Data processing complete.")
        except (DataLoaderError, KeyError, ValueError, RuntimeError, FileNotFoundError, AttributeError) as e: # Додано AttributeError
            logging.error(f"GUI: Critical error during data loading/processing: {e}", exc_info=True)
            messagebox.showerror("Помилка Завантаження Даних", f"Не вдалося завантажити або обробити дані:\n{e}\n\nПеревірте файл '{getattr(self.config, 'input_file', 'N/A')}' та конфігурацію.\nДодаток буде закрито.")
            self.root.quit() 
            return 
        except Exception as e:
             logging.critical(f"GUI: Unexpected critical error during initialization: {e}", exc_info=True)
             messagebox.showerror("Критична Помилка", f"Виникла неочікувана помилка під час ініціалізації:\n{e}\n\nДодаток буде закрито.")
             self.root.quit()
             return

        # self.status_label.pack_forget()
        self.status_label.config(text=f"Файл: {Path(self.config.input_file).name} | Група за замовчуванням: {self.config.target_group}")


        # --- Create widgets ---
        logging.info("GUI: Creating widgets...")
        self._create_widgets()
        logging.info("GUI: Initialization complete.")


    def _create_widgets(self):
        """Creates all interface elements."""

        # --- Style for widgets ---
        style = ttk.Style()
        style.configure('TButton', padding=6, relief="flat", font=('Helvetica', 10))
        style.configure('TLabel', padding=2, font=('Helvetica', 10))
        style.configure('TEntry', padding=4, font=('Helvetica', 10))
        style.configure('TLabelframe.Label', font=('Helvetica', 11, 'bold'))

        # --- Main frame ---
        main_frame = ttk.Frame(self.root, padding="10 10 10 10")
        main_frame.pack(expand=True, fill=tk.BOTH)

        # --- Frame for controls (left side) ---
        control_frame = ttk.Frame(main_frame, width=300)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        control_frame.pack_propagate(False) 

        # --- Output frame (right side) ---
        output_frame = ttk.Frame(main_frame)
        output_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

        # === Controls (left panel) ===

        # --- Search for a student ---
        student_search_frame = ttk.LabelFrame(control_frame, text="Пошук Студента")
        student_search_frame.pack(pady=10, padx=5, fill=tk.X)

        ttk.Label(student_search_frame, text="ПІБ (або частина):").pack(anchor=tk.W, padx=5)
        self.student_name_entry = ttk.Entry(student_search_frame, width=30)
        self.student_name_entry.pack(pady=5, padx=5, fill=tk.X)
        self.student_search_button = ttk.Button(student_search_frame, text="Знайти та Показати Оцінки", command=self._search_student_and_show_bar)
        self.student_search_button.pack(pady=5, padx=5)

        # --- Group analysis ---
        group_analysis_frame = ttk.LabelFrame(control_frame, text="Аналіз Групи")
        group_analysis_frame.pack(pady=10, padx=5, fill=tk.X)

        ttk.Label(group_analysis_frame, text="ID Групи:").pack(anchor=tk.W, padx=5)
        self.group_id_entry = ttk.Entry(group_analysis_frame, width=30)

        self.group_id_entry.insert(0, self.config.target_group if self.config else "")
        self.group_id_entry.pack(pady=5, padx=5, fill=tk.X)

        group_buttons_frame = ttk.Frame(group_analysis_frame) 
        group_buttons_frame.pack(pady=5)

        self.group_info_button = ttk.Button(group_buttons_frame, text="Інфо про Групу", command=self._show_group_info)
        self.group_info_button.grid(row=0, column=0, padx=3, pady=3)

        self.group_pie_button = ttk.Button(group_buttons_frame, text="Діаграма Успішності", command=self._show_group_pie_chart)
        self.group_pie_button.grid(row=0, column=1, padx=3, pady=3)

        self.group_pdf_button = ttk.Button(group_buttons_frame, text="Згенерувати PDF Звіт", command=self._generate_group_pdf)
        self.group_pdf_button.grid(row=1, column=0, columnspan=2, padx=3, pady=3)


        # --- General actions ---
        general_actions_frame = ttk.LabelFrame(control_frame, text="Загальні Дії")
        general_actions_frame.pack(pady=10, padx=5, fill=tk.X)

        self.all_scholars_button = ttk.Button(general_actions_frame, text="Показати Всіх Стипендіатів", command=self._show_all_scholars)
        self.all_scholars_button.pack(pady=5, padx=5)

        # --- Exit button ---
        self.quit_button = ttk.Button(control_frame, text="Вихід", command=self.root.quit)
        self.quit_button.pack(side=tk.BOTTOM, pady=20)

        # === Output area (right panel) ===

        # --- Text output ---
        results_frame = ttk.LabelFrame(output_frame, text="Результати")
        results_frame.pack(pady=5, padx=5, fill=tk.X)

        self.results_text = scrolledtext.ScrolledText(results_frame, height=12, width=60, wrap=tk.WORD, state=tk.DISABLED, font=('Courier New', 9))
        self.results_text.pack(expand=True, fill=tk.BOTH, pady=5, padx=5)

        # --- Area for Matplotlib graphs ---
        self.plot_frame = ttk.LabelFrame(output_frame, text="Графік")
        self.plot_frame.pack(pady=10, padx=5, expand=True, fill=tk.BOTH)
        self.plot_placeholder_label = ttk.Label(self.plot_frame, text="Тут буде відображено графік", style='TLabel', foreground='grey')
        self.plot_placeholder_label.pack(expand=True)

        self.current_plot_canvas = None
        self.current_plot_toolbar = None


    # === Auxiliary methods===

    def _clear_results(self):
        """Clears the results text field."""
        self.results_text.config(state=tk.NORMAL) # Дозволити редагування
        self.results_text.delete('1.0', tk.END)
        self.results_text.config(state=tk.DISABLED) # Знову заборонити

    def _append_results(self, text):
        """Adds text to the results text field."""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.insert(tk.END, text + "\n")
        self.results_text.config(state=tk.DISABLED)
        self.results_text.see(tk.END) # Прокрутити до кінця

    def _clear_plot_area(self):
        """Removes the current graph and its toolbar from the plot_frame."""
        if self.current_plot_toolbar:
            self.current_plot_toolbar.pack_forget()
            self.current_plot_toolbar = None
        if self.current_plot_canvas:
            self.current_plot_canvas.get_tk_widget().pack_forget()
            self.current_plot_canvas = None
        if not self.plot_placeholder_label.winfo_ismapped():
            self.plot_placeholder_label.pack(expand=True)

    def _display_plot(self, fig: Optional[Figure]): # Optional use
        """Displays the Matplotlib figure in the plot_frame."""
        self._clear_plot_area() 

        if fig is None:
            logging.warning("GUI: Cannot display plot, figure is None.")
            self.plot_placeholder_label.config(text="Не вдалося побудувати графік")
            if not self.plot_placeholder_label.winfo_ismapped():
                 self.plot_placeholder_label.pack(expand=True)
            return

        self.plot_placeholder_label.pack_forget()

        try:
            # Create Canvas
            canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
            canvas.draw()

            toolbar = NavigationToolbar2Tk(canvas, self.plot_frame, pack_toolbar=False)
            toolbar.update()

            toolbar.pack(side=tk.BOTTOM, fill=tk.X)
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

            self.current_plot_canvas = canvas
            self.current_plot_toolbar = toolbar
            logging.info("GUI: Plot displayed successfully.")

        except Exception as e:
            logging.error(f"GUI: Error displaying plot: {e}", exc_info=True)
            messagebox.showerror("Помилка Відображення Графіка", f"Не вдалося відобразити графік:\n{e}")
            self._clear_plot_area() # Спробувати очистити у разі помилки
            self.plot_placeholder_label.config(text="Помилка відображення графіка")
            self.plot_placeholder_label.pack(expand=True) # Показати текст помилки

        finally:
            # Close the Matplotlib figure to free up memory,
            # since it has already been drawn in Canvas
            # Check that fig is really a Figure object before closing
            if isinstance(fig, Figure):
                plt.close(fig)


    # === Event handlers for buttons ===

    def _search_student_and_show_bar(self):
        """Searches for a student and displays their bar chart."""
        student_name = self.student_name_entry.get().strip()
        if not student_name:
            messagebox.showwarning("Пошук Студента", "Будь ласка, введіть ПІБ або частину ПІБ студента.")
            return

        self._clear_results()
        self._clear_plot_area()
        logging.info(f"GUI: Searching for student: '{student_name}'")

        try:
            found_students_df = self.analyzer.find_student_by_name(student_name)

            if found_students_df is None or found_students_df.empty:
                self._append_results(f"Студентів, що містять '{student_name}', не знайдено.")
                logging.info("GUI: Student not found.")
                self.plot_placeholder_label.config(text=f"Студента '{student_name}' не знайдено")
                if not self.plot_placeholder_label.winfo_ismapped():
                    self.plot_placeholder_label.pack(expand=True)

            else:
                num_found = len(found_students_df)
                self._append_results(f"Знайдено {num_found} студент(ів), що містять '{student_name}':")

                for index, student_data in found_students_df.iterrows():
                    self._append_results("-" * 30)
                    name = student_data.get(self.config.name_column, "N/A")
                    group = student_data.get(self.config.group_column, "N/A")
                    gpa = student_data.get(self.config.gpa_column)
                    gpa_str = f"{gpa:.2f}" if pd.notna(gpa) else "N/A"
                    scholarship = student_data.get(self.config.scholarship_column, "") == self.config.scholarship_marker
                    scholarship_str = "Так" if scholarship else "Ні"

                    self._append_results(f"  ПІБ: {name}")
                    self._append_results(f"  Група: {group}")
                    self._append_results(f"  GPA: {gpa_str}")
                    self._append_results(f"  Стипендія: {scholarship_str}")
                    # Add grade
                    self._append_results("  Оцінки:")
                    for subj_col in self.config.subject_score_columns:
                        score = student_data.get(subj_col)
                        score_str = f"{score:.0f}" if pd.notna(score) else "N/A"
                        subj_name = self.config.get_national_scale_column_name(subj_col).replace(self.config.national_scale_suffix, '') # Використаємо метод з конфіга для очищення
                        self._append_results(f"    {subj_name}: {score_str}")

                first_student_data = found_students_df.iloc[0]
                logging.info(f"GUI: Creating bar chart for {first_student_data.get(self.config.name_column, 'N/A')}")

                student_fig = plotting.create_student_scores_bar(first_student_data, self.config)
                self._display_plot(student_fig)

        except RuntimeError as e:
             logging.error(f"GUI: Runtime error during student search: {e}")
             messagebox.showerror("Помилка", f"Помилка під час пошуку: {e}")
        except Exception as e:
             logging.error(f"GUI: Unexpected error during student search: {e}", exc_info=True)
             messagebox.showerror("Неочікувана Помилка", f"Виникла помилка: {e}")


    def _show_group_info(self):
        """Displays statistics for the entered group."""
        group_id = self.group_id_entry.get().strip()
        if not group_id:
            messagebox.showwarning("Аналіз Групи", "Будь ласка, введіть ID групи.")
            return

        self._clear_results()
        self._clear_plot_area()
        logging.info(f"GUI: Getting info for group: '{group_id}'")
        self.plot_placeholder_label.config(text=f"Інформація про групу '{group_id}'") 
        if not self.plot_placeholder_label.winfo_ismapped():
            self.plot_placeholder_label.pack(expand=True)


        try:
            group_stats = self.analyzer.get_group_stats(group_id)

            self._append_results(f"--- Статистика для Групи: {group_id} ---")
            self._append_results(f"Кількість студентів: {group_stats.get('students_in_group', 'N/A')}")
            self._append_results(f"Кількість стипендіатів: {group_stats.get('scholarship_recipients_in_group', 'N/A')}")

            avg_gpa = group_stats.get('average_gpa_in_group')
            avg_gpa_str = f"{avg_gpa:.2f}" if avg_gpa is not None and pd.notna(avg_gpa) else "N/A" 
            self._append_results(f"Середній GPA: {avg_gpa_str}")

            self._append_results(f"Найвищий GPA: {group_stats.get('highest_gpa_student_in_group', 'N/A')}")
            self._append_results(f"Найнижчий GPA: {group_stats.get('lowest_gpa_student_in_group', 'N/A')}")
            logging.info(f"GUI: Displayed info for group {group_id}")

        except ValueError as e: #
            logging.warning(f"GUI: Group '{group_id}' not found.")
            self._append_results(f"Помилка: {e}")
            self.plot_placeholder_label.config(text=f"Групу '{group_id}' не знайдено")
        except RuntimeError as e:
             logging.error(f"GUI: Runtime error getting group info: {e}")
             messagebox.showerror("Помилка", f"Помилка отримання даних групи: {e}")
        except Exception as e:
             logging.error(f"GUI: Unexpected error getting group info: {e}", exc_info=True)
             messagebox.showerror("Неочікувана Помилка", f"Виникла помилка: {e}")


    def _show_all_scholars(self):
        """Displays a list of all students who receive a scholarship."""
        self._clear_results()
        self._clear_plot_area()
        logging.info("GUI: Getting list of all scholars.")
        self.plot_placeholder_label.config(text="Список усіх стипендіатів")
        if not self.plot_placeholder_label.winfo_ismapped():
             self.plot_placeholder_label.pack(expand=True)

        try:
            scholars_df = self.analyzer.get_scholarship_students()

            if scholars_df is None or scholars_df.empty:
                self._append_results("Студентів, що отримують стипендію, не знайдено.")
                logging.info("GUI: No scholars found.")
            else:
                self._append_results("--- Список Студентів зі Стипендією ---")
                names = sorted(scholars_df[self.config.name_column].tolist())
                for i, name in enumerate(names, 1):
                    self._append_results(f"{i}. {name}")
                self._append_results(f"\nЗагальна кількість стипендіатів: {len(names)}")
                logging.info(f"GUI: Displayed {len(names)} scholars.")

        except RuntimeError as e:
             logging.error(f"GUI: Runtime error getting scholars list: {e}")
             messagebox.showerror("Помилка", f"Помилка отримання списку стипендіатів: {e}")
        except Exception as e:
             logging.error(f"GUI: Unexpected error getting scholars list: {e}", exc_info=True)
             messagebox.showerror("Неочікувана Помилка", f"Виникла помилка: {e}")


    def _show_group_pie_chart(self):
        """Displays a pie chart of the success rate for the entered group."""
        group_id = self.group_id_entry.get().strip()
        if not group_id:
            messagebox.showwarning("Аналіз Групи", "Будь ласка, введіть ID групи.")
            return

        self._clear_results()
        logging.info(f"GUI: Creating pie chart for group: '{group_id}'")

        try:
            group_df = self.analyzer.get_group_data(group_id)

            if group_df is None or group_df.empty:
                messagebox.showerror("Помилка", f"Групу '{group_id}' не знайдено або вона порожня.")
                self._clear_plot_area()
                self.plot_placeholder_label.config(text=f"Групу '{group_id}' не знайдено")
                if not self.plot_placeholder_label.winfo_ismapped():
                    self.plot_placeholder_label.pack(expand=True)
                return

            group_fig = plotting.create_group_performance_pie(group_df, group_id, self.config)
            self._display_plot(group_fig) 
        except RuntimeError as e:
             logging.error(f"GUI: Runtime error creating group pie chart: {e}")
             messagebox.showerror("Помилка", f"Помилка створення діаграми: {e}")
             self._clear_plot_area()
        except Exception as e:
             logging.error(f"GUI: Unexpected error creating group pie chart: {e}", exc_info=True)
             messagebox.showerror("Неочікувана Помилка", f"Виникла помилка: {e}")
             self._clear_plot_area()


    def _generate_group_pdf(self):
        """Generates a PDF report for the group and offers to save it."""
        group_id = self.group_id_entry.get().strip()
        if not group_id:
            messagebox.showwarning("Аналіз Групи", "Будь ласка, введіть ID групи для генерації звіту.")
            return

        logging.info(f"GUI: Starting PDF report generation for group: '{group_id}'")
        self._clear_results() 

        try:
            if not hasattr(self.config, 'output_dir') or not self.config.output_dir:
                 logging.error("Cannot generate PDF: config.output_dir is not set.")
                 messagebox.showerror("Помилка Конфігурації", "Шлях для збереження звітів не визначено в конфігурації.")
                 return

            group_df = self.analyzer.get_group_data(group_id)
            if group_df is None or group_df.empty:
                messagebox.showerror("Помилка", f"Групу '{group_id}' не знайдено або вона порожня. Неможливо створити звіт.")
                return

            group_stats = self.analyzer.get_group_stats(group_id)

            default_filename = f"group_{group_id}_report.pdf"
            # self.config.output_dir, 
            output_dir = self.config.output_dir
            output_dir.mkdir(parents=True, exist_ok=True) 
            filepath = filedialog.asksaveasfilename(
                initialdir=str(output_dir), 
                initialfile=default_filename,
                defaultextension=".pdf",
                filetypes=[("PDF Documents", "*.pdf"), ("All Files", "*.*")]
            )

            if not filepath:
                logging.info("GUI: PDF generation cancelled by user.")
                self._append_results("Генерацію PDF звіту скасовано.")
                return

            self._append_results(f"Генерація PDF звіту для групи {group_id} до файлу:\n{filepath}...")
            self.root.update_idletasks() 

            success = pdf_reporter.generate_group_report_pdf(
                group_df=group_df,
                group_stats=group_stats,
                group_id=group_id,
                config=self.config,
                output_filepath=filepath 
            )

            if success:
                logging.info(f"GUI: PDF report generated successfully: {filepath}")
                messagebox.showinfo("PDF Звіт Згенеровано", f"Звіт для групи {group_id} успішно збережено як:\n{filepath}")
                self._append_results(f"PDF звіт успішно збережено:\n{filepath}")
            else:
                logging.error(f"GUI: Failed to generate PDF report for group {group_id}.")
                messagebox.showerror("Помилка Генерації PDF", f"Не вдалося згенерувати PDF звіт для групи {group_id}.\nПеревірте лог-файл для деталей.")
                self._append_results(f"Помилка генерації PDF звіту для групи {group_id}.")

        except ValueError as e: 
             logging.warning(f"GUI: Error getting stats for PDF report: {e}")
             messagebox.showerror("Помилка Даних", f"Помилка отримання даних для звіту: {e}")
        except AttributeError as e: 
             logging.error(f"GUI: Configuration error during PDF generation: {e}", exc_info=True)
             messagebox.showerror("Помилка Конфігурації", f"Помилка доступу до налаштувань:\n{e}\n\nПеревірте файл config.py.")
        except RuntimeError as e:
             logging.error(f"GUI: Runtime error during PDF generation: {e}")
             messagebox.showerror("Помилка", f"Помилка під час генерації PDF: {e}")
        except Exception as e:
             logging.error(f"GUI: Unexpected error during PDF generation: {e}", exc_info=True)
             messagebox.showerror("Неочікувана Помилка", f"Виникла помилка: {e}")


def run_gui():
    """Initializes and runs the Tkinter main loop."""
    root = tk.Tk()
    app = StudentAnalysisGUI(root) 
    if hasattr(app, 'analyzer') and app.analyzer: 
        root.mainloop()
    else:
        logging.info("GUI: Exiting due to initialization failure.")
        if root.winfo_exists():
             root.destroy()


if __name__ == '__main__':
    _log_format = '%(asctime)s - [%(levelname)s] - %(name)s:%(lineno)d - %(message)s'
    _date_format = '%Y-%m-%d %H:%M:%S'
    logging.basicConfig(level=logging.INFO, format=_log_format, datefmt=_date_format)
    try:
        _log_dir = Path(__file__).parent.parent / "output" 
        _log_dir.mkdir(parents=True, exist_ok=True)
        _log_file_path = _log_dir / "student_analysis_gui_direct.log"
        _file_handler = logging.FileHandler(_log_file_path, mode='a', encoding='utf-8')
        _file_handler.setFormatter(logging.Formatter(_log_format, datefmt=_date_format))
        _file_handler.setLevel(logging.DEBUG)
        logging.getLogger().addHandler(_file_handler)
        logging.info(f"GUI Direct Run: File logging initialized: {_log_file_path}")
    except Exception as _log_err:
         logging.error(f"GUI Direct Run: Failed to set up file logging: {_log_err}")

    logging.warning("Running gui.py directly. Relative imports might fail if not executed as a module.")
    _parent_dir = str(Path(__file__).parent.parent)
    if _parent_dir not in sys.path:
         sys.path.insert(0, _parent_dir)
         logging.info(f"GUI Direct Run: Added {_parent_dir} to sys.path")

    run_gui()