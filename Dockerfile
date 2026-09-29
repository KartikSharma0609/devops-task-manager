# ---- Stage 1: build the React frontend (runs in CI, not on the EC2 host) ----
FROM node:22-alpine AS frontend

WORKDIR /frontend

COPY frontend/package.json frontend/package-lock.json ./

RUN npm ci

COPY frontend/ .

RUN npm run build

# ---- Stage 2: Flask API image ----
FROM python:3.13-slim-bookworm

LABEL org.opencontainers.image.title="DevOps Task Manager"
LABEL org.opencontainers.image.description="Flask Task Manager API"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.authors="Kartik Sharma"
LABEL org.opencontainers.image.licenses="MIT"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && \
    apt-get purge -y perl && \
    apt-get autoremove -y && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip setuptools \
    && pip install --no-cache-dir -r requirements.txt\
    && rm -rf /usr/local/lib/python*/ensurepip/_bundled/

RUN groupadd -r appgroup && \
    useradd -r -g appgroup -m -d /home/appuser -s /bin/bash appuser


COPY . .

COPY --from=frontend /frontend/dist /app/app/frontend_dist

RUN chmod +x start.sh

RUN chown -R appuser:appgroup /app

USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD curl -f http://localhost:5000/system/health || exit 1

CMD ["./start.sh"]
