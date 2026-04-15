FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends bash curl libnss3 libatk-bridge2.0-0 libdrm2 libxkbcommon0 libgtk-3-0 \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /tmp/requirements.txt \
    && python -m playwright install --with-deps chromium

COPY backend /app/backend
COPY README.md /app/README.md
COPY docs /app/docs

EXPOSE 8000
