# Architecture OpenMedia

## Vue d'ensemble

OpenMedia est construit avec une architecture microservices containerisée via Docker, favorisant la modularité, la scalabilité et la maintenabilité.

## Diagramme d'architecture

```
┌──────────────────────────────────────────────────────────────┐
│                          Internet                             │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
              ┌──────────────────┐
              │   Nginx Proxy    │
              │  (Port 80/443)   │
              │  - TLS/SSL       │
              │  - Rate Limiting │
              │  - Security      │
              └────────┬─────────┘
                       │
          ┌────────────┴────────────┐
          │                         │
          ▼                         ▼
┌──────────────────┐      ┌──────────────────┐
│   API Backend    │      │   Frontend       │
│   (FastAPI)      │      │   (Next.js)      │
│   Port 8000      │      │   Port 3000      │
└────────┬─────────┘      └──────────────────┘
         │
    ┌────┴────┬──────────┬───────────┐
    │         │          │           │
    ▼         ▼          ▼           ▼
┌────────┐ ┌─────────┐ ┌────────┐ ┌──────────┐
│  DB    │ │  Redis  │ │ Search │ │  Worker  │
│  PG15  │ │   7.x   │ │ Meili  │ │  Celery  │
└────────┘ └─────────┘ └────────┘ └──────────┘
```

## Composants

### 1. Nginx (Reverse Proxy)

**Rôle**: Point d'entrée unique pour toutes les requêtes

**Responsabilités**:
- Terminaison SSL/TLS
- Redirection HTTP → HTTPS
- Rate limiting (protection DoS)
- Headers de sécurité (HSTS, CSP, X-Frame-Options, etc.)
- Load balancing (si scaling horizontal)
- Compression gzip
- Cache des ressources statiques

**Configuration**: `nginx/nginx.conf`

### 2. API Backend (FastAPI)

**Rôle**: Cœur applicatif, logique métier et gestion des données

**Stack**:
- **Framework**: FastAPI (Python 3.11+)
- **ORM**: SQLAlchemy 2.0
- **Validation**: Pydantic v2
- **Migrations**: Alembic
- **Auth**: JWT + Argon2

**Responsabilités**:
- Endpoints REST API (CRUD)
- Authentification et autorisation
- Gestion des utilisateurs
- Business logic
- Validation des données
- Génération de documentation auto (OpenAPI)

**Structure**:
```
backend/
├── app/
│   ├── models/          # Modèles SQLAlchemy
│   ├── schemas/         # Schémas Pydantic
│   ├── routes/          # Endpoints API
│   ├── services/        # Logique métier
│   ├── utils/           # Utilitaires
│   ├── config.py        # Configuration
│   └── main.py          # Application principale
├── alembic/             # Migrations DB
├── tests/               # Tests
└── requirements.txt
```

### 3. Base de données (PostgreSQL 15)

**Rôle**: Stockage persistant des données

**Schéma principal**:
- **users**: Utilisateurs et authentification
- **api_keys**: Clés API pour accès programmatique
- **refresh_tokens**: Tokens de rafraîchissement JWT
- **movies**: Catalogue de films
- **series**: Catalogue de séries
- **seasons**: Saisons des séries
- **episodes**: Épisodes des séries
- **genres**: Genres (cinéma/TV)
- **people**: Personnes (acteurs, réalisateurs, etc.)
- **cast**: Distribution des films
- **crew**: Équipe technique des films
- **user_watchlist**: Liste de visionnage utilisateur
- **user_progress**: Progression de visionnage
- **user_ratings**: Notations utilisateur
- **user_history**: Historique de visionnage
- **platforms**: Plateformes de streaming
- **availabilities**: Disponibilité des médias sur les plateformes

**Optimisations**:
- Index sur les colonnes fréquemment interrogées
- Contraintes d'intégrité référentielle
- Support JSON pour métadonnées flexibles
- Triggers pour mise à jour automatique de `updated_at`

### 4. Cache & Queue (Redis 7)

**Rôle**: Cache en mémoire et broker de messages

**Utilisations**:
- **DB 0**: Cache applicatif (sessions, rate-limiting)
- **DB 1**: Broker Celery (queue de tâches)
- **DB 2**: Result backend Celery (résultats des tâches)

**Configuration**:
- Politique d'éviction: `allkeys-lru`
- Limite mémoire: 512 MB
- Authentification par mot de passe

### 5. Moteur de recherche (Meilisearch)

**Rôle**: Recherche full-text rapide et pertinente

**Caractéristiques**:
- Ultra-rapide (< 50ms)
- Tolérant aux fautes de frappe
- Support des synonymes
- Filtres et facettes
- Highlighting des résultats
- Ranking personnalisable

**Index**:
- **movies**: Titre, description, acteurs, réalisateurs
- **series**: Nom, description, acteurs
- **people**: Nom, biographie

**Configuration**:
- Attributs searchables
- Attributs filtrables (genre, année, rating)
- Attributs triables (popularité, date, rating)

### 6. Worker (Celery)

**Rôle**: Exécution de tâches asynchrones et planifiées

**Types de tâches**:

**Import** (`import_tasks.py`):
- Import datasets IMDb
- Import depuis TMDB API
- Import en masse

**Synchronisation** (`sync_tasks.py`):
- Sync bidirectionnelle Trakt.tv
- Mise à jour depuis APIs externes
- Mise à jour disponibilité plateformes

**Maintenance** (`maintenance_tasks.py`):
- Nettoyage tokens expirés
- Calcul des ratings moyens
- Mise à jour index de recherche
- Génération de backups
- Calcul de popularité

**Tâches planifiées** (Celery Beat):
- Quotidiennes: ratings, nettoyage
- Toutes les 6h: sync externe
- Horaires: mise à jour index

### 7. Frontend (Next.js 14)

**Rôle**: Interface utilisateur web

**Stack**:
- **Framework**: Next.js 14 (React 18)
- **Rendering**: SSR + SSG + CSR hybride
- **Styling**: TailwindCSS (recommandé)
- **State**: React Context / Zustand
- **API Client**: Axios / Fetch

**Pages principales** (à implémenter):
- Homepage (tendances, découverte)
- Recherche
- Détails film/série
- Profil utilisateur
- Watchlist
- Historique
- Paramètres

## Flux de données

### 1. Authentification utilisateur

```
User → Nginx → API → DB
                ↓
              JWT Token
                ↓
              Redis (session)
                ↓
            ← Response
```

### 2. Recherche de contenu

```
User → Nginx → API → Meilisearch
                ↓
            DB (détails complets)
                ↓
            ← Results
```

### 3. Import de données

```
Admin → API → Celery Task
                ↓
          TMDB/IMDb API
                ↓
           Parse & Transform
                ↓
        DB Insert + Meilisearch Index
                ↓
            Task Result
```

### 4. Tracking utilisateur

```
User watches episode → API
                        ↓
                   Validation
                        ↓
                  DB (user_progress)
                        ↓
                 Optional: Celery Task
                        ↓
                  Sync to Trakt
```

## Sécurité

### Couche Réseau (Nginx)
- TLS 1.2+ obligatoire
- Rate limiting par IP
- Headers de sécurité (HSTS, CSP, etc.)
- Protection XSS, CSRF, Clickjacking

### Couche Application (API)
- JWT avec expiration courte (30 min)
- Refresh tokens révoquables
- API Keys avec scopes et quotas
- Validation stricte des inputs (Pydantic)
- Hachage Argon2 pour passwords
- Protection contre brute-force

### Couche Données (DB)
- Contraintes d'intégrité
- Prepared statements (protection SQL injection)
- Isolation des transactions
- Backups automatiques chiffrés

## Scalabilité

### Scaling Horizontal

**API Backend**:
- Stateless (sessions dans Redis)
- Facilement réplicable
- Load balancing via Nginx

**Worker Celery**:
- Parallélisation native
- Ajout de workers à la demande
- Queue distribuée via Redis

**Base de données**:
- Read replicas pour lecture
- Connection pooling
- Index optimisés

### Caching Strategy

1. **Application Cache**: Redis
2. **Query Cache**: SQLAlchemy
3. **HTTP Cache**: Nginx (ressources statiques)
4. **CDN**: Cloudflare/AWS CloudFront (production)

## Monitoring & Observabilité

### Logs
- Structured logging (JSON)
- Centralisation via ELK/Loki
- Niveaux: DEBUG, INFO, WARNING, ERROR, CRITICAL

### Métriques
- Prometheus + Grafana
- Métriques applicatives (requêtes/sec, latence)
- Métriques système (CPU, RAM, disque)

### Tracing
- Sentry pour error tracking
- APM pour performance monitoring

### Health Checks
- `/health` endpoint
- Docker healthchecks
- Monitoring externe (UptimeRobot)

## Déploiement

### Environnements

1. **Development**: Docker Compose local
2. **Staging**: Docker Compose sur serveur dédié
3. **Production**: Docker Compose ou Kubernetes

### CI/CD Pipeline

```
Push → GitHub
   ↓
GitHub Actions
   ↓
Tests (pytest, jest)
   ↓
Linting (flake8, eslint)
   ↓
Build Images
   ↓
Push to Registry
   ↓
Deploy to Server
   ↓
Run Migrations
   ↓
Health Check
   ↓
✓ Success / ✗ Rollback
```

## Backup & Recovery

### Stratégie de backup

**Base de données**:
- Backup quotidien automatique (3h du matin)
- Rétention: 30 jours
- Format: pg_dump compressé + chiffré
- Stockage: Local + S3/Backblaze

**Volumes Docker**:
- Snapshot quotidien
- Rétention: 7 jours

**Configuration**:
- Versionné dans Git
- Variables sensibles dans vault (Ansible Vault, Doppler)

### Recovery

**RTO** (Recovery Time Objective): < 1 heure
**RPO** (Recovery Point Objective): < 24 heures

## Évolutions futures

### Phase 2
- Application mobile (React Native / Flutter)
- Recommandations par IA/ML
- Système de reviews et discussions
- API GraphQL en complément de REST

### Phase 3
- Scaling Kubernetes
- Multi-région
- CDN global
- Version payante (features premium)

## Ressources

- [Documentation FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [Meilisearch Docs](https://docs.meilisearch.com/)
- [Celery Docs](https://docs.celeryq.dev/)
- [Next.js Docs](https://nextjs.org/docs)
