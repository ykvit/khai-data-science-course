# Use the official Python image (for example, version 3.12.8 based on slim)
FROM python:3.12.8-slim-bookworm

# Set the working directory in the container
WORKDIR /app

# Copy all project files to the container
COPY . .

# Command to start the project
CMD ["sh", "-c", "python main.py && tail -f /dev/null"]
