# Use a high-performance Python base image
FROM python:3.11-slim

# Set environment variables
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

# Expose the port
EXPOSE 8080

# Use Uvicorn directly as the entry point
# We use the shell form so ${PORT} is expanded correctly by Railway
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT}
