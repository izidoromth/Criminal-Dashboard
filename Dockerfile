# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set environment variables for Python and buffering
ENV PYTHONUNBUFFERED 1

# Install GDAL dependencies
RUN apt-get update && apt-get install -y \
    binutils \
    libproj-dev \
    gdal-bin \
    libgdal-dev

# Set GDAL environment variables
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

# Create and set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container
COPY . /app/

EXPOSE 8150

# Start your application
CMD [ "python", "dashboard/app.py" ]
