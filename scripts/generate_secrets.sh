#!/bin/bash
# Script pour générer des secrets forts pour OpenMedia

echo "==================================="
echo "OpenMedia - Générateur de secrets"
echo "==================================="
echo ""
echo "Copiez ces valeurs dans votre fichier .env"
echo ""

echo "# Database"
echo "POSTGRES_PASSWORD=$(openssl rand -base64 32)"
echo ""

echo "# Redis"
echo "REDIS_PASSWORD=$(openssl rand -base64 32)"
echo ""

echo "# Meilisearch"
echo "MEILI_MASTER_KEY=$(openssl rand -base64 32)"
echo ""

echo "# Security - Application Secrets"
echo "SECRET_KEY=$(openssl rand -hex 32)"
echo "JWT_SECRET_KEY=$(openssl rand -hex 32)"
echo ""

echo "==================================="
echo "⚠️  IMPORTANT:"
echo "- Ne partagez JAMAIS ces secrets"
echo "- Utilisez des valeurs différentes pour chaque environnement"
echo "- Stockez-les de manière sécurisée (vault, gestionnaire de mots de passe)"
echo "==================================="
