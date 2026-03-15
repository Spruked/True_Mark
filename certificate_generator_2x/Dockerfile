# TrueMark Enterprise Certificate Forge v2.0
# Dockerfile for production deployment

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for PIL and ReportLab
RUN apt-get update && apt-get install -y \
    gcc \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libopenjp2-7-dev \
    libtiff-dev \
    tk-dev \
    tcl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better Docker layer caching)
COPY truemark/forge_v2.0/requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY truemark/ /app/truemark/
COPY Vault_System_1.0/ /app/Vault_System_1.0/

# Create necessary directories
RUN mkdir -p /app/Vault_System_1.0/certificates/issued && \
    mkdir -p /app/Vault_System_1.0/vault_logs && \
    mkdir -p /app/Vault_System_1.0/swarm_queue && \
    mkdir -p /app/Vault_System_1.0/vault_system/skg_core/skg_data

# Set environment variables
ENV PYTHONPATH=/app
ENV VAULT_BASE_PATH=/app/Vault_System_1.0
ENV VAULT_MODE=mock

# Expose port (if adding web API in future)
EXPOSE 8000

# Default command shows help
CMD ["python", "/app/truemark/forge_v2.0/certificate_forge.py", "--help"]
