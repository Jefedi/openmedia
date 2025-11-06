"""Routes API pour les films"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.session import get_db
from app.models.media import Movie, Genre, movie_genres
from app.models.user import User
from app.schemas.media import (
    MovieResponse,
    MovieCreate,
    MovieUpdate,
    MovieListResponse,
    OMDbSearchResponse,
    OMDbDetailResponse
)
from app.routes.auth import get_current_user
from app.services.omdb import omdb_service

router = APIRouter(prefix="/movies", tags=["Movies"])


# ============================================================================
# CRUD OPERATIONS
# ============================================================================

@router.get("", response_model=MovieListResponse)
async def list_movies(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    genre: Optional[str] = None,
    year: Optional[int] = None,
    sort_by: str = Query("created_at", regex="^(title|release_date|vote_average|popularity|created_at)$"),
    order: str = Query("desc", regex="^(asc|desc)$"),
    db: Session = Depends(get_db)
):
    """
    Liste des films avec pagination et filtres

    Args:
        page: Num�ro de page
        page_size: Nombre d'�l�ments par page
        search: Recherche par titre
        genre: Filtrer par genre (slug)
        year: Filtrer par ann�e de sortie
        sort_by: Trier par (title, release_date, vote_average, popularity, created_at)
        order: Ordre de tri (asc, desc)
    """
    query = db.query(Movie)

    # Filtrer par recherche
    if search:
        query = query.filter(
            func.lower(Movie.title).contains(search.lower())
        )

    # Filtrer par genre
    if genre:
        query = query.join(Movie.genres).filter(Genre.slug == genre)

    # Filtrer par ann�e
    if year:
        query = query.filter(Movie.year == year)

    # Compter le total
    total = query.count()

    # Tri
    sort_column = getattr(Movie, sort_by)
    if order == "desc":
        sort_column = sort_column.desc()
    else:
        sort_column = sort_column.asc()

    # Pagination
    movies = query.order_by(sort_column).offset((page - 1) * page_size).limit(page_size).all()

    return MovieListResponse(
        movies=movies,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{movie_id}", response_model=MovieResponse)
async def get_movie(
    movie_id: int,
    db: Session = Depends(get_db)
):
    """Obtenir un film par ID"""
    movie = db.query(Movie).filter(Movie.id == movie_id).first()

    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Film non trouv�"
        )

    return movie


@router.post("", response_model=MovieResponse, status_code=status.HTTP_201_CREATED)
async def create_movie(
    movie_data: MovieCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cr�er un nouveau film

    N�cessite une authentification.
    """
    # V�rifier si le film existe d�j� (par TMDB ID ou slug)
    if movie_data.tmdb_id:
        existing = db.query(Movie).filter(Movie.tmdb_id == movie_data.tmdb_id).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Un film avec cet ID TMDB existe d�j�"
            )

    existing_slug = db.query(Movie).filter(Movie.slug == movie_data.slug).first()
    if existing_slug:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un film avec ce slug existe d�j�"
        )

    # Cr�er le film
    movie = Movie(**movie_data.model_dump())
    db.add(movie)
    db.commit()
    db.refresh(movie)

    return movie


@router.put("/{movie_id}", response_model=MovieResponse)
async def update_movie(
    movie_id: int,
    movie_data: MovieUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mettre � jour un film

    N�cessite une authentification.
    """
    movie = db.query(Movie).filter(Movie.id == movie_id).first()

    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Film non trouv�"
        )

    # Mettre � jour les champs fournis
    for field, value in movie_data.model_dump(exclude_unset=True).items():
        setattr(movie, field, value)

    db.commit()
    db.refresh(movie)

    return movie


@router.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_movie(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Supprimer un film

    N�cessite une authentification et les droits admin.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas les droits pour supprimer des films"
        )

    movie = db.query(Movie).filter(Movie.id == movie_id).first()

    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Film non trouv�"
        )

    db.delete(movie)
    db.commit()


# ============================================================================
# TMDB INTEGRATION
# ============================================================================

@router.get("/tmdb/search", response_model=TMDBSearchResponse)
async def search_movies_tmdb(
    query: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    year: Optional[int] = None,
    language: str = Query("fr-FR")
):
    """
    Rechercher des films sur TMDB

    Args:
        query: Terme de recherche
        page: Num�ro de page
        year: Ann�e de sortie (optionnel)
        language: Code de langue
    """
    if not tmdb_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service TMDB non disponible. V�rifiez la configuration TMDB_API_KEY."
        )

    results = await tmdb_service.search_movie(
        query=query,
        page=page,
        year=year,
        language=language
    )

    if not results:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la recherche TMDB"
        )

    return TMDBSearchResponse(
        results=results.get("results", []),
        total_results=results.get("total_results", 0),
        page=results.get("page", 1),
        total_pages=results.get("total_pages", 0)
    )


@router.get("/tmdb/popular", response_model=TMDBSearchResponse)
async def get_popular_movies_tmdb(
    page: int = Query(1, ge=1),
    language: str = Query("fr-FR")
):
    """Obtenir les films populaires depuis TMDB"""
    if not tmdb_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service TMDB non disponible"
        )

    results = await tmdb_service.get_popular_movies(page=page, language=language)

    if not results:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la r�cup�ration des films populaires"
        )

    return TMDBSearchResponse(
        results=results.get("results", []),
        total_results=results.get("total_results", 0),
        page=results.get("page", 1),
        total_pages=results.get("total_pages", 0)
    )


@router.get("/tmdb/{tmdb_id}")
async def get_movie_from_tmdb(
    tmdb_id: int,
    language: str = Query("fr-FR")
):
    """Obtenir les d�tails d'un film depuis TMDB"""
    if not tmdb_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service TMDB non disponible"
        )

    movie = await tmdb_service.get_movie_details(tmdb_id, language=language)

    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Film non trouv� sur TMDB"
        )

    return movie


@router.post("/tmdb/{tmdb_id}/import", response_model=MovieResponse)
async def import_movie_from_tmdb(
    tmdb_id: int,
    language: str = Query("fr-FR"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Importer un film depuis TMDB

    R�cup�re les informations du film depuis TMDB et le cr�e dans la base de donn�es.
    """
    if not tmdb_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service TMDB non disponible"
        )

    # V�rifier si le film existe d�j�
    existing = db.query(Movie).filter(Movie.tmdb_id == tmdb_id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce film existe d�j� dans la base de donn�es"
        )

    # R�cup�rer les d�tails depuis TMDB
    tmdb_data = await tmdb_service.get_movie_details(tmdb_id, language=language)

    if not tmdb_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Film non trouv� sur TMDB"
        )

    # Cr�er le slug
    from slugify import slugify
    slug = slugify(tmdb_data.get("title", ""))

    # V�rifier l'unicit� du slug
    slug_base = slug
    counter = 1
    while db.query(Movie).filter(Movie.slug == slug).first():
        slug = f"{slug_base}-{counter}"
        counter += 1

    # Cr�er le film
    movie = Movie(
        tmdb_id=tmdb_id,
        imdb_id=tmdb_data.get("external_ids", {}).get("imdb_id"),
        title=tmdb_data.get("title"),
        original_title=tmdb_data.get("original_title"),
        slug=slug,
        overview=tmdb_data.get("overview"),
        tagline=tmdb_data.get("tagline"),
        release_date=tmdb_data.get("release_date"),
        year=int(tmdb_data.get("release_date", "")[:4]) if tmdb_data.get("release_date") else None,
        runtime=tmdb_data.get("runtime"),
        original_language=tmdb_data.get("original_language"),
        status=tmdb_data.get("status"),
        budget=tmdb_data.get("budget"),
        revenue=tmdb_data.get("revenue"),
        poster_path=tmdb_data.get("poster_path"),
        backdrop_path=tmdb_data.get("backdrop_path"),
        vote_average=tmdb_data.get("vote_average"),
        vote_count=tmdb_data.get("vote_count"),
        popularity=tmdb_data.get("popularity"),
        adult=tmdb_data.get("adult", False)
    )

    db.add(movie)
    db.flush()  # Pour obtenir l'ID du film

    # Ajouter les genres
    for genre_data in tmdb_data.get("genres", []):
        genre = db.query(Genre).filter(Genre.tmdb_id == genre_data["id"]).first()
        if genre:
            movie.genres.append(genre)

    db.commit()
    db.refresh(movie)

    return movie
