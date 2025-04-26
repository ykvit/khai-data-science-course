"""
Module for handling configuration, especially API keys.
"""

import os
from dotenv import load_dotenv

def load_api_key():
    """
    Loads the Google API key from a .env file or environment variables.

    Searches for a .env file in the parent directory (lab6/).

    Returns:
        str | None: The API key if found, otherwise None.
    """
    # Construct the path to the .env file located in the parent directory (lab6/)
    # __file__ -> lab6/src/config.py
    # os.path.dirname(__file__) -> lab6/src
    # os.path.dirname(os.path.dirname(__file__)) -> lab6
    dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    load_dotenv(dotenv_path=dotenv_path)
    api_key = os.getenv("GOOGLE_API_KEY")
    return api_key

def get_gemini_model_name():
    """Returns the Gemini model name to be used."""
    # I chose a small model
    return "gemini-2.5-flash-preview-04-17"

if __name__ == '__main__':
    key = load_api_key()
    if key:
        print(f"API key found: {key[:4]}...{key[-4:]}")
    else:
        print("API key not found.")
    print(f"Using Gemini model: {get_gemini_model_name()}")