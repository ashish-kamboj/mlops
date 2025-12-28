FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create output directory for data, feature_engineering, modeling, mlruns
RUN mkdir -p /output/data /output/feature_engineering /output/modeling /output/mlruns

# Copy application code
COPY app.py .

# Set environment variables for FastAPI/Uvicorn
ENV API_HOST=0.0.0.0
ENV API_PORT=5000
ENV API_WORKERS=1
ENV PYTHONUNBUFFERED=1

# Health check using curl (more reliable than Python requests)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Expose port
EXPOSE 5000

# Run FastAPI application with Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000", "--workers", "1"]