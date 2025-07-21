# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    GOOGLE_CLOUD_PROJECT=youvit-ai-chatbot

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for faster dependency management
RUN pip install --no-cache-dir uv

# Set work directory
WORKDIR /app

# Copy project files
COPY pyproject.toml ./
COPY app.py ./

# Install Python dependencies
RUN uv pip install --system --no-cache-dir -r pyproject.toml

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash youposm \
    && chown -R youposm:youposm /app

USER youposm

# Expose port (Cloud Run will set PORT env var)
EXPOSE 8080

# Health check for Cloud Run
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8080}/_stcore/health || exit 1

# Run Streamlit app
CMD streamlit run app.py \
    --server.port=${PORT:-8080} \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false