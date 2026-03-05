# ---------- Stage 1: Builder ----------
FROM python:3.12-slim AS builder

WORKDIR /build

# Install system deps for psycopg2
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY app/requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---------- Stage 2: Production ----------
FROM python:3.12-slim

# Install libpq for psycopg2 runtime
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq5 && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser -d /home/appuser -s /sbin/nologin appuser

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local

# Set working directory
WORKDIR /home/appuser/app

# Copy application code
COPY app/ .
COPY entrypoint.sh /home/appuser/entrypoint.sh
COPY gunicorn.conf.py /home/appuser/gunicorn.conf.py

# Create directories for static and media
RUN mkdir -p /home/appuser/app/staticfiles /home/appuser/app/media && \
    chown -R appuser:appuser /home/appuser

# Set environment
ENV DJANGO_SETTINGS_MODULE=confessions_project.settings.prod
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Entrypoint
ENTRYPOINT ["/home/appuser/entrypoint.sh"]
