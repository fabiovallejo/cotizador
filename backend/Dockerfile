FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libgobject-2.0-0 \
    libcairo2 \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY .env .env

# Script para inicializar BD y luego ejecutar app
RUN echo '#!/bin/bash\n\
    sleep 15\n\
    export PYTHONPATH=/app\n\
    python app/db/init_db.py\n\
    uvicorn app.main:app --host 0.0.0.0 --port 8000\n\
    ' > /start.sh && chmod +x /start.sh

RUN mkdir -p /app/uploads/logos
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

CMD ["/start.sh"]