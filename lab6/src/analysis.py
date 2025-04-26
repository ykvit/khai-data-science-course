"""
Module for performing the plagiarism analysis logic.
"""

from .llm_integration import check_plagiarism_with_gemini
from .exceptions import LLMConnectionError, LLMResponseError

def perform_analysis(text1: str, text2: str) -> str:
    """
    Performs plagiarism analysis between two texts by calling the LLM.

    Args:
        text1: The first text.
        text2: The second text.

    Returns:
        str: The formatted analysis result.

    Raises:
        LLMConnectionError: If a connection error occurs with the LLM API.
        LLMResponseError: If an error occurs during LLM request processing.
        ValueError: If the input texts are empty.
    """
    if not text1 or not text2:
        raise ValueError("Both text fields must be filled.")

    try:
        result = check_plagiarism_with_gemini(text1, text2)
        return result

    except (LLMConnectionError, LLMResponseError) as e:
        print(f"Error at analysis layer: {e}")
        raise 


if __name__ == '__main__':
    print("Testing analysis module...")
    from .llm_integration import API_KEY
    if not API_KEY:
         print("Testing cannot proceed: API key not loaded.")
    else:
        test_text1 = "Основні принципи програмування включають інкапсуляцію, успадкування та поліморфізм."
        test_text2 = "Ключовими концепціями об'єктно-орієнтованого програмування є інкапсуляція даних, механізм успадкування класів та поліморфізм методів."
        test_text3 = ""

        try:
            print("\nTest 1: Similar texts")
            result1 = perform_analysis(test_text1, test_text2)
            print(f"Result:\n{result1}")

            print("\nTest 2: Empty text (should raise ValueError)")
            try:
                 perform_analysis(test_text1, test_text3)
            except ValueError as e:
                 print(f"Caught expected error: {e}")

        except (LLMConnectionError, LLMResponseError) as e:
            print(f"\nError during testing: {e}")