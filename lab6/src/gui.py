# lab6/src/gui.py
# -*- coding: utf-8 -*-
"""
Модуль для графічного інтерфейсу користувача (GUI)
для аналізу плагіату тексту за допомогою LLM.
"""

import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import os

# from .utils import load_text_from_file
# from .analysis import perform_analysis
# from .config import get_api_key

def load_text_from_file():
    """Заглушка: Завантажує текст з файлу."""
    file_path = filedialog.askopenfilename(
        title="Вибрати текстовий файл",
        filetypes=(("Text files", "*.txt"),
                   ("Python files", "*.py"),
                   ("Java files", "*.java"),
                   ("All files", "*.*"))
    )
    if file_path:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            messagebox.showerror("Помилка читання файлу", f"Не вдалося прочитати файл:\n{e}")
            return None
    return None

def perform_analysis(text1, text2):
    """Заглушка: Виконує аналіз плагіату."""
    print("Виконується аналіз...")
    print(f"Текст 1 (перші 50 символів): {text1[:50]}")
    print(f"Текст 2 (перші 50 символів): {text2[:50]}")
    # llm_integration.check_plagiarism

    import time
    time.sleep(1)
    return "Результат аналізу:\nСхожість: 75%\n\nСхожі фрагменти:\n- Фрагмент А...\n- Фрагмент Б..."

def get_api_key():
    """Заглушка: Перевіряє наявність API ключа."""

    print("Перевірка API ключа...")
    key = os.getenv("GOOGLE_API_KEY") 
    if not key:
        print("API ключ не знайдено у змінних середовища.")
        # messagebox.showwarning
    return key


class PlagiarismApp:
    """
    Головний клас додатку для аналізу плагіату.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Аналізатор Плагіату на базі LLM")
        self.root.minsize(600, 400)

        # if not get_api_key():
        #    messagebox.showerror("Помилка конфігурації", "API Ключ Google не налаштовано!")
            # Можна або вимкнути кнопку аналізу, або закрити додаток
            # self.root.quit()

        top_frame = tk.Frame(self.root)
        top_frame.pack(padx=10, pady=5, fill=tk.X)

        middle_frame = tk.Frame(self.root)
        middle_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(padx=10, pady=10, fill=tk.X)

        label1 = tk.Label(top_frame, text="Текст 1:")
        label1.pack(side=tk.LEFT, padx=5)
        self.load_button1 = tk.Button(
            top_frame, text="Завантажити файл 1", command=self.load_file1
        )
        self.load_button1.pack(side=tk.LEFT)

        self.text_area1 = scrolledtext.ScrolledText(middle_frame, wrap=tk.WORD, height=10)
        self.text_area1.pack(side=tk.LEFT, padx=5, fill=tk.BOTH, expand=True)

        label2 = tk.Label(top_frame, text="Текст 2:")
        label2.pack(side=tk.LEFT, padx=5, pady=5)
        self.load_button2 = tk.Button(
            top_frame, text="Завантажити файл 2", command=self.load_file2
        )
        self.load_button2.pack(side=tk.LEFT, padx=(0, 5))

        self.text_area2 = scrolledtext.ScrolledText(middle_frame, wrap=tk.WORD, height=10)
        self.text_area2.pack(side=tk.RIGHT, padx=5, fill=tk.BOTH, expand=True)


        self.analyze_button = tk.Button(
            bottom_frame, text="Аналізувати на плагіат", command=self.analyze
        )
        self.analyze_button.pack(side=tk.LEFT, padx=5)

        self.result_label = tk.Label(bottom_frame, text="Результат аналізу:")
        self.result_label.pack(side=tk.LEFT, padx=5)

        self.result_area = scrolledtext.ScrolledText(bottom_frame, wrap=tk.WORD, height=5, state=tk.DISABLED)
        self.result_area.pack(pady=5, fill=tk.X, expand=True)


    def load_file_to_textarea(self, textarea):
        """Завантажує текст з файлу у вказане текстове поле."""
        content = load_text_from_file() 
        if content:
            textarea.delete('1.0', tk.END)
            textarea.insert('1.0', content)

    def load_file1(self):
        """Обробник кнопки завантаження для Тексту 1."""
        self.load_file_to_textarea(self.text_area1)

    def load_file2(self):
        """Обробник кнопки завантаження для Тексту 2."""
        self.load_file_to_textarea(self.text_area2)

    def analyze(self):
        """Виконує аналіз плагіату для введених текстів."""
        text1 = self.text_area1.get('1.0', tk.END).strip()
        text2 = self.text_area2.get('1.0', tk.END).strip()

        if not text1 or not text2:
            messagebox.showwarning("Немає даних", "Будь ласка, введіть або завантажте обидва тексти.")
            return

        self.analyze_button.config(state=tk.DISABLED, text="Аналіз...")
        self.root.update_idletasks()

        try:

            result = perform_analysis(text1, text2)

            self.result_area.config(state=tk.NORMAL)
            self.result_area.delete('1.0', tk.END)
            self.result_area.insert('1.0', result)
            self.result_area.config(state=tk.DISABLED)

        except Exception as e:
            messagebox.showerror("Помилка аналізу", f"Сталася помилка: {e}")
            self.result_area.config(state=tk.NORMAL)
            self.result_area.delete('1.0', tk.END)
            self.result_area.config(state=tk.DISABLED)
        finally:

            self.analyze_button.config(state=tk.NORMAL, text="Аналізувати на плагіат")


if __name__ == '__main__':
    print("Запуск GUI модуля для тестування...")
    root = tk.Tk()
    app = PlagiarismApp(root)
    root.mainloop()