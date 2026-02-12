# Use an official Python runtime as a parent image
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Copy dependency file first (helps with caching)
COPY pyproject.toml .
COPY mensabot ./mensabot

# Install Python dependencies
RUN pip install .
RUN playwright install-deps chromium
RUN playwright install 

