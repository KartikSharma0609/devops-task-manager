FROM python:3.13-slim

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

RUN chown -R appuser:appgroup /app

USER appuser

EXPOSE 5000

CMD [\
  "gunicorn",\
  "--bind", "0.0.0.0:5000",\
  "--workers", "2",\
  "--threads", "2",\
  "--timeout", "60",\
  "--access-logfile", "-",\
  "--error-logfile", "-",\
  "app:create_app()"\
]
