# OpenMedia Platform 🎬

Une plateforme open-source tout-en-un pour la gestion et le suivi de films/séries, inspirée de OMDb, Trakt.tv, TheMovieDB et JustWatch.

## 🎯 Fonctionnalités

- **Base de données complète** de films, séries, épisodes avec métadonnées riches
- **API publique REST** sécurisée par clés API avec quotas
- **Moteur de recherche** full-text rapide et tolérant aux fautes
- **Suivi utilisateur** (watchlist, progression, notations)
- **Gestion de disponibilité** (plateformes de streaming, prix)
- **Synchronisation Trakt.tv** (optionnelle)
- **Interface web moderne** et responsive
- **Architecture microservices** containerisée

## 🏗️ Architecture

### Stack Technique

- **Backend**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 15
- **Search**: Meilisearch
- **Cache/Queue**: Redis 7
- **Worker**: Celery
- **Proxy**: Nginx
- **Frontend**: Next.js 14

### Services

```
┌─────────────┐
│   Nginx     │ ← Proxy inverse, TLS, sécurité
└──────┬──────┘
       │
   ┌───┴────┐
   │        │
┌──▼──┐  ┌──▼────┐
│ API │  │ Front │
└──┬──┘  └───────┘
   │
   ├─────┬─────────┬──────────┐
   │     │         │          │
┌──▼──┐ ┌▼──────┐ ┌▼────────┐ ┌▼──────┐
│ DB  │ │ Redis │ │ Search  │ │Worker │
└─────┘ └───────┘ └─────────┘ └───────┘
```

## 🚀 Démarrage rapide

### Prérequis

- Docker 24+
- Docker Compose 2.20+
- 4 GB RAM minimum
- 20 GB espace disque

### Installation en 2 Étapes

```bash
# 1. Cloner le projet
git clone https://github.com/Jefedi/openmedia.git
cd openmedia

# 2. Déployer (génère automatiquement un .env sécurisé)
chmod +x deploy.sh
./deploy.sh
```

> 💡 **Le script `deploy.sh` génère automatiquement un fichier `.env` avec des mots de passe aléatoires sécurisés !**

**📖 [Guide de Démarrage Complet →](QUICKSTART.md)**

### Accès aux Services

Une fois déployé, les services seront accessibles :

- **Frontend** : http://localhost:13000
- **API** : http://localhost:18000
- **API Docs** : http://localhost:18000/docs

> ⚠️ **Note :** Les ports ont été changés pour éviter les conflits (13000-18000 au lieu de 3000-8000). Voir [PORTS_CONFIGURATION.md](PORTS_CONFIGURATION.md)

## 📚 Documentation

- [Architecture détaillée](docs/ARCHITECTURE.md)
- [Configuration Docker Compose](docs/DOCKER.md)
- [Configuration des ports](PORTS_CONFIGURATION.md) ← Si conflits de ports
- [Documentation API](docs/API.md)
- [Guide de contribution](docs/CONTRIBUTING.md)
- [Guide de déploiement](docs/DEPLOYMENT.md)
- [Sécurité](docs/SECURITY.md)

## 🔐 Sécurité

- Authentification JWT avec refresh tokens
- Clés API avec quotas et scopes
- Rate limiting sur tous les endpoints
- Chiffrement des mots de passe (Argon2)
- Protection CSRF, XSS, injection SQL
- Headers de sécurité HTTP
- Audit logging complet
- HTTPS obligatoire en production

## 🧪 Tests

```bash
# Tests unitaires backend
docker-compose exec api pytest

# Tests d'intégration
docker-compose exec api pytest --integration

# Coverage
docker-compose exec api pytest --cov=app --cov-report=html

# Tests frontend
docker-compose exec frontend npm test

# Linting
docker-compose exec api flake8 app/
docker-compose exec frontend npm run lint
```

## 📦 Import de données

```bash
# Importer les datasets IMDb
docker-compose exec worker python scripts/import_imdb.py

# Importer depuis TMDB
docker-compose exec worker python scripts/import_tmdb.py

# Mettre à jour l'index de recherche
docker-compose exec worker python scripts/reindex_search.py
```

## 🔧 Développement

```bash
# Logs en temps réel
docker-compose logs -f api

# Accéder au shell d'un container
docker-compose exec api bash

# Créer une nouvelle migration
docker-compose exec api alembic revision --autogenerate -m "description"

# Redémarrer un service
docker-compose restart api
```

## 🤝 Contribution

Les contributions sont les bienvenues ! Voir [CONTRIBUTING.md](docs/CONTRIBUTING.md).

### Workflow

1. Fork le projet
2. Créer une branche (`git checkout -b feature/amazing-feature`)
3. Commit (`git commit -m 'Add amazing feature'`)
4. Push (`git push origin feature/amazing-feature`)
5. Ouvrir une Pull Request

### Standards

- Tests obligatoires pour toute nouvelle fonctionnalité
- Couverture de code minimum : 80%
- Linting passant (flake8, black, isort)
- Documentation à jour
- Commit messages conventionnels

## 📄 Licence

Ce projet est sous licence **AGPL-3.0 avec restrictions commerciales**.

- ✅ Usage personnel et éducatif libre
- ✅ Contributions open-source bienvenues
- ❌ Usage commercial interdit sans autorisation
- ❌ Redistribution commerciale interdite

Voir [LICENSE](LICENSE) pour plus de détails.

## 👥 Auteurs

- **Jefedi** - Créateur et mainteneur principal

## 🙏 Remerciements

Inspiré par :
- [OMDb API](https://www.omdbapi.com/)
- [Trakt.tv](https://trakt.tv/)
- [The Movie Database](https://www.themoviedb.org/)
- [JustWatch](https://www.justwatch.com/)

## 📞 Support

- 🐛 [Issues GitHub](https://github.com/Jefedi/openmedia/issues)
- 💬 [Discussions](https://github.com/Jefedi/openmedia/discussions)
- 📧 Email: support@openmedia.example

## 🗺️ Roadmap

- [x] Architecture de base
- [ ] API CRUD complète
- [ ] Authentification et autorisation
- [ ] Import datasets IMDb
- [ ] Moteur de recherche
- [ ] Interface utilisateur
- [ ] Système de tracking utilisateur
- [ ] Synchronisation Trakt
- [ ] Gestion disponibilité plateformes
- [ ] Application mobile
- [ ] Recommandations IA

---

**Made with ❤️ by the OpenMedia community**
