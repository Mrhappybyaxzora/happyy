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

# Create .env file from environment variables
RUN echo "MongoUri=${MongoUri}" > .env && \
    echo "Cohere=${Cohere}" >> .env && \
    echo "HuggingFace=${HuggingFace}" >> .env && \
    echo "OpenAI=${OpenAI}" >> .env && \
    echo "Groq=${Groq}" >> .env && \
    echo "GEMINI_API_KEY=${GEMINI_API_KEY}" >> .env && \
    echo "PLAY_HT_USER_ID=${PLAY_HT_USER_ID}" >> .env && \
    echo "PLAY_HT_API_KEY=${PLAY_HT_API_KEY}" >> .env && \
    echo "ELEVENLABS_API_KEY=${ELEVENLABS_API_KEY}" >> .env && \
    chown appuser:appuser .env

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:7860/ || exit 1

# Specify the command to run your FastAPI app with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860", "--workers", "4"]
