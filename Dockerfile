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

# Specify the command to run your FastAPI app with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
