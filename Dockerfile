# Use the official Python image from the Docker Hub
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /code

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/code \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create a non-root user
RUN useradd -m appuser

# Copy the requirements file into the container
COPY --chown=appuser:appuser requirements.txt .

# Install the dependencies listed in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the working directory
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:7860/ || exit 1

# Specify the command to run your FastAPI app with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860", "--workers", "4"]
