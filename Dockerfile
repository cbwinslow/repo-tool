# Build stage
FROM python:3.9-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Install development dependencies and build
RUN pip install -e ".[dev]" && \
    make build

# Runtime stage
FROM python:3.9-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    git \
    nodejs \
    && rm -rf /var/lib/apt/lists/*

# Copy built application from builder
COPY --from=builder /app /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    REPO_TOOL_CONFIG_DIR=/config \
    REPO_TOOL_DATA_DIR=/data \
    REPO_TOOL_LOG_DIR=/logs

# Create necessary directories
RUN mkdir -p /config /data /logs && \
    chmod 777 /config /data /logs

# Create non-root user
RUN useradd -m -s /bin/bash repo-tool && \
    chown -R repo-tool:repo-tool /app /config /data /logs

USER repo-tool

# Expose port if needed
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Set entrypoint
ENTRYPOINT ["python", "-m", "repo_tool"]

