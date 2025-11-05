#!/bin/bash

# OpenMedia - Script de Déploiement
# Ce script nettoie complètement l'environnement Docker et redémarre les services

set -e  # Arrêter en cas d'erreur

echo "🧹 Nettoyage complet de l'environnement Docker..."

# Arrêter tous les conteneurs openmedia
echo "  → Arrêt des conteneurs openmedia..."
docker ps -a | grep openmedia | awk '{print $1}' | xargs -r docker rm -f || true

# Supprimer les réseaux openmedia
echo "  → Suppression des réseaux openmedia..."
docker network ls | grep openmedia | awk '{print $1}' | xargs -r docker network rm || true

# Nettoyer les conteneurs arrêtés
echo "  → Nettoyage des conteneurs arrêtés..."
docker compose down --remove-orphans 2>/dev/null || true

echo ""
echo "✅ Nettoyage terminé !"
echo ""

# Vérifier que le fichier .env existe
if [ ! -f .env ]; then
    echo "⚠️  Fichier .env manquant !"
    echo "📝 Création du fichier .env à partir de .env.example..."
    cp .env.example .env

    echo ""
    echo "⚠️  IMPORTANT: Modifiez le fichier .env et changez les mots de passe !"
    echo ""
    echo "Fichiers à modifier :"
    echo "  - POSTGRES_PASSWORD"
    echo "  - REDIS_PASSWORD"
    echo "  - MEILI_MASTER_KEY"
    echo "  - SECRET_KEY"
    echo "  - JWT_SECRET_KEY"
    echo ""
    read -p "Appuyez sur Entrée après avoir modifié .env, ou Ctrl+C pour annuler..."
fi

echo "🚀 Démarrage des services Docker Compose..."
echo ""

# Construction et démarrage des services
docker compose up -d --build

echo ""
echo "⏳ Attente du démarrage des services..."
sleep 5

echo ""
echo "📊 État des services :"
docker compose ps

echo ""
echo "✅ Déploiement terminé !"
echo ""
echo "🌐 Accès aux services :"
echo "  - Frontend:    http://localhost:13000"
echo "  - API:         http://localhost:18000"
echo "  - API Docs:    http://localhost:18000/docs"
echo "  - Database:    localhost:15432"
echo "  - Redis:       localhost:16379"
echo "  - Meilisearch: http://localhost:17700"
echo ""
echo "📝 Prochaines étapes :"
echo "  1. Initialiser la base de données:"
echo "     docker compose exec api alembic upgrade head"
echo ""
echo "  2. Créer un utilisateur admin:"
echo "     docker compose exec api python scripts/create_admin.py"
echo ""
echo "  3. Voir les logs:"
echo "     docker compose logs -f"
echo ""
