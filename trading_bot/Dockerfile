# Use official Python image
FROM python:3.8-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    unixodbc-dev \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better cache usage
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Environment variables
ENV PYTHONUNBUFFERED=1

# Command to run the application
CMD ["python", "main.py"]
