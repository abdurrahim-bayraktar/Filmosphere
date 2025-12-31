FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    DJANGO_SETTINGS_MODULE=config.settings_prod

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Collect static files
RUN python manage.py collectstatic --no-input || echo "Static collection skipped"

EXPOSE 8000

# Run migrations and start gunicorn with memory-optimized settings
# - 1 worker (less memory for free tier)
# - 120s timeout (more time to start)
# - preload to reduce memory
CMD python manage.py migrate && \
    gunicorn config.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 1 \
    --threads 2 \
    --timeout 120 \
    --preload

