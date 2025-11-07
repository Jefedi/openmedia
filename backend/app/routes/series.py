"""Routes API pour les s�ries TV"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.db.session import get_db
from app.models.media import Series, Season, Episode, Genre, series_genres, SeriesCast, SeriesCrew, Video
from app.models.user import User
from app.schemas.media import (
    SeriesResponse,
    SeriesCreate,
    SeriesUpdate,
    SeriesListResponse,
    SeasonResponse,
    SeasonCreate,
    EpisodeResponse,
    EpisodeCreate,
    OMDbSearchResponse,
    OMDbDetailResponse
)
from app.routes.auth import get_current_user
from app.services.omdb import omdb_service

router = APIRouter(prefix="/series", tags=["TV Series"])


# ============================================================================
# SERIES CRUD
# ============================================================================

@router.get("", response_model=SeriesListResponse)
async def list_series(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    genre: Optional[str] = None,
    year: Optional[int] = None,
    status: Optional[str] = None,
    sort_by: str = Query("created_at", regex="^(name|first_air_date|vote_average|popularity|created_at)$"),
    order: str = Query("desc", regex="^(asc|desc)$"),
    db: Session = Depends(get_db)
):
    """
    Liste des s�ries avec pagination et filtres

    Args:
        page: Num�ro de page
        page_size: Nombre d'�l�ments par page
        search: Recherche par nom
        genre: Filtrer par genre (slug)
        year: Filtrer par ann�e de premi�re diffusion
        status: Filtrer par statut (returning, ended, etc.)
        sort_by: Trier par
        order: Ordre de tri (asc, desc)
    """
    query = db.query(Series)

    # Filtrer par recherche
    if search:
        query = query.filter(
            func.lower(Series.name).contains(search.lower())
        )

    # Filtrer par genre
    if genre:
        query = query.join(Series.genres).filter(Genre.slug == genre)

    # Filtrer par ann�e
    if year:
        query = query.filter(Series.year == year)

    # Filtrer par statut
    if status:
        query = query.filter(Series.status == status)

    # Compter le total
    total = query.count()

    # Tri
    sort_column = getattr(Series, sort_by)
    if order == "desc":
        sort_column = sort_column.desc()
    else:
        sort_column = sort_column.asc()

    # Pagination
    series = query.order_by(sort_column).offset((page - 1) * page_size).limit(page_size).all()

    return SeriesListResponse(
        series=series,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{series_id}", response_model=SeriesResponse)
async def get_series(
    series_id: int,
    db: Session = Depends(get_db)
):
    """Obtenir une série par ID avec genres, saisons, cast, crew et videos"""
    series = db.query(Series).options(
        joinedload(Series.genres),
        joinedload(Series.seasons),
        joinedload(Series.cast).joinedload(SeriesCast.person),
        joinedload(Series.crew).joinedload(SeriesCrew.person),
        joinedload(Series.videos)
    ).filter(Series.id == series_id).first()

    if not series:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="S�rie non trouv�e"
        )

    return series


@router.post("", response_model=SeriesResponse, status_code=status.HTTP_201_CREATED)
async def create_series(
    series_data: SeriesCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cr�er une nouvelle s�rie"""
    # V�rifier si la s�rie existe d�j�
    if series_data.tmdb_id:
        existing = db.query(Series).filter(Series.tmdb_id == series_data.tmdb_id).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Une s�rie avec cet ID TMDB existe d�j�"
            )

    existing_slug = db.query(Series).filter(Series.slug == series_data.slug).first()
    if existing_slug:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Une s�rie avec ce slug existe d�j�"
        )

    # Cr�er la s�rie
    series = Series(**series_data.model_dump())
    db.add(series)
    db.commit()
    db.refresh(series)

    return series


@router.put("/{series_id}", response_model=SeriesResponse)
async def update_series(
    series_id: int,
    series_data: SeriesUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mettre � jour une s�rie"""
    series = db.query(Series).filter(Series.id == series_id).first()

    if not series:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="S�rie non trouv�e"
        )

    # Mettre � jour les champs fournis
    for field, value in series_data.model_dump(exclude_unset=True).items():
        setattr(series, field, value)

    db.commit()
    db.refresh(series)

    return series


@router.delete("/{series_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_series(
    series_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Supprimer une s�rie (admin uniquement)"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas les droits pour supprimer des s�ries"
        )

    series = db.query(Series).filter(Series.id == series_id).first()

    if not series:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="S�rie non trouv�e"
        )

    db.delete(series)
    db.commit()


# ============================================================================
# SEASONS
# ============================================================================

@router.get("/{series_id}/seasons", response_model=list[SeasonResponse])
async def get_series_seasons(
    series_id: int,
    db: Session = Depends(get_db)
):
    """Obtenir toutes les saisons d'une s�rie"""
    series = db.query(Series).filter(Series.id == series_id).first()

    if not series:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="S�rie non trouv�e"
        )

    return series.seasons


@router.get("/{series_id}/seasons/{season_number}", response_model=SeasonResponse)
async def get_season(
    series_id: int,
    season_number: int,
    db: Session = Depends(get_db)
):
    """Obtenir une saison sp�cifique"""
    season = db.query(Season).filter(
        Season.series_id == series_id,
        Season.season_number == season_number
    ).first()

    if not season:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saison non trouv�e"
        )

    return season


# ============================================================================
# EPISODES
# ============================================================================

@router.get("/{series_id}/seasons/{season_number}/episodes", response_model=list[EpisodeResponse])
async def get_season_episodes(
    series_id: int,
    season_number: int,
    db: Session = Depends(get_db)
):
    """Obtenir tous les �pisodes d'une saison"""
    episodes = db.query(Episode).filter(
        Episode.series_id == series_id,
        Episode.season_number == season_number
    ).order_by(Episode.episode_number).all()

    return episodes


@router.get("/{series_id}/seasons/{season_number}/episodes/{episode_number}", response_model=EpisodeResponse)
async def get_episode(
    series_id: int,
    season_number: int,
    episode_number: int,
    db: Session = Depends(get_db)
):
    """Obtenir un �pisode sp�cifique"""
    episode = db.query(Episode).filter(
        Episode.series_id == series_id,
        Episode.season_number == season_number,
        Episode.episode_number == episode_number
    ).first()

    if not episode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="�pisode non trouv�"
        )

    return episode


# ============================================================================
# TMDB INTEGRATION

# ============================================================================
# OMDB INTEGRATION
# ============================================================================

@router.get("/omdb/search", response_model=OMDbSearchResponse)
async def search_series_omdb(
    query: str = Query(..., min_length=1),
    page: int = Query(1, ge=1, le=100),
    year: Optional[int] = None
):
    """Rechercher des séries sur OMDb"""
    if not omdb_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service OMDb non disponible"
        )

    results = await omdb_service.search_series(
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
async def get_series_from_omdb(
    imdb_id: str,
    plot: str = Query("full", regex="^(short|full)$")
):
    """Obtenir les détails d'une série depuis OMDb par ID IMDb"""
    if not omdb_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service OMDb non disponible"
        )

    series = await omdb_service.get_by_imdb_id(imdb_id, plot=plot)

    if not series:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Série non trouvée sur OMDb"
        )

    return series


@router.post("/omdb/imdb/{imdb_id}/import", response_model=SeriesResponse)
async def import_series_from_omdb(
    imdb_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Importer une série depuis OMDb par ID IMDb
    """
    if not omdb_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service OMDb non disponible"
        )

    # Vérifier si la série existe déjà
    existing = db.query(Series).filter(Series.imdb_id == imdb_id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cette série existe déjà dans la base de données"
        )

    # Récupérer les détails depuis OMDb
    omdb_data = await omdb_service.get_by_imdb_id(imdb_id, plot="full")

    if not omdb_data or omdb_data.get("Type") != "series":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Série non trouvée sur OMDb"
        )

    # Créer le slug
    from slugify import slugify
    name = omdb_data.get("Title", "")
    slug = slugify(name)

    # Vérifier l'unicité du slug
    slug_base = slug
    counter = 1
    while db.query(Series).filter(Series.slug == slug).first():
        slug = f"{slug_base}-{counter}"
        counter += 1

    # Parser les données OMDb
    year = omdb_service.parse_year(omdb_data.get("Year"))
    rating = omdb_service.parse_rating(omdb_data.get("imdbRating"))
    total_seasons = int(omdb_data.get("totalSeasons", 0)) if omdb_data.get("totalSeasons") != "N/A" else 0

    # Convertir la date de première diffusion
    from datetime import datetime
    first_air_date = None
    if omdb_data.get("Released") and omdb_data.get("Released") != "N/A":
        try:
            first_air_date = datetime.strptime(omdb_data["Released"], "%d %b %Y").date()
        except:
            pass

    # Créer la série avec poster haute qualité
    poster_url = omdb_service.get_poster_url(omdb_data.get("Poster"), high_quality=True)

    series = Series(
        imdb_id=imdb_id,
        name=name,
        slug=slug,
        overview=omdb_data.get("Plot") if omdb_data.get("Plot") != "N/A" else None,
        first_air_date=first_air_date,
        year=year,
        number_of_seasons=total_seasons,
        original_language=omdb_data.get("Language", "").split(",")[0].strip() if omdb_data.get("Language") != "N/A" else None,
        poster_path=poster_url,
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
