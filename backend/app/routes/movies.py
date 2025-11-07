"""Routes API pour les films"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.db.session import get_db
from app.models.media import Movie, Genre, movie_genres, Cast, Crew
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
    """Obtenir un film par ID avec genres, cast et crew"""
    movie = db.query(Movie).options(
        joinedload(Movie.genres),
        joinedload(Movie.cast).joinedload(Cast.person),
        joinedload(Movie.crew).joinedload(Crew.person)
    ).filter(Movie.id == movie_id).first()

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
# OMDB INTEGRATION
# ============================================================================

@router.get("/omdb/search", response_model=OMDbSearchResponse)
async def search_movies_omdb(
    query: str = Query(..., min_length=1),
    page: int = Query(1, ge=1, le=100),
    year: Optional[int] = None
):
    """
    Rechercher des films sur OMDb

    Args:
        query: Terme de recherche
        page: Numéro de page (1-100)
        year: Année de sortie (optionnel)
    """
    if not omdb_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service OMDb non disponible. Vérifiez la configuration OMDB_API_KEY."
        )

    results = await omdb_service.search_movies(
        query=query,
        page=page,
        year=year
    )

    if not results:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la recherche OMDb"
        )

    return results


@router.get("/omdb/imdb/{imdb_id}", response_model=OMDbDetailResponse)
async def get_movie_from_omdb(
    imdb_id: str,
    plot: str = Query("full", regex="^(short|full)$")
):
    """Obtenir les détails d'un film depuis OMDb par ID IMDb"""
    if not omdb_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service OMDb non disponible"
        )

    movie = await omdb_service.get_by_imdb_id(imdb_id, plot=plot)

    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Film non trouvé sur OMDb"
        )

    return movie


@router.post("/omdb/imdb/{imdb_id}/import", response_model=MovieResponse)
async def import_movie_from_omdb(
    imdb_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Importer un film depuis OMDb par ID IMDb

    Récupère les informations du film depuis OMDb et le crée dans la base de données.
    """
    if not omdb_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service OMDb non disponible"
        )

    # Vérifier si le film existe déjà
    existing = db.query(Movie).filter(Movie.imdb_id == imdb_id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce film existe déjà dans la base de données"
        )

    # Récupérer les détails depuis OMDb
    omdb_data = await omdb_service.get_by_imdb_id(imdb_id, plot="full")

    if not omdb_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Film non trouvé sur OMDb"
        )

    # Créer le slug
    from slugify import slugify
    title = omdb_data.get("Title", "")
    slug = slugify(title)

    # Vérifier l'unicité du slug
    slug_base = slug
    counter = 1
    while db.query(Movie).filter(Movie.slug == slug).first():
        slug = f"{slug_base}-{counter}"
        counter += 1

    # Parser les données OMDb
    year = omdb_service.parse_year(omdb_data.get("Year"))
    runtime = omdb_service.parse_runtime(omdb_data.get("Runtime"))
    rating = omdb_service.parse_rating(omdb_data.get("imdbRating"))

    # Convertir la date de sortie
    from datetime import datetime
    release_date = None
    if omdb_data.get("Released") and omdb_data.get("Released") != "N/A":
        try:
            release_date = datetime.strptime(omdb_data["Released"], "%d %b %Y").date()
        except:
            pass

    # Créer le film avec poster haute qualité
    poster_url = omdb_service.get_poster_url(omdb_data.get("Poster"), high_quality=True)

    movie = Movie(
        imdb_id=imdb_id,
        title=title,
        slug=slug,
        overview=omdb_data.get("Plot") if omdb_data.get("Plot") != "N/A" else None,
        release_date=release_date,
        year=year,
        runtime=runtime,
        original_language=omdb_data.get("Language", "").split(",")[0].strip() if omdb_data.get("Language") != "N/A" else None,
        poster_path=poster_url,
        vote_average=rating,
        adult=omdb_data.get("Rated") == "R" or omdb_data.get("Rated") == "NC-17"
    )

    db.add(movie)
    db.flush()

    # Ajouter les genres
    genres = omdb_service.parse_genres(omdb_data.get("Genre"))
    for genre_name in genres:
        from slugify import slugify
        genre_slug = slugify(genre_name)
        genre = db.query(Genre).filter(Genre.slug == genre_slug).first()

        if not genre:
            # Créer le genre s'il n'existe pas
            genre = Genre(name=genre_name, slug=genre_slug)
            db.add(genre)
            db.flush()

        movie.genres.append(genre)

    db.commit()
    db.refresh(movie)

    return movie
