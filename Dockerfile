FROM python:3.11-slim

# Install Tesseract and ZBar with Hindi and English
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-hin \
    libtesseract-dev \
    zbar-tools \
    libzbar0 \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app
COPY . /app

# Upgrade pip
RUN python -m pip install --upgrade pip

# Install dependencies including PaddlePaddle CPU version
RUN pip install --no-cache-dir paddlepaddle==2.7.2 \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir paddleocr==3.4.0

# Expose port
EXPOSE 10000

# Start FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]