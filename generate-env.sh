#!/bin/bash

# OpenMedia - Générateur de fichier .env sécurisé
# Ce script génère automatiquement un fichier .env avec des mots de passe aléatoires sécurisés

set -e

ENV_FILE=".env"

echo "🔐 Génération du fichier .env avec des mots de passe sécurisés..."

# Générer des mots de passe aléatoires
POSTGRES_PASSWORD=$(openssl rand -hex 32)
REDIS_PASSWORD=$(openssl rand -hex 32)
MEILI_MASTER_KEY=$(openssl rand -hex 32)
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)
FIRST_SUPERUSER_PASSWORD=$(openssl rand -hex 32)

# Créer le fichier .env
cat > $ENV_FILE << EOF
# OpenMedia Platform - Configuration Générée Automatiquement
# Généré le: $(date)

# =============================================================================
# GENERAL
# =============================================================================
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=debug

# =============================================================================
# POSTGRESQL DATABASE
# =============================================================================
POSTGRES_DB=openmedia
POSTGRES_USER=openmedia
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
POSTGRES_PORT=15432

# =============================================================================
# REDIS CACHE & QUEUE
# =============================================================================
REDIS_PASSWORD=${REDIS_PASSWORD}
REDIS_PORT=16379

# =============================================================================
# MEILISEARCH
# =============================================================================
MEILI_MASTER_KEY=${MEILI_MASTER_KEY}
MEILI_ENV=development
MEILI_PORT=17700

# =============================================================================
# API BACKEND
# =============================================================================
API_PORT=18000
SECRET_KEY=${SECRET_KEY}
JWT_SECRET_KEY=${JWT_SECRET_KEY}
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
BACKEND_CORS_ORIGINS=["http://localhost:13000","http://localhost:18000"]
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# =============================================================================
# FRONTEND
# =============================================================================
FRONTEND_PORT=13000
NODE_ENV=development
NEXT_PUBLIC_API_URL=http://localhost:18000
NEXT_PUBLIC_APP_NAME=OpenMedia

# =============================================================================
# VERSIONS
# =============================================================================
PYTHON_VERSION=3.11
NODE_VERSION=20

# =============================================================================
# CELERY WORKER
# =============================================================================
CELERY_LOG_LEVEL=debug
CELERY_CONCURRENCY=2

# =============================================================================
# FIRST SUPERUSER (Admin Account)
# =============================================================================
FIRST_SUPERUSER_EMAIL=admin@openmedia.local
FIRST_SUPERUSER_PASSWORD=${FIRST_SUPERUSER_PASSWORD}

# =============================================================================
# EXTERNAL APIs (Optionnel)
# =============================================================================
# TMDB_API_KEY=
# TMDB_API_READ_TOKEN=
# TRAKT_CLIENT_ID=
# TRAKT_CLIENT_SECRET=
# OMDB_API_KEY=
EOF

chmod 600 $ENV_FILE

echo "✅ Fichier .env généré avec succès !"
echo ""
echo "📝 Mots de passe générés (SAUVEGARDEZ-LES) :"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "POSTGRES_PASSWORD=${POSTGRES_PASSWORD}"
echo "REDIS_PASSWORD=${REDIS_PASSWORD}"
echo "MEILI_MASTER_KEY=${MEILI_MASTER_KEY}"
echo "SECRET_KEY=${SECRET_KEY}"
echo "JWT_SECRET_KEY=${JWT_SECRET_KEY}"
echo ""
echo "👤 ADMIN CREDENTIALS:"
echo "FIRST_SUPERUSER_EMAIL=admin@openmedia.local"
echo "FIRST_SUPERUSER_PASSWORD=${FIRST_SUPERUSER_PASSWORD}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💾 Fichier sauvegardé : $ENV_FILE"
echo "🔒 Permissions : 600 (lecture/écriture propriétaire uniquement)"
echo ""
