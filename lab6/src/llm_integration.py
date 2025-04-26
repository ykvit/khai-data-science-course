"""
Integration tests that may require external services (like LLM API).
"""

import pytest
import os
import google.generativeai as genai 
from src import llm_integration, analysis, config, exceptions

API_KEY_FROM_ENV = os.getenv("GOOGLE_API_KEY")
API_KEY_AVAILABLE = bool(API_KEY_FROM_ENV) 

@pytest.fixture(autouse=True, scope='module')
def setup_llm_integration():
    """
    Fixture to explicitly configure the genai library and update the
    llm_integration.API_KEY variable before integration tests run.
    """
    if API_KEY_AVAILABLE:
        print(f"\nAttempting to configure GenAI for integration tests (Key: {API_KEY_FROM_ENV[:4]}...).")
        try:
            genai.configure(api_key=API_KEY_FROM_ENV)
            llm_integration.API_KEY = API_KEY_FROM_ENV
            print("GenAI configured successfully for tests.")
        except Exception as e:
            pytest.fail(f"CRITICAL: Failed to configure genai in fixture: {e}")
    else:
        print("\nWARNING: GOOGLE_API_KEY not found in environment. Integration tests will be skipped.")
        llm_integration.API_KEY = None
    yield

# --- The tests remain almost the same, but now they use the configuration from the fixture ---

@pytest.mark.skipif(not API_KEY_AVAILABLE, reason="GOOGLE_API_KEY not set, skipping integration test")
def test_gemini_api_call_different_texts():
    """Tests a real call to the Gemini API with different texts."""
    text1 = "Hello world."
    text2 = "Goodbye world."
    try:
        result = llm_integration.check_plagiarism_with_gemini(text1, text2)
        assert isinstance(result, str)
        assert len(result) > 10
        assert "схожість" in result.lower() or "similarity" in result.lower()
    except (exceptions.LLMConnectionError, exceptions.LLMResponseError) as e:
        pytest.fail(f"LLM API call failed unexpectedly during test: {e}")


@pytest.mark.skipif(not API_KEY_AVAILABLE, reason="GOOGLE_API_KEY not set, skipping integration test")
def test_analysis_integration_similar_texts():
    """Tests perform_analysis with a real LLM call."""
    text1 = "The quick brown fox jumps over the lazy dog."
    text2 = "A fast brown fox leaps over a sleepy dog."
    try:
        result = analysis.perform_analysis(text1, text2)
        assert isinstance(result, str)
        assert "схожість" in result.lower() or "similarity" in result.lower()
    except (exceptions.LLMConnectionError, exceptions.LLMResponseError) as e:
        pytest.fail(f"Analysis with LLM call failed unexpectedly during test: {e}")