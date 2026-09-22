# ---------------------------------------------------------------------
# Dockerfile - AI-Powered Smart Fitness Tracking & Health Monitoring System
# ---------------------------------------------------------------------
FROM python:3.11-slim

# Prevent Python from writing .pyc files and buffer stdout for cleaner logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies needed by scikit-learn / pandas wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (better Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Flask app listens on port 5000
EXPOSE 5000

# Basic container health check hitting the JSON health-check endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/api/health-check')" || exit 1

# Run with gunicorn in production-style mode (falls back fine for demo use)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]
