FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create instance directory for SQLite files (if needed)
RUN mkdir -p instance

# Set environment variables
ENV FLASK_APP=app.py
ENV PYTHONPATH=/app

CMD ["flask", "run", "--host=0.0.0.0"]