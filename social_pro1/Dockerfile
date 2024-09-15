# Use the official Python image from the Docker Hub
FROM python:3.12.1

# Set the working directory inside the container
WORKDIR /app

# Copy the project files to the working directory
COPY . /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose port 8000 to be accessible from outside the container
EXPOSE 8000

# Command to run the Django server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
 
