# Use the official Python image from Docker Hub
FROM python:3.12-bullseye

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt /app/

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy the entire Django project to the container
COPY . /app/

# Collect static files
RUN python3 manage.py collectstatic --noinput
#
RUN mv IZRLOGOROUND.png /app/statcifiles/IZRLOGOROUND.png
# Run database migrations
RUN python3 manage.py migrate

# Expose the port the app runs on
EXPOSE 8000

# Run the Django application with Gunicorn
CMD ["gunicorn", "izr_server.wsgi:application", "--bind", "0.0.0.0:8000"]
