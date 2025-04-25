# Use an official Python runtime as a parent image
# FROM python:3.13.3-alpine
FROM python:3.13.3-slim-bookworm

# Set the working directory in the container
WORKDIR /app

# Install system dependencies for Tkinter and X11 forwarding
RUN apt-get update && apt-get install -y --no-install-recommends \
    tk8.6 \
    python3-tk \
    libx11-6 \
    && rm -rf /var/lib/apt/lists/*

# Copy all project files to the container
COPY . .

# Setting up dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Command to start the project
CMD ["python", "main.py"]