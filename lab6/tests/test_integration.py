import pytest
import os
from src import llm_integration, analysis

API_KEY_AVAILABLE = llm_integration.API_KEY is not None

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
    except (llm_integration.LLMConnectionError, llm_integration.LLMResponseError) as e:
        pytest.fail(f"LLM API call failed: {e}")

@pytest.mark.skipif(not API_KEY_AVAILABLE, reason="GOOGLE_API_KEY not set, skipping integration test")
def test_analysis_integration_similar_texts():
    """Tests perform_analysis with a real LLM call."""
    text1 = "The quick brown fox jumps over the lazy dog."
    text2 = "A fast brown fox leaps over a sleepy dog."
    try:
        result = analysis.perform_analysis(text1, text2)
        assert isinstance(result, str)
        assert "схожість" in result.lower() or "similarity" in result.lower()
    except (llm_integration.LLMConnectionError, llm_integration.LLMResponseError) as e:
        pytest.fail(f"Analysis with LLM call failed: {e}")