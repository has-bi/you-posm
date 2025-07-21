FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Set work directory
WORKDIR /app

# Copy project files
COPY pyproject.toml ./
COPY app.py ./

# Install dependencies
RUN uv pip install --system --no-cache-dir -r pyproject.toml

# Create non-root user
RUN useradd --create-home --shell /bin/bash youposm \
    && chown -R youposm:youposm /app
USER youposm

# Cloud Run automatically sets PORT environment variable
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/_stcore/health || exit 1

# Run You-POSM
CMD streamlit run app.py --server.port=${PORT:-8080} --server.address=0.0.0.0 --server.headless=true --server.enableCORS=false --server.enableXsrfProtection=false
