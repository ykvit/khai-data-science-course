# Use the official Python image (version 3.12.8 based on slim)
FROM python:3.12.8-slim-bookworm

# Set the working directory in the container
WORKDIR /app

# Update pip and install required packages
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip install pandas openpyxl

# Create necessary directories
RUN mkdir -p data output

# Copy only the necessary files and directories
COPY src/ /app/src/
COPY data/LW3.xlsx /app/data/

# Add src directory to Python path
ENV PYTHONPATH=/app/src

# Command to run the project
CMD ["python", "src/main.py"]