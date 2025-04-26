"""
Custom exception classes for the plagiarism analysis application.
"""

class LLMError(Exception):
    """Base class for errors related to the Large Language Model."""
    pass

class LLMConnectionError(LLMError):
    """Error related to connecting to or configuring the LLM API."""
    pass

class LLMResponseError(LLMError):
    """Error related to the response received from the LLM (e.g., bad format, processing error, blocked prompt)."""
    pass

# mb later
# class FileReadError(Exception):
#     """Error encountered while reading a user-provided file."""
#     pass