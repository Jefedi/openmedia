# Scripts d'Import OpenMedia

Ce dossier contient des scripts utilitaires pour importer et gérer les données.

## 📥 Import Cast, Crew et Vidéos depuis TMDB

Le script `import_cast_crew_videos.py` permet d'importer automatiquement :
- 👥 **Cast** : Les acteurs avec leurs photos de profil
- 🎬 **Crew** : Réalisateurs, scénaristes, producteurs
- 🎥 **Vidéos** : Trailers, teasers, making-of depuis YouTube

### 🔑 Prérequis : Obtenir une clé API TMDB (GRATUIT)

1. Allez sur https://www.themoviedb.org/
2. Créez un compte (gratuit)
3. Allez dans **Settings** → **API** → **Create** → **Developer**
4. Remplissez le formulaire (sélectionnez "Personal" ou "Educational")
5. Copiez votre **API Key (v3 auth)**
6. Ajoutez-la dans votre fichier `.env` :
   ```bash
   TMDB_API_KEY=votre_cle_api_ici
   ```

### 📖 Utilisation

**Importer tout (films ET séries)** :
```bash
docker compose exec api python scripts/import_cast_crew_videos.py --all
```

**Importer seulement les films** :
```bash
docker compose exec api python scripts/import_cast_crew_videos.py --movies
```

**Importer seulement les séries** :
```bash
docker compose exec api python scripts/import_cast_crew_videos.py --series
```

**Forcer la réimportation (écraser les données existantes)** :
```bash
docker compose exec api python scripts/import_cast_crew_videos.py --all --force
```

### ⚙️ Comment ça fonctionne

1. Le script parcourt tous vos films/séries qui ont un `tmdb_id`
2. Pour chaque média, il récupère depuis TMDB :
   - Top 15 acteurs principaux
   - Réalisateurs/créateurs/scénaristes/producteurs
   - Jusqu'à 5 vidéos (trailers, teasers, etc.)
3. Les personnes sont créées automatiquement dans la table `people`
4. Les données sont insérées dans les tables :
   - `cast` / `series_cast`
   - `crew` / `series_crew`
   - `videos`

### ✅ Résultat

Après l'import, vos pages de détail afficheront automatiquement :
- Photos et noms des acteurs
- Informations sur les réalisateurs/créateurs
- Trailers et vidéos YouTube intégrés

### 🔄 Import Incrémental

Par défaut, le script ignore les films/séries qui ont déjà des données.

Si vous ajoutez de nouveaux films/séries plus tard, relancez simplement le script :
```bash
docker compose exec api python scripts/import_cast_crew_videos.py --all
```

Seuls les nouveaux médias sans données seront importés.

### 📊 Exemple de sortie

```
======================================================================
🚀 Import de Cast, Crew et Vidéos depuis TMDB
======================================================================

🎬 Import de cast/crew/videos pour 150 films...

[1/150]   📥 Import de 'Inception' (TMDB ID: 27205)...
    ✅ 15 acteurs et 8 crew importés
    ✅ 3 vidéos importées

[2/150]   ⏭️  Film 'The Matrix' a déjà des données, ignoré

[3/150]   📥 Import de 'Interstellar' (TMDB ID: 157336)...
    ✅ 15 acteurs et 6 crew importés
    ✅ 5 vidéos importées

...

✅ Import des films terminé !

📺 Import de cast/crew/videos pour 85 séries...

[1/85]   📥 Import de 'Breaking Bad' (TMDB ID: 1396)...
    ✅ 15 acteurs et 5 crew importés
    ✅ 4 vidéos importées

...

======================================================================
✅ Import terminé avec succès !
======================================================================
```

## 🔧 Ajout Manuel via API

Vous pouvez aussi ajouter du cast/crew/videos manuellement via les endpoints API (à venir).

## ⚠️ Limites TMDB API

TMDB offre une API gratuite avec les limites suivantes :
- **40 requêtes par 10 secondes**
- **Pas de limite quotidienne**

Le script respecte automatiquement ces limites en ajoutant un petit délai entre les requêtes si nécessaire.

## 🐛 Dépannage

**Erreur "TMDB_API_KEY not configured"** :
- Vérifiez que vous avez ajouté la clé dans `.env`
- Redémarrez les conteneurs : `docker compose restart api`

**Erreur "relation X does not exist"** :
- Assurez-vous d'avoir exécuté la migration :
  ```bash
  docker compose exec api python run_migration.py
  ```

**Aucune donnée importée** :
- Vérifiez que vos films/séries ont un `tmdb_id` dans la base de données
- Ces IDs sont normalement ajoutés automatiquement lors de l'import depuis TMDB/OMDB
