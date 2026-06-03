# Production ready slim Python base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

WORKDIR /app

# Install system dependencies (including git for optional checks, and standard utilities)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install python packages directly (keeps build layer clean and fast)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    fastapi \
    uvicorn \
    pydantic \
    pandas \
    openpyxl \
    pypdf \
    opencv-python-headless \
    pytest \
    pytest-cov

# Copy the entire workspace into /app
COPY . /app

# Ensure correct PYTHONPATH
ENV PYTHONPATH=/app/store-intelligence

# Run uvicorn server on the port specified by environment
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT
