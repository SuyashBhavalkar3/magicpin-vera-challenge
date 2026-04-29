# Use a high-performance Python base image
FROM python:3.11-slim

# Set environment variables for better performance
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PORT 8080

# Set the working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose the port (Railway will use the PORT env var)
EXPOSE 8080

# Start the application using Uvicorn
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT}
