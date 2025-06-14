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
    echo "MongoUri = \"${MONGO_URI}\"" >> env && \
    echo "Cohere = \"${COHERE_API_KEY}\"" >> env && \
    echo "HuggingFace = \"${HUGGINGFACE_API_KEY}\"" >> env && \
    echo "OpenAI = \"${REMOVED}\"" >> env && \
    echo "Groq = \"${GROQ_API_KEY}\"" >> env && \
    echo "GEMINI_API_KEY = \"${GEMINI_API_KEY}\"" >> env && \
    echo "PLAY_HT_USER_ID = \"${PLAY_HT_USER_ID}\"" >> env && \
    echo "PLAY_HT_API_KEY = \"${PLAY_HT_API_KEY}\"" >> env && \
    echo "ELEVENLABS_API_KEY = \"${ELEVENLABS_API_KEY}\"" >> env

# Make sure the env file is readable
RUN chmod 644 env

# Specify the command to run your FastAPI app with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
