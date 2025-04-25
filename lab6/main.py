# lab6/main.py
# -*- coding: utf-8 -*-
"""
Головний скрипт запуску додатку аналізу плагіату.
"""

import tkinter as tk
from src.gui import PlagiarismApp
from src.config import load_api_key 
import sys

api_key = load_api_key()

if not api_key:
    print("ПОМИЛКА: GOOGLE_API_KEY не знайдено в .env або змінних середовища.", file=sys.stderr)
    print("Будь ласка, створіть файл .env у директорії lab6/ за прикладом .env.example", file=sys.stderr)
    # sys.exit(1) 

def main():
    """
    Основна функція для запуску програми.
    """
    root = tk.Tk()
    app = PlagiarismApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()