"""
Модуль для роботи з конфігурацією, зокрема API ключами.
"""

import os
from dotenv import load_dotenv

def load_api_key():
    """
    Завантажує API ключ Google з файлу .env або змінних середовища.

    Returns:
        str | None: API ключ, якщо знайдено, інакше None.
    """
    # __file__ -> lab6/src/config.py
    # os.path.dirname(__file__) -> lab6/src
    # os.path.dirname(os.path.dirname(__file__)) -> lab6
    dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    load_dotenv(dotenv_path=dotenv_path)
    api_key = os.getenv("GOOGLE_API_KEY")
    return api_key

def get_gemini_model_name():
    """Повертає ім'я моделі Gemini для використання."""

    return "gemini"

if __name__ == '__main__':
    key = load_api_key()
    if key:
        print(f"Знайдено API ключ: {key[:4]}...{key[-4:]}") 
    else:
        print("API ключ не знайдено.")
    print(f"Використовувана модель Gemini: {get_gemini_model_name()}")