#!/bin/bash
set -e

echo "🔄 Initialisation de la base de données OpenMedia..."

# Attendre que l'API soit prête
echo "⏳ Attente du démarrage de l'API..."
sleep 5

# Vérifier que l'API est accessible
if ! docker compose exec api curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "❌ L'API n'est pas accessible. Vérifiez les logs avec: docker compose logs api"
    exit 1
fi

echo "✅ API démarrée"

# Créer la migration initiale si elle n'existe pas
if [ ! -f backend/alembic/versions/*initial*.py ]; then
    echo "📝 Création de la migration initiale..."
    docker compose exec api alembic revision --autogenerate -m "Initial migration"
else
    echo "ℹ️  Migration initiale existante"
fi

# Appliquer les migrations
echo "🔄 Application des migrations..."
docker compose exec api alembic upgrade head

echo "✅ Base de données initialisée avec succès !"

# Créer l'utilisateur admin
echo "👤 Création de l'utilisateur admin..."
docker compose exec api python -m app.initial_data

echo ""
echo "🎉 OpenMedia est prêt !"
echo ""
echo "📍 URLs d'accès:"
echo "   - Frontend: http://localhost:13000"
echo "   - API: http://localhost:18000"
echo "   - API Docs: http://localhost:18000/docs"
echo "   - Meilisearch: http://localhost:17700"
echo ""
