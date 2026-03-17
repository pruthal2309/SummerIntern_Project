# HR & Compliance RAG System - Docker Configuration
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ /app/backend/

# Copy main entry point
COPY main.py /app/

# Copy environment file
COPY .env /app/

# Create data directories
RUN mkdir -p /app/data/raw /app/data/processed

# Expose API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run the API server
CMD ["python", "main.py", "--serve", "--host", "0.0.0.0"]
