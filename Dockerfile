# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container
COPY . .

EXPOSE 5000

# Command to run the Flask application using Gunicorn (recommended for production)
# Make sure you have `gunicorn` in your requirements.txt
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:create_app()"]
