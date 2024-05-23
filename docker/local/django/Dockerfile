# This Dockerfile uses a multi-stage build approach to:
# 1. Build dependency wheels.
# 2. Run the application.

# Set the Python version as an argument with a default value.
ARG PYTHON_VERSION=3.11.8-bullseye

# First stage: Use the specified Python version as the base image for the initial stage.
FROM python:${PYTHON_VERSION} as python

# Second stage: Build stage to create Python wheels for dependencies.
FROM python as python-build-stage

# Argument for the build environment, defaulting to 'local'.
ARG BUILD_ENVIRONMENT=local

# Update the package list and install necessary build tools and libraries.
# Essential tools for building software (e.g., gcc, g++).
# PostgreSQL development libraries for psycopg2.
RUN apt-get update && apt-get install --no-install-recommends -y \
    build-essential \   
    libpq-dev           

# Copy the requirements files to the container.
COPY ./requirements .

# Create Python wheel packages for the dependencies listed in the requirements file.
RUN pip wheel --wheel-dir /usr/src/app/wheels -r ${BUILD_ENVIRONMENT}.txt

# Third stage: Final stage to run the application.
FROM python as python-run-stage

# Re-declare the build environment argument for this stage.
ARG BUILD_ENVIRONMENT=local

# Set the application home directory as an argument.
ARG APP_HOME=/app

# Set environment variables:
# Prevent Python from writing .pyc files to the disk.
# Ensure Python output is sent straight to the terminal without buffering.
# Set the build environment.

ENV PYTHONDONTWRITEBYTECODE=1 
ENV PYTHONBUFFERED=1          
ENV BUILD_ENV=${BUILD_ENVIRONMENT} 

# Set the working directory inside the container to the application home directory.
WORKDIR ${APP_HOME}

# Update the package list, install required libraries, then clean up to reduce image size.
# PostgreSQL development libraries for psycopg2.
# GNU gettext for message translation.
# Remove unnecessary packages.
# Clean up package lists.
RUN apt-get update && apt-get install --no-install-recommends -y \
    libpq-dev \   
    gettext \    
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \  
    && rm -rf /var/lib/apt/lists/*   

# Copy the built wheels from the build stage to the current stage.
COPY --from=python-build-stage /usr/src/app/wheels /wheels/

# Install the dependencies using the pre-built wheels and then remove the wheels to save space.
RUN pip install --no-cache-dir --no-index --find-links=/wheels/ /wheels/* \
    && rm -rf /wheels/

# Copy the entrypoint script from the local directory to the container.
COPY ./docker/local/django/entrypoint /entrypoint

# Convert Windows-style line endings to Unix-style to avoid issues.
RUN sed -i 's/\r$//g' /entrypoint

# Make the entrypoint script executable.
RUN chmod +x /entrypoint

# Copy the start script from the local directory to the container.
COPY ./docker/local/django/start /start

# Convert Windows-style line endings to Unix-style to avoid issues.
RUN sed -i 's/\r$//g' /start

# Make the start script executable.
RUN chmod +x /start

# Copy the entire project directory into the container.
COPY . ${APP_HOME}

# Set the entrypoint to the entrypoint script to ensure it runs when the container starts.
ENTRYPOINT ["/entrypoint"]



# Key Points:
# Multi-Stage Build:

# Stage 1: Uses a specified Python base image.
# Stage 2: Installs build tools and creates Python wheels for dependencies.
# Stage 3: Runs the application using the wheels built in the previous stage.
# Environment Variables and Working Directory:

# Environment variables manage Python behavior and define the application directory.
# WORKDIR sets the working directory for subsequent instructions.
# Package Management and Cleanup:

# Installs necessary build tools and libraries in the build stage.
# Cleans up package lists and unnecessary files to reduce the final image size.
# Script Preparation:

# Copies and prepares the entrypoint and start scripts, ensuring they have the correct line endings and permissions.
# Entrypoint:

# Sets the entrypoint script to ensure it runs specific commands when the container starts.
# This detailed commenting should help clarify the purpose and function of each part of the Dockerfile.
