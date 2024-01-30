# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set environment variables to prevent Python from writing pyc files and buffering output
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create and set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 80 for the Flask app to listen on
EXPOSE 80

# Define the command to run the application
CMD ["python", "app.py"]
