#!/usr/bin/env python3
"""
Script pour importer les cast, crew et videos depuis TMDB

Usage:
    python scripts/import_cast_crew_videos.py --movies      # Importer pour les films
    python scripts/import_cast_crew_videos.py --series      # Importer pour les séries
    python scripts/import_cast_crew_videos.py --all         # Importer tout
"""
import sys
import asyncio
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.media import Movie, Series, Person, Cast, Crew, SeriesCast, SeriesCrew, Video
from app.services.tmdb import tmdb_service
from slugify import slugify


def get_or_create_person(db: Session, tmdb_person_data: dict) -> Optional[Person]:
    """
    Créer ou récupérer une personne depuis les données TMDB

    Args:
        db: Session de base de données
        tmdb_person_data: Données de la personne depuis TMDB

    Returns:
        Instance Person ou None
    """
    tmdb_id = tmdb_person_data.get("id")
    if not tmdb_id:
        return None

    # Chercher si la personne existe déjà
    person = db.query(Person).filter(Person.tmdb_id == tmdb_id).first()

    if person:
        return person

    # Créer la personne
    name = tmdb_person_data.get("name")
    if not name:
        return None

    person = Person(
        name=name,
        slug=slugify(name),
        tmdb_id=tmdb_id,
        profile_path=tmdb_person_data.get("profile_path"),
        biography=None,  # On pourrait fetch les détails si nécessaire
        birthday=None,
        place_of_birth=None
    )

    db.add(person)
    db.flush()  # Pour obtenir l'ID

    return person


async def import_movie_data(db: Session, movie: Movie, skip_existing: bool = True):
    """
    Importer cast, crew et videos pour un film

    Args:
        db: Session de base de données
        movie: Instance Movie
        skip_existing: Si True, ignore les films qui ont déjà du cast/crew/videos
    """
    if not movie.tmdb_id:
        print(f"  ⚠️  Film '{movie.title}' n'a pas de TMDB ID, ignoré")
        return

    # Skip si déjà importé
    if skip_existing:
        has_data = (
            db.query(Cast).filter(Cast.movie_id == movie.id).count() > 0 or
            db.query(Crew).filter(Crew.movie_id == movie.id).count() > 0 or
            db.query(Video).filter(Video.movie_id == movie.id).count() > 0
        )
        if has_data:
            print(f"  ⏭️  Film '{movie.title}' a déjà des données, ignoré")
            return

    print(f"  📥 Import de '{movie.title}' (TMDB ID: {movie.tmdb_id})...")

    # 1. Importer le cast et crew
    credits_data = await tmdb_service.get_movie_credits(movie.tmdb_id)

    if credits_data:
        cast_list = credits_data.get("cast", [])[:15]  # Top 15 acteurs
        crew_list = credits_data.get("crew", [])

        # Filtrer le crew pour garder seulement certains rôles importants
        important_jobs = ["Director", "Writer", "Screenplay", "Producer", "Executive Producer"]
        crew_list = [c for c in crew_list if c.get("job") in important_jobs][:10]

        # Importer le cast
        for cast_data in cast_list:
            person = get_or_create_person(db, cast_data)
            if not person:
                continue

            # Vérifier si ce cast existe déjà
            existing = db.query(Cast).filter(
                Cast.movie_id == movie.id,
                Cast.person_id == person.id
            ).first()

            if not existing:
                cast_member = Cast(
                    movie_id=movie.id,
                    person_id=person.id,
                    character=cast_data.get("character"),
                    order=cast_data.get("order", 999)
                )
                db.add(cast_member)

        # Importer le crew
        for crew_data in crew_list:
            person = get_or_create_person(db, crew_data)
            if not person:
                continue

            # Vérifier si ce crew existe déjà
            existing = db.query(Crew).filter(
                Crew.movie_id == movie.id,
                Crew.person_id == person.id,
                Crew.job == crew_data.get("job")
            ).first()

            if not existing:
                crew_member = Crew(
                    movie_id=movie.id,
                    person_id=person.id,
                    job=crew_data.get("job", "Unknown"),
                    department=crew_data.get("department", "Unknown")
                )
                db.add(crew_member)

        print(f"    ✅ {len(cast_list)} acteurs et {len(crew_list)} crew importés")

    # 2. Importer les vidéos
    videos_data = await tmdb_service.get_movie_videos(movie.tmdb_id)

    if videos_data:
        video_list = videos_data.get("results", [])
        # Filtrer pour garder seulement YouTube et types importants
        video_list = [
            v for v in video_list
            if v.get("site") == "YouTube" and v.get("type") in ["Trailer", "Teaser", "Clip", "Behind the Scenes", "Featurette"]
        ][:5]  # Max 5 vidéos

        for video_data in video_list:
            # Vérifier si la vidéo existe déjà
            existing = db.query(Video).filter(
                Video.movie_id == movie.id,
                Video.key == video_data.get("key")
            ).first()

            if not existing:
                video = Video(
                    movie_id=movie.id,
                    series_id=None,
                    key=video_data.get("key"),
                    name=video_data.get("name"),
                    site=video_data.get("site", "YouTube"),
                    type=video_data.get("type"),
                    size=video_data.get("size", 1080),
                    official=video_data.get("official", True),
                    published_at=datetime.fromisoformat(video_data["published_at"].replace("Z", "+00:00")) if video_data.get("published_at") else None,
                    iso_639_1=video_data.get("iso_639_1"),
                    iso_3166_1=video_data.get("iso_3166_1")
                )
                db.add(video)

        print(f"    ✅ {len(video_list)} vidéos importées")

    db.commit()


async def import_series_data(db: Session, series: Series, skip_existing: bool = True):
    """
    Importer cast, crew et videos pour une série

    Args:
        db: Session de base de données
        series: Instance Series
        skip_existing: Si True, ignore les séries qui ont déjà du cast/crew/videos
    """
    if not series.tmdb_id:
        print(f"  ⚠️  Série '{series.name}' n'a pas de TMDB ID, ignorée")
        return

    # Skip si déjà importé
    if skip_existing:
        has_data = (
            db.query(SeriesCast).filter(SeriesCast.series_id == series.id).count() > 0 or
            db.query(SeriesCrew).filter(SeriesCrew.series_id == series.id).count() > 0 or
            db.query(Video).filter(Video.series_id == series.id).count() > 0
        )
        if has_data:
            print(f"  ⏭️  Série '{series.name}' a déjà des données, ignorée")
            return

    print(f"  📥 Import de '{series.name}' (TMDB ID: {series.tmdb_id})...")

    # 1. Importer le cast et crew
    credits_data = await tmdb_service.get_series_credits(series.tmdb_id)

    if credits_data:
        cast_list = credits_data.get("cast", [])[:15]  # Top 15 acteurs
        crew_list = credits_data.get("crew", [])

        # Filtrer le crew pour les créateurs et scénaristes principaux
        important_jobs = ["Creator", "Executive Producer", "Writer", "Producer"]
        crew_list = [c for c in crew_list if c.get("job") in important_jobs][:10]

        # Importer le cast
        for cast_data in cast_list:
            person = get_or_create_person(db, cast_data)
            if not person:
                continue

            # Vérifier si ce cast existe déjà
            existing = db.query(SeriesCast).filter(
                SeriesCast.series_id == series.id,
                SeriesCast.person_id == person.id
            ).first()

            if not existing:
                # Pour les séries, character peut être une liste de rôles
                character = cast_data.get("character") or cast_data.get("roles", [{}])[0].get("character")

                cast_member = SeriesCast(
                    series_id=series.id,
                    person_id=person.id,
                    character=character,
                    order=cast_data.get("order", 999)
                )
                db.add(cast_member)

        # Importer le crew
        for crew_data in crew_list:
            person = get_or_create_person(db, crew_data)
            if not person:
                continue

            # Vérifier si ce crew existe déjà
            existing = db.query(SeriesCrew).filter(
                SeriesCrew.series_id == series.id,
                SeriesCrew.person_id == person.id,
                SeriesCrew.job == crew_data.get("job")
            ).first()

            if not existing:
                crew_member = SeriesCrew(
                    series_id=series.id,
                    person_id=person.id,
                    job=crew_data.get("job", "Unknown"),
                    department=crew_data.get("department", "Unknown")
                )
                db.add(crew_member)

        print(f"    ✅ {len(cast_list)} acteurs et {len(crew_list)} crew importés")

    # 2. Importer les vidéos
    videos_data = await tmdb_service.get_series_videos(series.tmdb_id)

    if videos_data:
        video_list = videos_data.get("results", [])
        # Filtrer pour garder seulement YouTube et types importants
        video_list = [
            v for v in video_list
            if v.get("site") == "YouTube" and v.get("type") in ["Trailer", "Teaser", "Clip", "Behind the Scenes", "Featurette"]
        ][:5]  # Max 5 vidéos

        for video_data in video_list:
            # Vérifier si la vidéo existe déjà
            existing = db.query(Video).filter(
                Video.series_id == series.id,
                Video.key == video_data.get("key")
            ).first()

            if not existing:
                video = Video(
                    movie_id=None,
                    series_id=series.id,
                    key=video_data.get("key"),
                    name=video_data.get("name"),
                    site=video_data.get("site", "YouTube"),
                    type=video_data.get("type"),
                    size=video_data.get("size", 1080),
                    official=video_data.get("official", True),
                    published_at=datetime.fromisoformat(video_data["published_at"].replace("Z", "+00:00")) if video_data.get("published_at") else None,
                    iso_639_1=video_data.get("iso_639_1"),
                    iso_3166_1=video_data.get("iso_3166_1")
                )
                db.add(video)

        print(f"    ✅ {len(video_list)} vidéos importées")

    db.commit()


async def import_all_movies(skip_existing: bool = True):
    """Importer les données pour tous les films"""
    db = SessionLocal()
    try:
        movies = db.query(Movie).filter(Movie.tmdb_id.isnot(None)).all()
        print(f"\n🎬 Import de cast/crew/videos pour {len(movies)} films...")

        for i, movie in enumerate(movies, 1):
            print(f"\n[{i}/{len(movies)}]", end=" ")
            try:
                await import_movie_data(db, movie, skip_existing)
            except Exception as e:
                print(f"  ❌ Erreur pour '{movie.title}': {e}")
                db.rollback()

        print(f"\n✅ Import des films terminé !")

    finally:
        db.close()


async def import_all_series(skip_existing: bool = True):
    """Importer les données pour toutes les séries"""
    db = SessionLocal()
    try:
        series_list = db.query(Series).filter(Series.tmdb_id.isnot(None)).all()
        print(f"\n📺 Import de cast/crew/videos pour {len(series_list)} séries...")

        for i, series in enumerate(series_list, 1):
            print(f"\n[{i}/{len(series_list)}]", end=" ")
            try:
                await import_series_data(db, series, skip_existing)
            except Exception as e:
                print(f"  ❌ Erreur pour '{series.name}': {e}")
                db.rollback()

        print(f"\n✅ Import des séries terminé !")

    finally:
        db.close()


async def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(description="Importer cast, crew et videos depuis TMDB")
    parser.add_argument("--movies", action="store_true", help="Importer pour les films")
    parser.add_argument("--series", action="store_true", help="Importer pour les séries")
    parser.add_argument("--all", action="store_true", help="Importer tout")
    parser.add_argument("--force", action="store_true", help="Réimporter même si les données existent déjà")

    args = parser.parse_args()

    if not tmdb_service:
        print("❌ TMDB_API_KEY n'est pas configurée dans .env")
        print("   Obtenez une clé gratuite sur: https://www.themoviedb.org/settings/api")
        sys.exit(1)

    skip_existing = not args.force

    print("=" * 70)
    print("🚀 Import de Cast, Crew et Vidéos depuis TMDB")
    print("=" * 70)

    if args.all or (not args.movies and not args.series):
        # Import tout par défaut
        await import_all_movies(skip_existing)
        await import_all_series(skip_existing)
    else:
        if args.movies:
            await import_all_movies(skip_existing)
        if args.series:
            await import_all_series(skip_existing)

    print("\n" + "=" * 70)
    print("✅ Import terminé avec succès !")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
