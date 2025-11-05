# 🚀 Guide de Démarrage Rapide - OpenMedia

Ce guide vous permet de déployer OpenMedia en **5 minutes** sur n'importe quel serveur avec Docker.

## 📋 Prérequis

- **Docker** 24+ installé
- **Docker Compose** 2.20+ installé
- **4 GB RAM** minimum
- **20 GB d'espace disque**

## 🎯 Installation en 3 Étapes

### 1️⃣ Cloner le Projet

```bash
# Cloner le repository
git clone https://github.com/Jefedi/openmedia.git
cd openmedia
```

### 2️⃣ Configurer l'Environnement

```bash
# Copier le fichier d'exemple
cp .env.example .env

# Modifier les mots de passe (IMPORTANT !)
nano .env  # ou vim, vi, etc.
```

**⚠️ Mots de passe à changer obligatoirement :**

```env
POSTGRES_PASSWORD=CHANGE_ME_STRONG_PASSWORD_HERE
REDIS_PASSWORD=CHANGE_ME_REDIS_PASSWORD
MEILI_MASTER_KEY=CHANGE_ME_MEILI_MASTER_KEY
SECRET_KEY=CHANGE_ME_SECRET_KEY_64_CHARS_MIN
JWT_SECRET_KEY=CHANGE_ME_JWT_SECRET_KEY_64_CHARS_MIN
```

**💡 Générer des mots de passe sécurisés :**

```bash
# Générer SECRET_KEY et JWT_SECRET_KEY
openssl rand -hex 32

# Ou pour un mot de passe simple
openssl rand -base64 24
```

### 3️⃣ Déployer avec le Script Automatique

```bash
# Rendre le script exécutable
chmod +x deploy.sh

# Lancer le déploiement
./deploy.sh
```

Le script va :
1. 🧹 Nettoyer les anciens conteneurs Docker
2. 🔨 Construire les images
3. 🚀 Démarrer tous les services
4. ✅ Vérifier que tout fonctionne

## 🌐 Accès aux Services

Une fois déployé, accédez aux services :

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:13000 | Interface utilisateur |
| **API** | http://localhost:18000 | API REST |
| **API Docs** | http://localhost:18000/docs | Documentation Swagger |
| **Database** | localhost:15432 | PostgreSQL |
| **Redis** | localhost:16379 | Cache Redis |
| **Meilisearch** | http://localhost:17700 | Moteur de recherche |

## 🔧 Configuration Post-Installation

### Initialiser la Base de Données

```bash
# Appliquer les migrations
docker compose exec api alembic upgrade head
```

### Créer un Utilisateur Admin

```bash
# Créer le premier utilisateur administrateur
docker compose exec api python scripts/create_admin.py
```

Vous serez invité à entrer :
- Email de l'admin
- Mot de passe
- Nom d'utilisateur

### Importer des Données (Optionnel)

```bash
# Importer les datasets IMDb
docker compose exec worker python scripts/import_imdb.py

# Importer depuis TMDB
docker compose exec worker python scripts/import_tmdb.py
```

## 📊 Gestion des Services

### Voir les Logs

```bash
# Tous les services
docker compose logs -f

# Un service spécifique
docker compose logs -f api
docker compose logs -f frontend
docker compose logs -f worker
```

### Arrêter les Services

```bash
# Arrêter sans supprimer les données
docker compose stop

# Arrêter et supprimer les conteneurs (garde les volumes)
docker compose down

# Arrêter et TOUT supprimer (⚠️ perte de données)
docker compose down -v
```

### Redémarrer un Service

```bash
# Redémarrer l'API
docker compose restart api

# Redémarrer tous les services
docker compose restart
```

### Reconstruire après Modification du Code

```bash
# Reconstruire l'API
docker compose up -d --build api

# Reconstruire tout
docker compose up -d --build
```

## 🐛 Résolution de Problèmes

### Les ports sont déjà utilisés ?

Si vous avez d'autres services qui utilisent les ports par défaut, modifiez le fichier `.env` :

```env
POSTGRES_PORT=25432   # Au lieu de 15432
REDIS_PORT=26379      # Au lieu de 16379
MEILI_PORT=27700      # Au lieu de 17700
API_PORT=28000        # Au lieu de 18000
FRONTEND_PORT=23000   # Au lieu de 13000
```

Puis redémarrez :

```bash
docker compose down
docker compose up -d
```

### Les services ne démarrent pas ?

```bash
# Vérifier l'état
docker compose ps

# Voir les erreurs
docker compose logs

# Nettoyer complètement et redémarrer
./deploy.sh
```

### Réinitialiser Complètement

```bash
# ATTENTION : Cela supprime TOUTES les données !
docker compose down -v
docker system prune -af
./deploy.sh
```

## 📚 Documentation Complète

- [Architecture Détaillée](docs/ARCHITECTURE.md)
- [Configuration Docker](docs/DOCKER.md)
- [Configuration des Ports](PORTS_CONFIGURATION.md)
- [Documentation API](docs/API.md)
- [Guide de Déploiement Production](docs/DEPLOYMENT.md)

## 🆘 Support

- 🐛 [Issues GitHub](https://github.com/Jefedi/openmedia/issues)
- 💬 [Discussions](https://github.com/Jefedi/openmedia/discussions)

## 📝 Notes Importantes

### Ports Utilisés par Défaut

OpenMedia utilise des ports dans la plage **13000-18000** pour éviter les conflits avec d'autres services courants :

- `13000` : Frontend (au lieu de 3000)
- `15432` : PostgreSQL (au lieu de 5432)
- `16379` : Redis (au lieu de 6379)
- `17700` : Meilisearch (au lieu de 7700)
- `18000` : API (au lieu de 8000)

### Sécurité

⚠️ **En production** :

1. Changez TOUS les mots de passe dans `.env`
2. Configurez HTTPS avec un certificat SSL valide
3. Configurez un firewall pour limiter l'accès
4. Activez les backups automatiques
5. Consultez [docs/SECURITY.md](docs/SECURITY.md)

### Performance

Pour un serveur de production :

- **Minimum** : 4 GB RAM, 2 CPU cores
- **Recommandé** : 8 GB RAM, 4 CPU cores
- **Optimal** : 16 GB RAM, 8 CPU cores

---

**Bon déploiement ! 🎉**
