# Multi-stage Dockerfile for OSINT Toolkit
# Stage 1: Builder - Compile and build dependencies
FROM python:3.11-slim as builder

LABEL maintainer="OSINT Team"
LABEL description="OSINT Toolkit - Builder Stage"

# Set working directory
WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    libpq-dev \
    libssl-dev \
    libffi-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime - Minimal production image
FROM python:3.11-slim

LABEL maintainer="OSINT Team"
LABEL description="OSINT Toolkit - Production Image"

# Create non-root user for security
RUN groupadd -r osint && useradd -r -g osint -u 1000 osint

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Copy application code
COPY --chown=osint:osint . .

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# Health check configuration
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Expose application port
EXPOSE 8000

# Create necessary directories with proper permissions
RUN mkdir -p /app/logs /app/data /app/cache && \
    chown -R osint:osint /app

# Switch to non-root user
USER osint

# Volume for persistent data
VOLUME ["/app/data", "/app/logs"]

# Default command
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
