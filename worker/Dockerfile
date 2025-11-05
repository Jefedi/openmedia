# OpenMedia Worker Dockerfile
ARG PYTHON_VERSION=3.11

FROM python:${PYTHON_VERSION}-slim as base

# Configuration de l'environnement Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    C_FORCE_ROOT=true

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Créer utilisateur non-root pour sécurité
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Copier les requirements et installer les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application
COPY --chown=appuser:appuser . .

# Créer les répertoires nécessaires
RUN mkdir -p /app/logs /app/data && chown -R appuser:appuser /app

# Passer à l'utilisateur non-root
USER appuser

# Commande par défaut (sera overridée dans docker-compose)
CMD ["celery", "-A", "tasks.celery_app", "worker", "--loglevel=info"]
