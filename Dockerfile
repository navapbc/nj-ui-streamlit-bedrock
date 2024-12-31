# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Create a working directory inside the container
WORKDIR /app

# Copy the requirements.txt file first for efficient Docker layer caching
COPY requirements.txt .

# Install required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy your source code into the container
COPY . .

# Expose the port that Streamlit will run on (default is 8501)
EXPOSE 8501

ENV AWS_PROFILE=chris_llm

# The command that starts your Streamlit application
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
