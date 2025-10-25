FROM python:3.11-slim

# System deps for building some Python packages (psycopg2) and general utilities
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       gcc \
       libpq-dev \
       curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Prevent Python from writing .pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install project dependencies declared in pyproject.toml
COPY pyproject.toml /app/
RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir .

# Copy project sources
COPY . /app

EXPOSE 5000

# Use gunicorn to serve the Flask app (main:app) on port 5000
CMD ["gunicorn", "--preload", "--bind", "0.0.0.0:5000", "main:app", "--workers", "3"]
