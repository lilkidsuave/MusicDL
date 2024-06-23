# Use a base image with Python
FROM python:3.12-slim

# Set working directory in the container
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the entire project directory into the container
COPY . .

# Copy script to create or edit settings.json
COPY setup_settings.sh /app

# Run the script to generate or edit settings.json
RUN chmod +x /app/setup_settings.sh && /app/setup_settings.sh

# Specify the command to run your application
CMD ["python", "app.py"]
