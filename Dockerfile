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

ENV QOBUZ_USERNAME=""
ENV QOBUZ_PASSWORD=""

RUN chmod +x /app/setup_settings.sh && /app/setup_settings.sh "$QOBUZ_USERNAME" "$QOBUZ_PASSWORD"

# Specify the command to run your application
CMD ["python", "app.py"]
