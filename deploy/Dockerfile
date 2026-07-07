FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libcairo2 \
    libffi-dev \
    shared-mime-info \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
COPY alembic.ini ./
COPY src ./src
COPY migrations ./migrations
COPY agente ./agente
COPY docs/canon ./docs/canon
COPY scripts ./scripts
COPY static ./static
COPY audit-portal ./audit-portal

RUN pip install --no-cache-dir .

RUN AUDIT_API_BASE="" python scripts/generar_audit_portal.py

ENV PYTHONUNBUFFERED=1
EXPOSE 8000

HEALTHCHECK CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "-m", "src.main"]
