# ──────────────────────────────────────────────────────────
#  LifePulse — Dockerfile for Google Cloud Run
#  Multi-stage build optimised for cold-start performance
# ──────────────────────────────────────────────────────────

# Stage 1: dependency builder
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build tools needed by some wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        libffi-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install --no-cache-dir --prefix=/install -r requirements.txt


# Stage 2: lean runtime image
FROM python:3.11-slim AS runtime

# ── Non-root user for Cloud Run security best practice
RUN addgroup --system lifepulse && adduser --system --ingroup lifepulse lifepulse

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application source
COPY app.py .

# Streamlit configuration
RUN mkdir -p /app/.streamlit
COPY streamlit_config.toml /app/.streamlit/config.toml

# Cloud Run injects PORT env var (default 8080)
ENV PORT=8080 \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_ENABLE_CORS=false \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

USER lifepulse

EXPOSE 8080

# Healthcheck — Cloud Run will probe after startup
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/_stcore/health')"

ENTRYPOINT ["streamlit", "run", "app.py", \
            "--server.port=8080", \
            "--server.address=0.0.0.0", \
            "--server.headless=true", \
            "--server.enableCORS=false", \
            "--server.enableXsrfProtection=true"]
