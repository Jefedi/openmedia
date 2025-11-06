"""Routes API pour la recherche intelligente avec cache BDD"""
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from datetime import datetime

from app.db.session import get_db
from app.models.media import Movie, Series, Genre
from app.services.omdb import omdb_service
from slugify import slugify

router = APIRouter(prefix="/search", tags=["Search"])


def search_local_movies(db: Session, query: str, limit: int = 10) -> List[Movie]:
    """Rechercher des films dans la BDD locale"""
    return db.query(Movie).filter(
        or_(
            func.lower(Movie.title).contains(query.lower()),
            func.lower(Movie.original_title).contains(query.lower())
        )
    ).limit(limit).all()


def search_local_series(db: Session, query: str, limit: int = 10) -> List[Series]:
    """Rechercher des séries dans la BDD locale"""
    return db.query(Series).filter(
        or_(
            func.lower(Series.name).contains(query.lower()),
            func.lower(Series.original_name).contains(query.lower())
        )
    ).limit(limit).all()


async def import_movie_from_omdb_auto(db: Session, imdb_id: str) -> Optional[Movie]:
    """Importer automatiquement un film depuis OMDb"""
    if not omdb_service:
        return None

    # Vérifier si le film existe déjà
    existing = db.query(Movie).filter(Movie.imdb_id == imdb_id).first()
    if existing:
        return existing

    # Récupérer depuis OMDb
    omdb_data = await omdb_service.get_by_imdb_id(imdb_id, plot="full")
    if not omdb_data or omdb_data.get("Type") != "movie":
        return None

    # Créer le slug
    title = omdb_data.get("Title", "")
    slug = slugify(title)
    slug_base = slug
    counter = 1
    while db.query(Movie).filter(Movie.slug == slug).first():
        slug = f"{slug_base}-{counter}"
        counter += 1

    # Parser les données
    year = omdb_service.parse_year(omdb_data.get("Year"))
    runtime = omdb_service.parse_runtime(omdb_data.get("Runtime"))
    rating = omdb_service.parse_rating(omdb_data.get("imdbRating"))

    # Date de sortie
    release_date = None
    if omdb_data.get("Released") and omdb_data.get("Released") != "N/A":
        try:
            release_date = datetime.strptime(omdb_data["Released"], "%d %b %Y").date()
        except:
            pass

    # Créer le film
    movie = Movie(
        imdb_id=imdb_id,
        title=title,
        slug=slug,
        overview=omdb_data.get("Plot") if omdb_data.get("Plot") != "N/A" else None,
        release_date=release_date,
        year=year,
        runtime=runtime,
        original_language=omdb_data.get("Language", "").split(",")[0].strip() if omdb_data.get("Language") != "N/A" else None,
        poster_path=omdb_data.get("Poster") if omdb_data.get("Poster") != "N/A" else None,
        vote_average=rating,
        adult=omdb_data.get("Rated") == "R" or omdb_data.get("Rated") == "NC-17"
    )

    db.add(movie)
    db.flush()

    # Ajouter les genres
    genres = omdb_service.parse_genres(omdb_data.get("Genre"))
    for genre_name in genres:
        genre_slug = slugify(genre_name)
        genre = db.query(Genre).filter(Genre.slug == genre_slug).first()
        if not genre:
            genre = Genre(name=genre_name, slug=genre_slug)
            db.add(genre)
            db.flush()
        movie.genres.append(genre)

    db.commit()
    db.refresh(movie)
    return movie


async def import_series_from_omdb_auto(db: Session, imdb_id: str) -> Optional[Series]:
    """Importer automatiquement une série depuis OMDb"""
    if not omdb_service:
        return None

    # Vérifier si la série existe déjà
    existing = db.query(Series).filter(Series.imdb_id == imdb_id).first()
    if existing:
        return existing

    # Récupérer depuis OMDb
    omdb_data = await omdb_service.get_by_imdb_id(imdb_id, plot="full")
    if not omdb_data or omdb_data.get("Type") != "series":
        return None

    # Créer le slug
    name = omdb_data.get("Title", "")
    slug = slugify(name)
    slug_base = slug
    counter = 1
    while db.query(Series).filter(Series.slug == slug).first():
        slug = f"{slug_base}-{counter}"
        counter += 1

    # Parser les données
    year = omdb_service.parse_year(omdb_data.get("Year"))
    rating = omdb_service.parse_rating(omdb_data.get("imdbRating"))
    total_seasons = int(omdb_data.get("totalSeasons", 0)) if omdb_data.get("totalSeasons") != "N/A" else 0

    # Date de première diffusion
    first_air_date = None
    if omdb_data.get("Released") and omdb_data.get("Released") != "N/A":
        try:
            first_air_date = datetime.strptime(omdb_data["Released"], "%d %b %Y").date()
        except:
            pass

    # Créer la série
    series = Series(
        imdb_id=imdb_id,
        name=name,
        slug=slug,
        overview=omdb_data.get("Plot") if omdb_data.get("Plot") != "N/A" else None,
        first_air_date=first_air_date,
        year=year,
        number_of_seasons=total_seasons,
        original_language=omdb_data.get("Language", "").split(",")[0].strip() if omdb_data.get("Language") != "N/A" else None,
        poster_path=omdb_data.get("Poster") if omdb_data.get("Poster") != "N/A" else None,
        vote_average=rating,
        adult=omdb_data.get("Rated") == "R" or omdb_data.get("Rated") == "NC-17"
    )

    db.add(series)
    db.flush()

    # Ajouter les genres
    genres = omdb_service.parse_genres(omdb_data.get("Genre"))
    for genre_name in genres:
        genre_slug = slugify(genre_name)
        genre = db.query(Genre).filter(Genre.slug == genre_slug).first()
        if not genre:
            genre = Genre(name=genre_name, slug=genre_slug)
            db.add(genre)
            db.flush()
        series.genres.append(genre)

    db.commit()
    db.refresh(series)
    return series


@router.get("")
async def smart_search(
    q: str = Query(..., min_length=1, description="Terme de recherche"),
    db: Session = Depends(get_db)
):
    """
    Recherche intelligente avec cache BDD

    1. Cherche d'abord dans la BDD locale
    2. Si pas de résultats, cherche sur OMDb
    3. Importe automatiquement les résultats OMDb dans la BDD
    4. Retourne les résultats combinés

    Cela permet d'économiser les requêtes API OMDb.
    """
    results = {
        "query": q,
        "movies": [],
        "series": [],
        "from_cache": False,
        "from_omdb": False
    }

    # 1. Chercher dans la BDD locale
    local_movies = search_local_movies(db, q, limit=10)
    local_series = search_local_series(db, q, limit=10)

    if local_movies or local_series:
        # On a des résultats en cache!
        results["from_cache"] = True
        results["movies"] = [
            {
                "id": m.id,
                "title": m.title,
                "year": m.year,
                "poster_path": m.poster_path,
                "vote_average": float(m.vote_average) if m.vote_average else None,
                "overview": m.overview,
                "imdb_id": m.imdb_id,
                "type": "movie"
            }
            for m in local_movies
        ]
        results["series"] = [
            {
                "id": s.id,
                "name": s.name,
                "year": s.year,
                "poster_path": s.poster_path,
                "vote_average": float(s.vote_average) if s.vote_average else None,
                "overview": s.overview,
                "imdb_id": s.imdb_id,
                "type": "series"
            }
            for s in local_series
        ]
        return results

    # 2. Pas de résultats locaux, chercher sur OMDb
    if not omdb_service:
        results["error"] = "Service OMDb non disponible"
        return results

    omdb_results = await omdb_service.search(q, page=1)

    if not omdb_results or not omdb_results.get("Search"):
        results["message"] = "Aucun résultat trouvé"
        return results

    results["from_omdb"] = True

    # 3. Importer automatiquement chaque résultat dans la BDD
    for item in omdb_results.get("Search", [])[:10]:  # Limiter à 10 pour ne pas surcharger
        imdb_id = item.get("imdbID")
        media_type = item.get("Type")

        if media_type == "movie":
            movie = await import_movie_from_omdb_auto(db, imdb_id)
            if movie:
                results["movies"].append({
                    "id": movie.id,
                    "title": movie.title,
                    "year": movie.year,
                    "poster_path": movie.poster_path,
                    "vote_average": float(movie.vote_average) if movie.vote_average else None,
                    "overview": movie.overview,
                    "imdb_id": movie.imdb_id,
                    "type": "movie"
                })

        elif media_type == "series":
            series = await import_series_from_omdb_auto(db, imdb_id)
            if series:
                results["series"].append({
                    "id": series.id,
                    "name": series.name,
                    "year": series.year,
                    "poster_path": series.poster_path,
                    "vote_average": float(series.vote_average) if series.vote_average else None,
                    "overview": series.overview,
                    "imdb_id": series.imdb_id,
                    "type": "series"
                })

    return results
