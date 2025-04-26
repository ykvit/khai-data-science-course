"""
Module for the graphical user interface (GUI)
for text plagiarism analysis using an LLM.
"""

import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import os

# Import utility functions
from .utils import load_text_from_file, clear_text_area
from .analysis import perform_analysis
from .exceptions import LLMConnectionError, LLMResponseError, LLMError # Import custom exceptions


class PlagiarismApp:
    """
    Main application class for the plagiarism analyzer.
    Uses a 3-column grid layout.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Аналізатор Плагіату на базі LLM") # UI String
        self.root.minsize(800, 500) # Adjusted min size for 3 columns

        # --- Configure Root Window Grid ---
        # 3 columns, equal weight for horizontal expansion
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.columnconfigure(2, weight=1)
        # Row 1 (Text Areas) gets weight for vertical expansion
        self.root.rowconfigure(1, weight=1)
        # Rows 0 (Labels) and 2 (Buttons) have no weight

        # --- Widgets Column 1: Text 1 ---
        label1 = tk.Label(self.root, text="Текст 1:") # UI String
        label1.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")

        self.text_area1 = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, height=10, width=30)
        self.text_area1.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

        # Frame to hold buttons for column 1
        button_frame1 = tk.Frame(self.root)
        button_frame1.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="ew")
        self.load_button1 = tk.Button(
            button_frame1, text="Завантажити файл 1", command=self.load_file1 # UI String
        )
        self.load_button1.pack(side=tk.LEFT, padx=(0, 5)) # Pack buttons horizontally inside the frame
        self.clear_button1 = tk.Button(
            button_frame1, text="Очистити 1", command=lambda: clear_text_area(self.text_area1) # UI String
        )
        self.clear_button1.pack(side=tk.LEFT)

        # --- Widgets Column 2: Text 2 ---
        label2 = tk.Label(self.root, text="Текст 2:") # UI String
        label2.grid(row=0, column=1, padx=10, pady=(10, 0), sticky="w")

        self.text_area2 = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, height=10, width=30)
        self.text_area2.grid(row=1, column=1, padx=10, pady=5, sticky="nsew")

        # Frame to hold buttons for column 2
        button_frame2 = tk.Frame(self.root)
        button_frame2.grid(row=2, column=1, padx=10, pady=(0, 10), sticky="ew")
        self.load_button2 = tk.Button(
            button_frame2, text="Завантажити файл 2", command=self.load_file2 # UI String
        )
        self.load_button2.pack(side=tk.LEFT, padx=(0, 5))
        self.clear_button2 = tk.Button(
            button_frame2, text="Очистити 2", command=lambda: clear_text_area(self.text_area2) # UI String
        )
        self.clear_button2.pack(side=tk.LEFT)

        # --- Widgets Column 3: Result ---
        self.result_label = tk.Label(self.root, text="Результат аналізу:") # UI String
        self.result_label.grid(row=0, column=2, padx=10, pady=(10, 0), sticky="w")

        self.result_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, height=10, width=30, state=tk.DISABLED)
        self.result_area.grid(row=1, column=2, padx=10, pady=5, sticky="nsew")

        # Frame to hold button for column 3 (consistency)
        button_frame3 = tk.Frame(self.root)
        button_frame3.grid(row=2, column=2, padx=10, pady=(0, 10), sticky="ew")
        # Center the analyze button within its frame/column
        button_frame3.columnconfigure(0, weight=1) # Allow button to center if packed without expand=True
        self.analyze_button = tk.Button(
            button_frame3, text="Аналізувати на плагіат", command=self.analyze # UI String
        )
        self.analyze_button.pack(pady=(0,0)) # Pack button inside the frame

    def load_file_to_textarea(self, textarea):
        """Loads text from a selected file into the specified text area."""
        try:
            content = load_text_from_file()
            if content is not None:
                # Make sure text area is editable before modification
                is_disabled = textarea.cget('state') == tk.DISABLED
                if is_disabled:
                    textarea.config(state=tk.NORMAL)

                textarea.delete('1.0', tk.END)
                textarea.insert('1.0', content)

                if is_disabled: # Restore state if needed (e.g., for result area)
                    textarea.config(state=tk.DISABLED)

        except Exception as e:
             # Show error message to the user
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
            # Inform user that both fields are required
            messagebox.showwarning("Немає даних", "Будь ласка, введіть або завантажте обидва тексти.") # UI String
            return

        # Update UI to indicate processing
        self.analyze_button.config(state=tk.DISABLED, text="Аналіз...") # UI String
        self.display_result("Обробка запиту...") # UI String: "Processing request..."
        self.root.update_idletasks() # Force UI update

        try:
            # Perform the actual analysis by calling the backend logic
            result = perform_analysis(text1, text2)
            self.display_result(result) # Show result from LLM

        except (LLMConnectionError, LLMResponseError) as e:
            # Handle specific LLM errors and inform the user
            error_msg = f"Не вдалося виконати аналіз:\n{e}" # UI String
            messagebox.showerror("Помилка LLM", error_msg) # UI String
            self.display_result(f"Помилка: {e}") # Show error in result area
        except ValueError as e:
            # Handle validation errors (e.g., empty input, though checked above)
            messagebox.showwarning("Невірні дані", str(e)) # UI String
            self.display_result("") # Clear result area
        except Exception as e:
            # Handle any other unexpected errors
            error_msg = f"Сталася неочікувана помилка: {e}" # UI String
            messagebox.showerror("Неочікувана помилка", error_msg) # UI String
            self.display_result(f"Неочікувана помилка: {e}")
            print(f"Unexpected error during analysis: {e}") # Log for developer debugging
        finally:
            # Always re-enable the analyze button, regardless of success or failure
            self.analyze_button.config(state=tk.NORMAL, text="Аналізувати на плагіат") # UI String


# Keep the main block for potential separate testing of the GUI module
if __name__ == '__main__':
    print("Running GUI module directly for testing...")
    root = tk.Tk()
    app = PlagiarismApp(root)
    root.mainloop()