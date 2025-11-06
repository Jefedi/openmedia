#!/bin/bash

# OpenMedia - Script de Déploiement
# Ce script nettoie complètement l'environnement Docker et redémarre les services

set -e  # Arrêter en cas d'erreur

echo "🧹 Nettoyage complet de l'environnement Docker..."

# Arrêter tous les conteneurs openmedia
echo "  → Arrêt des conteneurs openmedia..."
docker ps -a | grep openmedia | awk '{print $1}' | xargs -r docker rm -f 2>/dev/null || true

# Supprimer les réseaux openmedia
echo "  → Suppression des réseaux openmedia..."
docker network ls | grep openmedia | awk '{print $1}' | xargs -r docker network rm 2>/dev/null || true

# Nettoyer les conteneurs arrêtés
echo "  → Nettoyage des conteneurs arrêtés..."
docker compose down --remove-orphans 2>/dev/null || true

echo ""
echo "✅ Nettoyage terminé !"
echo ""

# Vérifier que le fichier .env existe
if [ ! -f .env ]; then
    echo "⚠️  Fichier .env manquant !"
    echo "🔐 Génération automatique d'un fichier .env sécurisé..."
    echo ""

    # Rendre le script exécutable et l'exécuter
    chmod +x generate-env.sh
    ./generate-env.sh

    echo ""
    echo "✅ Configuration .env créée avec succès !"
    echo ""
else
    echo "✅ Fichier .env trouvé"

    # Vérifier que les variables requises sont définies
    MISSING_VARS=()

    if ! grep -q "POSTGRES_PASSWORD=.\+" .env; then
        MISSING_VARS+=("POSTGRES_PASSWORD")
    fi

    if ! grep -q "REDIS_PASSWORD=.\+" .env; then
        MISSING_VARS+=("REDIS_PASSWORD")
    fi

    if ! grep -q "MEILI_MASTER_KEY=.\+" .env; then
        MISSING_VARS+=("MEILI_MASTER_KEY")
    fi

    if ! grep -q "SECRET_KEY=.\+" .env; then
        MISSING_VARS+=("SECRET_KEY")
    fi

    if ! grep -q "JWT_SECRET_KEY=.\+" .env; then
        MISSING_VARS+=("JWT_SECRET_KEY")
    fi

    if [ ${#MISSING_VARS[@]} -gt 0 ]; then
        echo ""
        echo "⚠️  Variables manquantes ou vides dans .env:"
        for var in "${MISSING_VARS[@]}"; do
            echo "   - $var"
        done
        echo ""
        echo "🔐 Voulez-vous régénérer automatiquement le fichier .env ? (y/N)"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            mv .env .env.backup.$(date +%s)
            echo "📦 Ancien .env sauvegardé"
            chmod +x generate-env.sh
            ./generate-env.sh
        else
            echo "❌ Veuillez remplir les variables manquantes dans .env"
            exit 1
        fi
    fi
fi

echo ""
echo "🚀 Démarrage des services Docker Compose..."
echo ""

# Construction et démarrage des services
docker compose up -d --build

echo ""
echo "⏳ Attente du démarrage des services..."
sleep 10

echo ""
echo "📊 État des services :"
docker compose ps

# Vérifier si tous les services sont en cours d'exécution
UNHEALTHY=$(docker compose ps --format json | grep -c '"Health":"unhealthy"' || true)
FAILED=$(docker compose ps --format json | grep -c '"State":"exited"' || true)

if [ "$UNHEALTHY" -gt 0 ] || [ "$FAILED" -gt 0 ]; then
    echo ""
    echo "⚠️  Certains services ont des problèmes. Affichage des logs..."
    echo ""
    docker compose logs --tail=50
    echo ""
    echo "💡 Pour voir les logs en détail : docker compose logs -f [service]"
else
    echo ""
    echo "✅ Déploiement terminé avec succès !"
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
fi
