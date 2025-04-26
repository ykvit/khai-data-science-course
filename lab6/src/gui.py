"""
Module for the graphical user interface (GUI)
for text plagiarism analysis using an LLM.
"""

import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import os

from .utils import load_text_from_file, clear_text_area
from .analysis import perform_analysis
from .exceptions import LLMConnectionError, LLMResponseError, LLMError 


class PlagiarismApp:
    """
    Main application class for the plagiarism analyzer.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Аналізатор Плагіату на базі LLM") # UI String
        self.root.minsize(700, 500)

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        # --- Frames for layout ---
        top_frame = tk.Frame(self.root)
        top_frame.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")
        top_frame.columnconfigure((0, 2), weight=1)
        top_frame.columnconfigure((1, 3), weight=0)

        middle_frame = tk.Frame(self.root)
        middle_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        middle_frame.columnconfigure(0, weight=1)
        middle_frame.columnconfigure(1, weight=1)
        middle_frame.rowconfigure(0, weight=1)

        bottom_frame = tk.Frame(self.root)
        bottom_frame.grid(row=2, column=0, padx=10, pady=(5, 10), sticky="ew")
        bottom_frame.columnconfigure(1, weight=1)

        # --- Widgets for Text 1 ---
        label1 = tk.Label(top_frame, text="Текст 1:") # UI String
        label1.grid(row=0, column=0, padx=(0, 5), sticky="w")
        self.load_button1 = tk.Button(
            top_frame, text="Завантажити файл 1", command=self.load_file1 # UI String
        )
        self.load_button1.grid(row=0, column=1, padx=5)
        self.clear_button1 = tk.Button(
            top_frame, text="Очистити 1", command=lambda: clear_text_area(self.text_area1) # UI String
        )
        self.clear_button1.grid(row=0, column=2, padx=(5, 20)) # Adjusted padding slightly
        self.text_area1 = scrolledtext.ScrolledText(middle_frame, wrap=tk.WORD, height=10, width=40)
        self.text_area1.grid(row=0, column=0, padx=(0, 5), pady=5, sticky="nsew")

        # --- Widgets for Text 2 ---
        label2 = tk.Label(top_frame, text="Текст 2:") # UI String
        label2.grid(row=1, column=0, padx=(0, 5), pady=(5,0), sticky="w")
        self.load_button2 = tk.Button(
            top_frame, text="Завантажити файл 2", command=self.load_file2 # UI String
        )
        self.load_button2.grid(row=1, column=1, padx=5, pady=(5,0))
        self.clear_button2 = tk.Button(
            top_frame, text="Очистити 2", command=lambda: clear_text_area(self.text_area2) # UI String
        )
        self.clear_button2.grid(row=1, column=2, padx=(5, 20), pady=(5,0)) # Adjusted padding slightly
        self.text_area2 = scrolledtext.ScrolledText(middle_frame, wrap=tk.WORD, height=10, width=40)
        self.text_area2.grid(row=0, column=1, padx=(5, 0), pady=5, sticky="nsew")

        # --- Widgets for Analysis and Results ---
        self.analyze_button = tk.Button(
            bottom_frame, text="Аналізувати на плагіат", command=self.analyze # UI String
        )
        self.analyze_button.grid(row=0, column=0, padx=(0,10), pady=(0, 5), sticky="w") # Added bottom padding

        self.result_label = tk.Label(bottom_frame, text="Результат аналізу:") # UI String
        self.result_label.grid(row=1, column=0, sticky="nw", pady=(5,0)) # Anchor north-west

        self.result_area = scrolledtext.ScrolledText(bottom_frame, wrap=tk.WORD, height=6, state=tk.DISABLED)
        self.result_area.grid(row=1, column=1, sticky="ew", pady=(5,0))


    def load_file_to_textarea(self, textarea):
        """Loads text from a selected file into the specified text area."""
        try:
            content = load_text_from_file()
            if content is not None:
                textarea.config(state=tk.NORMAL)
                textarea.delete('1.0', tk.END)
                textarea.insert('1.0', content)
        except Exception as e:
             messagebox.showerror("Помилка читання файлу", f"Не вдалося прочитати файл:\n{e}") # UI String


    def load_file1(self):
        """Handler for the 'Load File 1' button."""
        self.load_file_to_textarea(self.text_area1)

    def load_file2(self):
        """Handler for the 'Load File 2' button."""
        self.load_file_to_textarea(self.text_area2)

    def display_result(self, result_text):
        """Displays the analysis result (as plain text) in the result_area."""
        self.result_area.config(state=tk.NORMAL) # Enable writing
        self.result_area.delete('1.0', tk.END)
        self.result_area.insert('1.0', result_text) # Insert the raw text
        self.result_area.config(state=tk.DISABLED) # Disable writing

    def analyze(self):
        """Performs plagiarism analysis on the texts in the text areas."""
        text1 = self.text_area1.get('1.0', tk.END).strip()
        text2 = self.text_area2.get('1.0', tk.END).strip()

        if not text1 or not text2:
            messagebox.showwarning("Немає даних", "Будь ласка, введіть або завантажте обидва тексти.") # UI String
            return

        self.analyze_button.config(state=tk.DISABLED, text="Аналіз...") # UI String
        self.display_result("Обробка запиту...") # UI String: "Processing request..."
        self.root.update_idletasks()

        try:
            result = perform_analysis(text1, text2)
            self.display_result(result)

        except (LLMConnectionError, LLMResponseError) as e:
            error_msg = f"Не вдалося виконати аналіз:\n{e}" # UI String
            messagebox.showerror("Помилка LLM", error_msg) # UI String
            self.display_result(f"Помилка: {e}")
        except ValueError as e:
            messagebox.showwarning("Невірні дані", str(e)) # UI String
            self.display_result("")
        except Exception as e:
            error_msg = f"Сталася неочікувана помилка: {e}" # UI String
            messagebox.showerror("Неочікувана помилка", error_msg) # UI String
            self.display_result(f"Неочікувана помилка: {e}")
            print(f"Unexpected error during analysis: {e}")
        finally:
            self.analyze_button.config(state=tk.NORMAL, text="Аналізувати на плагіат") # UI String


# Keep the main block for potential separate testing of the GUI module
if __name__ == '__main__':
    print("Running GUI module directly for testing...")
    root = tk.Tk()
    app = PlagiarismApp(root)
    root.mainloop()