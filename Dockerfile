FROM python:3.10

# ---------------- ENV ----------------
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV OMP_NUM_THREADS=1
ENV KMP_DUPLICATE_LIB_OK=TRUE

# ---------------- SYSTEM DEPENDENCIES ----------------
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    git \
    curl \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    libzbar0 \
    zbar-tools \
    && rm -rf /var/lib/apt/lists/*

# ---------------- WORKDIR ----------------
WORKDIR /app

# ---------------- COPY REQUIREMENTS ----------------
COPY requirements.txt .

# ---------------- INSTALL ----------------
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ❌ DO NOT preload model (this causes segfault in build)
# REMOVE THIS:
# RUN python -c "from paddleocr import PaddleOCR; PaddleOCR(...)"

# ---------------- COPY PROJECT ----------------
COPY . .

# ---------------- PORT ----------------
EXPOSE 10000

# ---------------- START ----------------
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]