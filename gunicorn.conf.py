"""Gunicorn configuration for production."""

import multiprocessing

# Bind to all interfaces on port 8000
bind = "0.0.0.0:8000"

# Number of workers (2 * CPU cores + 1)
workers = multiprocessing.cpu_count() * 2 + 1

# Worker class
worker_class = "sync"

# Timeout (seconds)
timeout = 120

# Graceful timeout
graceful_timeout = 30

# Keep alive
keepalive = 5

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Max requests before worker restart (prevents memory leaks)
max_requests = 1000
max_requests_jitter = 50
