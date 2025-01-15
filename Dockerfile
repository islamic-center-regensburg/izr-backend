# Use the official Python image from Docker Hub
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt /app/

# Install dependencies
RUN pip install --upgrade pip

# Copy the entire Django project to the container
COPY . /app/


# Expose the port the app runs on
#EXPOSE 8000

# Run the Django server
#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
CMD ["gunicorn", "izr_server.wsgi:application","--bind","0.0.0.0:8000"]
