FROM python:3.11-slim

# Install Tesseract and ZBar
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    zbar-tools \
    libzbar0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 10000

# Start server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]