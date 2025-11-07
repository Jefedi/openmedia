#!/usr/bin/env python3
"""
Script pour trouver et ajouter les TMDB IDs aux films et séries existants

Ce script parcourt tous les films/séries sans tmdb_id et cherche leur ID
en utilisant l'API TMDB (recherche par titre + année).

Usage:
    python scripts/find_tmdb_ids.py --movies      # Seulement les films
    python scripts/find_tmdb_ids.py --series      # Seulement les séries
    python scripts/find_tmdb_ids.py --all         # Tout (par défaut)
"""
import sys
import asyncio
import argparse
from pathlib import Path
from typing import Optional

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.media import Movie, Series
from app.services.tmdb import tmdb_service


async def search_movie_tmdb_id(title: str, year: Optional[int] = None) -> Optional[int]:
    """
    Chercher le TMDB ID d'un film par son titre

    Args:
        title: Titre du film
        year: Année de sortie (optionnel, améliore la précision)

    Returns:
        TMDB ID ou None si non trouvé
    """
    try:
        params = {"query": title}
        if year:
            params["year"] = year

        result = await tmdb_service._request("/search/movie", **params)

        if result and result.get("results"):
            # Prendre le premier résultat (le plus pertinent)
            first_result = result["results"][0]
            return first_result.get("id")

        return None
    except Exception as e:
        print(f"      ❌ Erreur lors de la recherche: {e}")
        return None


async def search_series_tmdb_id(name: str, year: Optional[int] = None) -> Optional[int]:
    """
    Chercher le TMDB ID d'une série par son nom

    Args:
        name: Nom de la série
        year: Année de première diffusion (optionnel)

    Returns:
        TMDB ID ou None si non trouvé
    """
    try:
        params = {"query": name}
        if year:
            params["first_air_date_year"] = year

        result = await tmdb_service._request("/search/tv", **params)

        if result and result.get("results"):
            # Prendre le premier résultat
            first_result = result["results"][0]
            return first_result.get("id")

        return None
    except Exception as e:
        print(f"      ❌ Erreur lors de la recherche: {e}")
        return None


async def process_movies(db: Session, force: bool = False):
    """
    Trouver et ajouter les TMDB IDs pour tous les films

    Args:
        db: Session de base de données
        force: Si True, réinitialise même les films qui ont déjà un tmdb_id
    """
    if force:
        query = db.query(Movie)
    else:
        query = db.query(Movie).filter(Movie.tmdb_id.is_(None))

    movies = query.all()

    if not movies:
        print("  ✅ Tous les films ont déjà un TMDB ID")
        return

    print(f"\n🎬 Traitement de {len(movies)} films sans TMDB ID...")

    found = 0
    not_found = 0

    for i, movie in enumerate(movies, 1):
        print(f"\n[{i}/{len(movies)}] 🔍 Recherche: '{movie.title}'", end="")
        if movie.year:
            print(f" ({movie.year})", end="")
        print("...")

        # Chercher le TMDB ID
        tmdb_id = await search_movie_tmdb_id(movie.title, movie.year)

        if tmdb_id:
            movie.tmdb_id = tmdb_id
            db.commit()
            print(f"      ✅ TMDB ID trouvé: {tmdb_id}")
            found += 1
        else:
            print(f"      ⚠️  TMDB ID non trouvé")
            not_found += 1

        # Petit délai pour respecter les limites de l'API
        await asyncio.sleep(0.3)

    print(f"\n📊 Résultat films:")
    print(f"   ✅ {found} TMDB IDs trouvés")
    print(f"   ⚠️  {not_found} non trouvés")


async def process_series(db: Session, force: bool = False):
    """
    Trouver et ajouter les TMDB IDs pour toutes les séries

    Args:
        db: Session de base de données
        force: Si True, réinitialise même les séries qui ont déjà un tmdb_id
    """
    if force:
        query = db.query(Series)
    else:
        query = db.query(Series).filter(Series.tmdb_id.is_(None))

    series_list = query.all()

    if not series_list:
        print("  ✅ Toutes les séries ont déjà un TMDB ID")
        return

    print(f"\n📺 Traitement de {len(series_list)} séries sans TMDB ID...")

    found = 0
    not_found = 0

    for i, series in enumerate(series_list, 1):
        print(f"\n[{i}/{len(series_list)}] 🔍 Recherche: '{series.name}'", end="")
        if series.year:
            print(f" ({series.year})", end="")
        print("...")

        # Chercher le TMDB ID
        tmdb_id = await search_series_tmdb_id(series.name, series.year)

        if tmdb_id:
            series.tmdb_id = tmdb_id
            db.commit()
            print(f"      ✅ TMDB ID trouvé: {tmdb_id}")
            found += 1
        else:
            print(f"      ⚠️  TMDB ID non trouvé")
            not_found += 1

        # Petit délai pour respecter les limites de l'API
        await asyncio.sleep(0.3)

    print(f"\n📊 Résultat séries:")
    print(f"   ✅ {found} TMDB IDs trouvés")
    print(f"   ⚠️  {not_found} non trouvés")


async def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(description="Trouver et ajouter les TMDB IDs")
    parser.add_argument("--movies", action="store_true", help="Traiter les films")
    parser.add_argument("--series", action="store_true", help="Traiter les séries")
    parser.add_argument("--all", action="store_true", help="Traiter tout")
    parser.add_argument("--force", action="store_true", help="Réinitialiser même ceux qui ont déjà un TMDB ID")

    args = parser.parse_args()

    if not tmdb_service:
        print("❌ TMDB_API_KEY n'est pas configurée dans .env")
        print("   Obtenez une clé gratuite sur: https://www.themoviedb.org/settings/api")
        sys.exit(1)

    print("=" * 70)
    print("🔍 Recherche de TMDB IDs pour vos films et séries")
    print("=" * 70)

    db = SessionLocal()
    try:
        if args.all or (not args.movies and not args.series):
            # Traiter tout par défaut
            await process_movies(db, args.force)
            await process_series(db, args.force)
        else:
            if args.movies:
                await process_movies(db, args.force)
            if args.series:
                await process_series(db, args.force)

        print("\n" + "=" * 70)
        print("✅ Recherche terminée !")
        print("=" * 70)
        print("\n💡 Étape suivante:")
        print("   Lancez maintenant le script d'import pour ajouter cast/crew/videos:")
        print("   docker compose exec api python scripts/import_cast_crew_videos.py --all")
        print("=" * 70)

    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
