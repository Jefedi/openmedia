# Guide de démarrage rapide OpenMedia

Ce guide vous permet de lancer OpenMedia en quelques minutes.

## Prérequis

- **Docker** 24+ ([Installation](https://docs.docker.com/engine/install/))
- **Docker Compose** 2.20+ (inclus avec Docker Desktop)
- **4 GB RAM** minimum (8 GB recommandé)
- **20 GB** d'espace disque libre

## Installation en 5 étapes

### 1. Cloner le repository

```bash
git clone https://github.com/Jefedi/openmedia.git
cd openmedia
```

### 2. Configurer l'environnement

```bash
# Copier le template de configuration
cp .env.example .env

# Éditer le fichier .env et changer les valeurs suivantes
nano .env
```

**⚠️ OBLIGATOIRE** - Changez ces valeurs:

```env
# Générer des secrets forts
POSTGRES_PASSWORD=<générer_un_mot_de_passe_fort>
REDIS_PASSWORD=<générer_un_mot_de_passe_fort>
MEILI_MASTER_KEY=<générer_une_clé_forte>

# Générer des clés secrètes (32+ caractères)
SECRET_KEY=<openssl rand -hex 32>
JWT_SECRET_KEY=<openssl rand -hex 32>  # Différent de SECRET_KEY
```

**Générer des secrets forts rapidement**:

```bash
# Sur Linux/Mac
echo "POSTGRES_PASSWORD=$(openssl rand -base64 32)"
echo "REDIS_PASSWORD=$(openssl rand -base64 32)"
echo "MEILI_MASTER_KEY=$(openssl rand -base64 32)"
echo "SECRET_KEY=$(openssl rand -hex 32)"
echo "JWT_SECRET_KEY=$(openssl rand -hex 32)"
```

### 3. Démarrer les services

```bash
# Lancer tous les conteneurs en arrière-plan
docker-compose up -d

# Vérifier que tous les services sont démarrés
docker-compose ps
```

Vous devriez voir 8 conteneurs en état "healthy" ou "running":
- openmedia_db
- openmedia_redis
- openmedia_search
- openmedia_api
- openmedia_worker
- openmedia_beat
- openmedia_frontend
- openmedia_nginx

### 4. Initialiser la base de données

```bash
# Exécuter les migrations
docker-compose exec api alembic upgrade head

# Vérifier que les tables sont créées
docker-compose exec db psql -U openmedia -d openmedia -c "\dt"
```

### 5. Accéder à l'application

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | Interface utilisateur |
| **API** | http://localhost:8000 | API Backend |
| **API Docs** | http://localhost:8000/api/v1/docs | Documentation interactive (Swagger) |
| **Meilisearch** | http://localhost:7700 | Dashboard de recherche |

## Créer un utilisateur admin

```bash
# Méthode 1: Via un script Python (à créer)
docker-compose exec api python scripts/create_admin.py

# Méthode 2: Via l'API directement
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@openmedia.local",
    "username": "admin",
    "password": "ChangeMe123!",
    "full_name": "Administrator"
  }'
```

## Importer des données de test

```bash
# Importer quelques films depuis TMDB (nécessite TMDB_API_KEY dans .env)
docker-compose exec worker python -c "
from tasks.import_tasks import import_tmdb_movie
# IDs TMDB de films populaires
movie_ids = [550, 680, 155, 13, 24428]  # Fight Club, Pulp Fiction, etc.
for movie_id in movie_ids:
    import_tmdb_movie.delay(movie_id)
"

# Vérifier l'import via l'API
curl http://localhost:8000/api/v1/movies | jq
```

## Commandes utiles

### Gestion des conteneurs

```bash
# Voir les logs en temps réel
docker-compose logs -f api

# Voir les logs d'un service spécifique
docker-compose logs -f worker

# Redémarrer un service
docker-compose restart api

# Arrêter tous les services
docker-compose down

# Arrêter et supprimer les volumes (⚠️ perte de données)
docker-compose down -v
```

### Base de données

```bash
# Accéder au shell PostgreSQL
docker-compose exec db psql -U openmedia -d openmedia

# Créer une migration Alembic
docker-compose exec api alembic revision --autogenerate -m "Description"

# Appliquer les migrations
docker-compose exec api alembic upgrade head

# Revenir à la migration précédente
docker-compose exec api alembic downgrade -1

# Voir l'historique des migrations
docker-compose exec api alembic history
```

### Worker Celery

```bash
# Voir les tâches actives
docker-compose exec worker celery -A tasks.celery_app inspect active

# Voir les tâches enregistrées
docker-compose exec worker celery -A tasks.celery_app inspect registered

# Voir les statistiques
docker-compose exec worker celery -A tasks.celery_app inspect stats

# Purger toutes les tâches en attente
docker-compose exec worker celery -A tasks.celery_app purge
```

### Redis

```bash
# Accéder au CLI Redis
docker-compose exec redis redis-cli -a ${REDIS_PASSWORD}

# Voir toutes les clés
docker-compose exec redis redis-cli -a ${REDIS_PASSWORD} KEYS "*"

# Voir les infos Redis
docker-compose exec redis redis-cli -a ${REDIS_PASSWORD} INFO
```

### Meilisearch

```bash
# Voir les index
curl -H "Authorization: Bearer ${MEILI_MASTER_KEY}" \
  http://localhost:7700/indexes

# Rechercher des films
curl -H "Authorization: Bearer ${MEILI_MASTER_KEY}" \
  -X POST http://localhost:7700/indexes/movies/search \
  -H "Content-Type: application/json" \
  -d '{"q": "inception"}'
```

## Tests

```bash
# Tests unitaires backend
docker-compose exec api pytest

# Tests avec coverage
docker-compose exec api pytest --cov=app --cov-report=html

# Tests d'intégration
docker-compose exec api pytest tests/integration/

# Tests frontend (à implémenter)
docker-compose exec frontend npm test
```

## Debugging

### L'API ne démarre pas

```bash
# Vérifier les logs
docker-compose logs api

# Vérifier que la DB est prête
docker-compose exec db pg_isready -U openmedia

# Vérifier que Redis est accessible
docker-compose exec redis redis-cli -a ${REDIS_PASSWORD} PING
```

### Problèmes de connexion

```bash
# Vérifier que tous les services sont sur le même réseau
docker network inspect openmedia_openmedia_network

# Vérifier les ports exposés
docker-compose ps

# Tester la connectivité entre conteneurs
docker-compose exec api ping db
docker-compose exec api ping redis
```

### Permissions Docker

```bash
# Sur Linux, ajouter votre utilisateur au groupe docker
sudo usermod -aG docker $USER
# Puis se reconnecter
```

## Mode développement

Pour le développement, vous pouvez monter les volumes en mode hot-reload:

```bash
# Éditer docker-compose.yml pour activer le hot-reload
# Les volumes sont déjà configurés pour le dev

# Redémarrer avec auto-reload
docker-compose restart api frontend
```

Les changements dans `backend/app/` et `frontend/src/` seront automatiquement détectés.

## Performances

### Optimisations recommandées

1. **Augmenter les resources Docker**
   - Docker Desktop → Settings → Resources
   - Allouer au moins 4 GB RAM, 2 CPU cores

2. **Utiliser des volumes nommés** (déjà configuré)
   - Plus rapides que bind mounts sur Windows/Mac

3. **Limiter les logs**
   ```bash
   # Ajouter dans docker-compose.yml pour chaque service
   logging:
     driver: "json-file"
     options:
       max-size: "10m"
       max-file: "3"
   ```

## Prochaines étapes

1. ✅ Configurer votre profil utilisateur
2. ✅ Importer votre première collection de films
3. ✅ Explorer la documentation API
4. ✅ Contribuer au projet (voir [CONTRIBUTING.md](CONTRIBUTING.md))

## Besoin d'aide ?

- 📚 [Documentation complète](docs/)
- 🐛 [Signaler un bug](https://github.com/Jefedi/openmedia/issues)
- 💬 [Discussions](https://github.com/Jefedi/openmedia/discussions)
- 📧 Contact: support@openmedia.example

## Arrêt de l'application

```bash
# Arrêter tous les services (données préservées)
docker-compose down

# Arrêter et supprimer les volumes (⚠️ PERTE DE DONNÉES)
docker-compose down -v

# Arrêter et supprimer les images
docker-compose down --rmi all
```

---

**Bon développement avec OpenMedia ! 🎬**
