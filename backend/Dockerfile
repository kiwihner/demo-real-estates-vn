# ─────────────────────────────────────────────────────────────────────────────
# PropVision Backend — Dockerfile
# ─────────────────────────────────────────────────────────────────────────────

FROM python:3.11-slim

# ── System dependencies ───────────────────────────────────────────────────────
# libgomp1  : OpenMP runtime — bắt buộc cho LightGBM / XGBoost multi-threading
# build-essential: cần thiết để build một số Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgomp1 \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# ── Working directory ─────────────────────────────────────────────────────────
WORKDIR /app

# ── Python dependencies ───────────────────────────────────────────────────────
# Copy requirements trước để tận dụng Docker layer cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── App source ────────────────────────────────────────────────────────────────
COPY . .

# ── pkl_models ────────────────────────────────────────────────────────────────
# KHÔNG tạo folder ở đây — dùng volume mount khi chạy container
# docker run -v ./pkl_models:/app/pkl_models ...
# hoặc khai báo trong docker-compose.yml

# ── Runtime ───────────────────────────────────────────────────────────────────
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
