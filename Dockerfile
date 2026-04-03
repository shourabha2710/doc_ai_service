FROM python:3.11-slim

# ---------------- ENV ----------------
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK=True

# ---------------- SYSTEM DEPENDENCIES ----------------
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    git \
    curl \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libzbar0 \
    zbar-tools \
    && rm -rf /var/lib/apt/lists/*

# ---------------- WORKDIR ----------------
WORKDIR /app

# ---------------- COPY REQUIREMENTS ----------------
COPY requirements.txt .

# ---------------- INSTALL DEPENDENCIES ----------------
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ---------------- PRELOAD MODEL ----------------
RUN python -c "from paddleocr import PaddleOCR; PaddleOCR(use_angle_cls=True, lang='en')"

# ---------------- COPY PROJECT ----------------
COPY . .

# ---------------- PORT ----------------
EXPOSE 10000

# ---------------- START SERVER ----------------
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}"]