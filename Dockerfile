# Use the official Python image from the Docker Hub
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /code

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies listed in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application code
COPY . .

# Create a default env file if it doesn't exist
RUN touch env && \
    echo "MongoUri = \"REMOVED\"" >> env && \
    echo "Cohere = \"REMOVED \"" >> env && \
    echo "HuggingFace = \"REMOVED\"" >> env && \
    echo "OpenAI = \"REMOVED\"" >> env && \
    echo "Groq = \"REMOVED\"" >> env && \
    echo "GEMINI_API_KEY = \"REMOVED\"" >> env && \
    echo "PLAY_HT_USER_ID = \"your_play_ht_user_id\"" >> env && \
    echo "PLAY_HT_API_KEY = \"your_play_ht_api_key\"" >> env && \
    echo "ELEVENLABS_API_KEY = \"your_elevenlabs_api_key\"" >> env

# Make sure the env file is readable
RUN chmod 644 env

# Specify the command to run your FastAPI app with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
