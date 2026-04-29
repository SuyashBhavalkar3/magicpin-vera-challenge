# Use a high-performance Python base image
FROM python:3.11-slim

# Set environment variables using modern format
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Set the working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose the port
EXPOSE 8080

# Start the application using JSON format for better signal handling
# We use 'sh -c' to ensure the ${PORT} variable is expanded
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
