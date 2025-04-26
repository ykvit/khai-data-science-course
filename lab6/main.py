"""
Main entry point script for launching the plagiarism analysis application.
"""

import tkinter as tk
import sys
from src.gui import PlagiarismApp
from src.config import load_api_key

api_key = load_api_key()

# Check if the API key was loaded successfully
if not api_key:
    print("ERROR: GOOGLE_API_KEY not found in .env or environment variables.", file=sys.stderr)
    print("Please create a .env file in the lab6/ directory based on .env.example", file=sys.stderr)

def main():
    """
    Initializes and runs the Tkinter application.
    """
    root = tk.Tk()
    app = PlagiarismApp(root)
    root.mainloop()

# Standard Python entry point check
if __name__ == "__main__":
    main()