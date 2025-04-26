"""
Utility functions for the application.
"""

import tkinter as tk
from tkinter import filedialog, scrolledtext

def load_text_from_file() -> str | None:
    """
    Opens a file dialog for the user to select a file and reads its content.

    Returns:
        str: The content of the file as a string, if successfully read.
        None: If the user cancels the dialog or an error occurs during reading.

    Raises:
        Exception: If an error occurs during file opening or reading
                   (this exception is handled by the caller in gui.py).
    """
    file_path = filedialog.askopenfilename(
        title="Вибрати текстовий файл", # UI String: "Select text file"
        filetypes=(("Text files", "*.txt"),
                   ("Python files", "*.py"),
                   ("Java files", "*.java"),
                   ("All files", "*.*"))
    )
    if not file_path: # User cancelled
        return None

    try:
        # Read with UTF-8 encoding
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        # Re-raise the exception to be handled by the GUI
        raise


def clear_text_area(text_area: scrolledtext.ScrolledText):
    """Clears the content of a ScrolledText widget."""
    # Ensure the widget is editable before modifying
    is_disabled = text_area.cget('state') == tk.DISABLED
    if is_disabled:
        text_area.config(state=tk.NORMAL)

    text_area.delete('1.0', tk.END)

    # Restore state if it was disabled
    if is_disabled:
        text_area.config(state=tk.DISABLED)