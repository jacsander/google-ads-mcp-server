# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml ./
COPY ads_mcp/ ./ads_mcp/
COPY README.md ./

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Expose port (Cloud Run uses PORT environment variable)
EXPOSE 8080

# Set environment variable for port
ENV PORT=8080

# Run the HTTP server
CMD ["python", "-m", "ads_mcp.http_server"]

