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
# Ensure dashboard.html is in the same directory as main.py
COPY . .

# Expose the port (Render uses the $PORT env var)
EXPOSE 8080

# Start the application using a shell-form CMD
# This ensures that the ${PORT} environment variable provided by Render 
# is correctly expanded by the shell before uvicorn starts.
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT}
