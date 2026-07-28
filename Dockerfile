FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

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
