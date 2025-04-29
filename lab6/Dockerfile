# Use the official Python Alpine image as a base
FROM python:3.13.3-alpine

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required for Tkinter on Alpine
RUN apk update && \
    apk add --no-cache tk fontconfig ttf-dejavu && \
    rm -rf /var/cache/apk/*

# Copy the requirements file first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source code and main script
COPY src/ ./src/
COPY main.py .

# Command to start the project
CMD ["python", "main.py"]