"""
Module for interacting with the Google Gemini API.
"""

import google.generativeai as genai
import os
from .config import load_api_key, get_gemini_model_name
from .exceptions import LLMConnectionError, LLMResponseError

# Load the API key once when the module is imported
API_KEY = load_api_key()

if API_KEY:
    try:
        genai.configure(api_key=API_KEY)
    except Exception as e:
        print(f"Error configuring Google GenAI: {e}")
        API_KEY = None # Assume the key is invalid
else:
    print("WARNING: Google API key not found. LLM analysis will be unavailable.")

def check_plagiarism_with_gemini(text1: str, text2: str) -> str:
    """
    Sends two texts to Google Gemini for plagiarism analysis.

    Args:
        text1: The first text to compare.
        text2: The second text to compare.

    Returns:
        str: The analysis result from the LLM.

    Raises:
        LLMConnectionError: If the API key is not configured or a connection error occurs.
        LLMResponseError: If the LLM returns an error or an unexpected response format.
    """
    if not API_KEY:
        raise LLMConnectionError("Google API key is not configured or is invalid.")

    model_name = get_gemini_model_name()
    try:
        model = genai.GenerativeModel(model_name)

        # Construct the prompt for Gemini
        # Providing clear instructions is important
        prompt = f"""
        Analyse the following two texts for plagiarism.
        Estimate the degree of similarity in percentage terms and, if possible, indicate the main similarities.
        Answer without using Markdown
        Please write your answer in Ukrainian.

        Текст 1:
        ---
        {text1}
        ---

        Текст 2:
        ---
        {text2}
        ---

        Результат аналізу:
        """

        generation_config = genai.types.GenerationConfig(
            temperature=0.3 
        )

        # Send the request
        response = model.generate_content(
            prompt,
            generation_config=generation_config
            )

        # Process the response
        if response and response.text:
            return response.text.strip()
        else:
            error_details = getattr(response, 'prompt_feedback', 'Unknown response error.')
            raise LLMResponseError(f"LLM did not return a text response. Details: {error_details}")

    except Exception as e:
        print(f"Error during request to Gemini API: {e}") # Log the error
        if isinstance(e, genai.types.BlockedPromptException):
             raise LLMResponseError(f"Prompt blocked due to safety settings: {e}")
        elif isinstance(e, (genai.types.StopCandidateException, genai.types.InvalidResponseError)):
             raise LLMResponseError(f"LLM generation issue: {e}")
        elif isinstance(e, Exception): # Catch-all for other API or network issues
             raise LLMConnectionError(f"Connection or request error with Gemini API: {e}")
        else:
             raise LLMResponseError(f"Unexpected error during LLM interaction: {e}")


if __name__ == '__main__':
    # Simple test for the module (requires a valid .env file)
    print("Testing llm_integration module...")
    if not API_KEY:
        print("Testing cannot proceed: API key not loaded.")
    else:
        test_text1 = "Це перший тестовий текст для перевірки." # UI String
        test_text2 = "А це другий текст, також для тестування." # UI String
        test_text3 = "Це перший тестовий текст для перевірки." # UI String (Exact duplicate)

        try:
            print("\nTest 1: Different texts")
            result1 = check_plagiarism_with_gemini(test_text1, test_text2)
            print(f"Result:\n{result1}")

            print("\nTest 2: Identical texts")
            result2 = check_plagiarism_with_gemini(test_text1, test_text3)
            print(f"Result:\n{result2}")

        except (LLMConnectionError, LLMResponseError) as e:
            print(f"\nError during testing: {e}")