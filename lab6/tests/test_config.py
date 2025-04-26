"""
Unit tests for the configuration module (src/config.py).
"""

import pytest
import os
from src import config 

def test_get_gemini_model_name():
    """Test that get_gemini_model_name returns the expected model string."""
    expected_model = "gemini-2.5-flash-preview-04-17"
    actual_model = config.get_gemini_model_name()
    assert actual_model == expected_model

def test_load_api_key_found(mocker):
    """Test load_api_key when the environment variable is set."""
    # Mock os.getenv to return a fake key
    fake_key = "fake_api_key_123"
    mocker.patch('os.getenv', return_value=fake_key)
    # Mock load_dotenv to do nothing, as we are mocking os.getenv directly
    mocker.patch('src.config.load_dotenv')

    loaded_key = config.load_api_key()
    assert loaded_key == fake_key
    config.load_dotenv.assert_called_once()

def test_load_api_key_not_found(mocker):
    """Test load_api_key when the environment variable is NOT set."""
    # Mock os.getenv to return None
    mocker.patch('os.getenv', return_value=None)
    mocker.patch('src.config.load_dotenv')

    loaded_key = config.load_api_key()
    assert loaded_key is None
    config.load_dotenv.assert_called_once()
