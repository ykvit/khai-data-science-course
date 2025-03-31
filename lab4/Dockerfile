# Use an official Python runtime as a parent image
FROM python:3.12.8-slim-bookworm

# Set the working directory in the container
WORKDIR /app

# Copy all project files to the container
COPY . .

# Setting up dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Command to start the project
CMD ["python", "main.py"]