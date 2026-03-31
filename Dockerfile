FROM python:3.11-slim

# install tesseract
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    && rm -rf /var/lib/apt/lists/*

# set working directory
WORKDIR /app

# copy files
COPY . /app

# install python deps
RUN pip install --no-cache-dir -r requirements.txt

# expose port
EXPOSE 10000

# start server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]