# Guide Docker Compose OpenMedia

Ce document explique les différentes configurations Docker Compose disponibles pour OpenMedia.

## 📁 Fichiers disponibles

```
.
├── docker-compose.yml              # Configuration DÉVELOPPEMENT (par défaut)
├── docker-compose.prod.yml         # Configuration PRODUCTION
└── docker-compose.override.yml.example  # Template personnalisation locale
```

## 🛠️ Environnements

### Développement (par défaut)

**Fichier**: `docker-compose.yml`

**Utilisation**:
```bash
# Démarrage simple
docker-compose up -d

# Équivalent à
docker-compose -f docker-compose.yml up -d
```

**Caractéristiques**:
- ✅ **Hot-reload** activé (API et Frontend)
- ✅ Volumes montés pour le code source
- ✅ Logs en mode debug
- ✅ Ports exposés directement (sans Nginx)
- ✅ Concurrence Celery réduite (2 workers)
- ✅ Mémoire Redis réduite (256 MB)
- ⚠️ Pas de TLS/HTTPS
- ⚠️ Secrets moins stricts

**Services**:
- PostgreSQL (port 5432)
- Redis (port 6379)
- Meilisearch (port 7700)
- API FastAPI (port 8000) - mode reload
- Celery Worker (2 workers)
- Celery Beat
- Frontend Next.js (port 3000) - mode dev

**Avantages**:
- Démarrage rapide
- Modifications de code instantanément visibles
- Debugging facile
- Logs détaillés

### Production

**Fichier**: `docker-compose.prod.yml`

**Utilisation**:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

**Caractéristiques**:
- ✅ **Optimisé** pour la performance
- ✅ Nginx comme reverse proxy
- ✅ TLS/HTTPS activé
- ✅ Security headers
- ✅ Rate limiting
- ✅ Multi-workers (API: 4, Celery: 4)
- ✅ Mémoire Redis optimisée (512 MB)
- ✅ Build optimisés (multi-stage)
- ✅ Health checks stricts

**Services**:
- PostgreSQL
- Redis
- Meilisearch
- API FastAPI (4 workers uvicorn)
- Celery Worker (4 workers)
- Celery Beat
- Frontend Next.js (build production)
- **Nginx** (ports 80/443)

**Avantages**:
- Haute performance
- Sécurisé
- Scalable
- Production-ready

## 🎯 Personnalisation locale

### Créer un fichier override

```bash
cp docker-compose.override.yml.example docker-compose.override.yml
```

Le fichier `docker-compose.override.yml` sera automatiquement utilisé par Docker Compose et **ne sera pas commité** (dans .gitignore).

### Exemples de personnalisation

#### 1. Changer les ports

```yaml
# docker-compose.override.yml
version: '3.9'

services:
  api:
    ports:
      - "8001:8000"  # API sur port 8001 au lieu de 8000

  frontend:
    ports:
      - "3001:3000"  # Frontend sur port 3001
```

#### 2. Ajouter Adminer (DB manager)

```yaml
services:
  adminer:
    image: adminer:latest
    container_name: openmedia_adminer
    ports:
      - "8080:8080"
    environment:
      ADMINER_DEFAULT_SERVER: db
    depends_on:
      - db
    networks:
      - openmedia_network
```

Accès: http://localhost:8080

#### 3. Ajouter Redis Commander

```yaml
services:
  redis-commander:
    image: rediscommander/redis-commander:latest
    container_name: openmedia_redis_commander
    ports:
      - "8081:8081"
    environment:
      REDIS_HOSTS: local:redis:6379:0:${REDIS_PASSWORD}
    depends_on:
      - redis
    networks:
      - openmedia_network
```

Accès: http://localhost:8081

#### 4. Monter des volumes locaux

```yaml
services:
  api:
    volumes:
      - ./custom-data:/app/data
      - ./local-backups:/backups
```

#### 5. Augmenter les ressources

```yaml
services:
  redis:
    command: >
      redis-server
      --requirepass ${REDIS_PASSWORD}
      --maxmemory 1gb
      --maxmemory-policy allkeys-lru

  worker:
    command: celery -A tasks.celery_app worker --loglevel=info --concurrency=8
```

## 🚀 Commandes utiles

### Démarrage

```bash
# Développement
docker-compose up -d

# Production
docker-compose -f docker-compose.prod.yml up -d

# Avec rebuild des images
docker-compose up -d --build

# Voir les logs
docker-compose logs -f

# Logs d'un service spécifique
docker-compose logs -f api
```

### Arrêt

```bash
# Arrêter les services
docker-compose down

# Arrêter et supprimer les volumes (⚠️ PERTE DE DONNÉES)
docker-compose down -v

# Arrêter et supprimer les images
docker-compose down --rmi all
```

### Gestion des services

```bash
# Redémarrer un service
docker-compose restart api

# Reconstruire un service
docker-compose up -d --build api

# Voir l'état des services
docker-compose ps

# Voir les ressources utilisées
docker stats
```

### Accès aux conteneurs

```bash
# Shell dans l'API
docker-compose exec api bash

# Shell PostgreSQL
docker-compose exec db psql -U openmedia -d openmedia

# Shell Redis
docker-compose exec redis redis-cli -a ${REDIS_PASSWORD}

# Python shell dans l'API
docker-compose exec api python
```

### Debugging

```bash
# Voir les logs en temps réel
docker-compose logs -f

# Voir les dernières lignes de logs
docker-compose logs --tail=100

# Voir les logs avec timestamps
docker-compose logs -f --timestamps

# Inspecter un service
docker-compose exec api env

# Vérifier la santé
docker-compose ps
```

## 📊 Comparaison des configurations

| Feature | Développement | Production |
|---------|--------------|------------|
| **Hot-reload** | ✅ Oui | ❌ Non |
| **Volumes montés** | ✅ Code source | ❌ Build only |
| **Nginx** | ❌ Non | ✅ Oui |
| **HTTPS** | ❌ Non | ✅ Oui |
| **Workers API** | 1 (reload) | 4 |
| **Workers Celery** | 2 | 4 |
| **Redis Memory** | 256 MB | 512 MB |
| **Log Level** | DEBUG | INFO |
| **Build** | Simple | Multi-stage |
| **Performance** | ⚡ Moyen | ⚡⚡⚡ Élevé |
| **Sécurité** | ⚠️ Basique | 🔒 Forte |

## 🔧 Variables d'environnement

Toutes les variables sont définies dans `.env`:

```bash
# Copier le template
cp .env.example .env

# Éditer les valeurs
nano .env
```

### Variables essentielles

```env
# Base de données
POSTGRES_PASSWORD=changeme

# Redis
REDIS_PASSWORD=changeme

# Meilisearch
MEILI_MASTER_KEY=changeme

# Sécurité API
SECRET_KEY=changeme
JWT_SECRET_KEY=changeme
```

### Générer des secrets

```bash
# Méthode 1: Script fourni
bash scripts/generate_secrets.sh

# Méthode 2: Manuellement
openssl rand -hex 32
```

## 🐳 Multi-fichiers compose

Vous pouvez combiner plusieurs fichiers:

```bash
# Dev + Override
docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d

# Prod + Custom
docker-compose -f docker-compose.prod.yml -f docker-compose.custom.yml up -d
```

L'ordre est important : les fichiers suivants écrasent les précédents.

## 📦 Volumes

### Volumes nommés (données persistantes)

```bash
# Lister les volumes
docker volume ls | grep openmedia

# Inspecter un volume
docker volume inspect openmedia_postgres_data

# Sauvegarder un volume
docker run --rm -v openmedia_postgres_data:/data -v $(pwd):/backup alpine \
  tar czf /backup/postgres_backup.tar.gz /data

# Restaurer un volume
docker run --rm -v openmedia_postgres_data:/data -v $(pwd):/backup alpine \
  tar xzf /backup/postgres_backup.tar.gz -C /
```

### Volumes bind (développement)

En mode dev, le code source est monté:

```yaml
volumes:
  - ./backend/app:/app/app:ro  # Read-only
  - ./frontend/src:/app/src    # Read-write
```

## 🔒 Sécurité

### Développement

- Ports exposés directement
- Secrets moins stricts
- Logs détaillés
- ⚠️ **NE PAS UTILISER EN PRODUCTION**

### Production

- Tout passe par Nginx (TLS)
- Secrets forts obligatoires
- Rate limiting
- Security headers
- Logs INFO minimum

## 🆘 Troubleshooting

### Les services ne démarrent pas

```bash
# Vérifier les logs
docker-compose logs

# Vérifier les health checks
docker-compose ps

# Reconstruire from scratch
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### Port déjà utilisé

```bash
# Trouver le processus
sudo lsof -i :8000

# Ou changer le port dans .env
API_PORT=8001
```

### Problèmes de permissions

```bash
# Sur Linux, vérifier les permissions des volumes
sudo chown -R $USER:$USER ./backend ./frontend

# Ou dans docker-compose.override.yml
services:
  api:
    user: "${UID}:${GID}"
```

### Base de données corrompue

```bash
# Arrêter tout
docker-compose down

# Supprimer le volume
docker volume rm openmedia_postgres_data

# Redémarrer
docker-compose up -d

# Réinitialiser
docker-compose exec api alembic upgrade head
```

## 📚 Ressources

- [Documentation Docker Compose](https://docs.docker.com/compose/)
- [Best practices Docker](https://docs.docker.com/develop/dev-best-practices/)
- [Compose file reference](https://docs.docker.com/compose/compose-file/)
