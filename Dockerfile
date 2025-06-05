# Use official Python image
FROM python:3.11-slim

# Set working directory in container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies (all in one layer to reduce image size)
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project
COPY . .

# Skip database initialization during build
# We'll initialize it when the container starts
RUN echo "Database will be initialized at startup"

# Create necessary directories
RUN mkdir -p ./personas ./uploads ./knowledge

# Expose the ports for FastAPI and Gradio
EXPOSE 8100 7860

# Copy and make the startup script executable
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Start both services
CMD ["/app/start.sh"]
