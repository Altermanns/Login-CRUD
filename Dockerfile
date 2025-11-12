# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=LoginCRUD.settings.production

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Create necessary directories
RUN mkdir -p /app/staticfiles /app/Texcore/static/css /app/Texcore/static/js

# Backup existing database if it exists
RUN if [ -f "/app/db.sqlite3" ]; then \
        echo "📦 Database found, preserving existing data..."; \
        cp /app/db.sqlite3 /app/db_backup.sqlite3; \
    else \
        echo "📋 No existing database, will create fresh one..."; \
    fi

# Ensure db.sqlite3 has correct permissions
RUN chmod 664 /app/db.sqlite3 2>/dev/null || touch /app/db.sqlite3 && chmod 664 /app/db.sqlite3

# Don't run migrations here - let entrypoint handle it to preserve data
# RUN python manage.py migrate --noinput --settings=LoginCRUD.settings.production

# Collect static files
RUN python manage.py collectstatic --noinput --settings=LoginCRUD.settings.production

# Create non-root user and change ownership
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Copy and set permissions for entrypoint script
COPY --chown=appuser:appuser entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

# Run entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]