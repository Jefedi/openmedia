"""Routes API pour les séries TV"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.session import get_db
from app.models.media import Series, Season, Episode, Genre, series_genres
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
    TMDBSearchResponse
)
from app.routes.auth import get_current_user
from app.services.tmdb import tmdb_service

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
    Liste des séries avec pagination et filtres

    Args:
        page: Numéro de page
        page_size: Nombre d'éléments par page
        search: Recherche par nom
        genre: Filtrer par genre (slug)
        year: Filtrer par année de première diffusion
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

    # Filtrer par année
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
    """Obtenir une série par ID"""
    series = db.query(Series).filter(Series.id == series_id).first()

    if not series:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Série non trouvée"
        )

    return series


@router.post("", response_model=SeriesResponse, status_code=status.HTTP_201_CREATED)
async def create_series(
    series_data: SeriesCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Créer une nouvelle série"""
    # Vérifier si la série existe déjà
    if series_data.tmdb_id:
        existing = db.query(Series).filter(Series.tmdb_id == series_data.tmdb_id).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Une série avec cet ID TMDB existe déjà"
            )

    existing_slug = db.query(Series).filter(Series.slug == series_data.slug).first()
    if existing_slug:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Une série avec ce slug existe déjà"
        )

    # Créer la série
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
    """Mettre à jour une série"""
    series = db.query(Series).filter(Series.id == series_id).first()

    if not series:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Série non trouvée"
        )

    # Mettre à jour les champs fournis
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
    """Supprimer une série (admin uniquement)"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas les droits pour supprimer des séries"
        )

    series = db.query(Series).filter(Series.id == series_id).first()

    if not series:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Série non trouvée"
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
    """Obtenir toutes les saisons d'une série"""
    series = db.query(Series).filter(Series.id == series_id).first()

    if not series:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Série non trouvée"
        )

    return series.seasons


@router.get("/{series_id}/seasons/{season_number}", response_model=SeasonResponse)
async def get_season(
    series_id: int,
    season_number: int,
    db: Session = Depends(get_db)
):
    """Obtenir une saison spécifique"""
    season = db.query(Season).filter(
        Season.series_id == series_id,
        Season.season_number == season_number
    ).first()

    if not season:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saison non trouvée"
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
    """Obtenir tous les épisodes d'une saison"""
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
    """Obtenir un épisode spécifique"""
    episode = db.query(Episode).filter(
        Episode.series_id == series_id,
        Episode.season_number == season_number,
        Episode.episode_number == episode_number
    ).first()

    if not episode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Épisode non trouvé"
        )

    return episode


# ============================================================================
# TMDB INTEGRATION
# ============================================================================

@router.get("/tmdb/search", response_model=TMDBSearchResponse)
async def search_series_tmdb(
    query: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    first_air_date_year: Optional[int] = None,
    language: str = Query("fr-FR")
):
    """Rechercher des séries sur TMDB"""
    if not tmdb_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service TMDB non disponible"
        )

    results = await tmdb_service.search_tv(
        query=query,
        page=page,
        first_air_date_year=first_air_date_year,
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
async def get_popular_series_tmdb(
    page: int = Query(1, ge=1),
    language: str = Query("fr-FR")
):
    """Obtenir les séries populaires depuis TMDB"""
    if not tmdb_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service TMDB non disponible"
        )

    results = await tmdb_service.get_popular_tv(page=page, language=language)

    if not results:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des séries populaires"
        )

    return TMDBSearchResponse(
        results=results.get("results", []),
        total_results=results.get("total_results", 0),
        page=results.get("page", 1),
        total_pages=results.get("total_pages", 0)
    )


@router.get("/tmdb/{tmdb_id}")
async def get_series_from_tmdb(
    tmdb_id: int,
    language: str = Query("fr-FR")
):
    """Obtenir les détails d'une série depuis TMDB"""
    if not tmdb_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service TMDB non disponible"
        )

    series = await tmdb_service.get_tv_details(tmdb_id, language=language)

    if not series:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Série non trouvée sur TMDB"
        )

    return series


@router.post("/tmdb/{tmdb_id}/import", response_model=SeriesResponse)
async def import_series_from_tmdb(
    tmdb_id: int,
    import_seasons: bool = Query(False, description="Importer également les saisons et épisodes"),
    language: str = Query("fr-FR"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Importer une série depuis TMDB

    Args:
        tmdb_id: ID TMDB de la série
        import_seasons: Si True, importe également les saisons et épisodes
        language: Code de langue
    """
    if not tmdb_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service TMDB non disponible"
        )

    # Vérifier si la série existe déjà
    existing = db.query(Series).filter(Series.tmdb_id == tmdb_id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cette série existe déjà dans la base de données"
        )

    # Récupérer les détails depuis TMDB
    tmdb_data = await tmdb_service.get_tv_details(tmdb_id, language=language)

    if not tmdb_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Série non trouvée sur TMDB"
        )

    # Créer le slug
    from slugify import slugify
    slug = slugify(tmdb_data.get("name", ""))

    # Vérifier l'unicité du slug
    slug_base = slug
    counter = 1
    while db.query(Series).filter(Series.slug == slug).first():
        slug = f"{slug_base}-{counter}"
        counter += 1

    # Créer la série
    series = Series(
        tmdb_id=tmdb_id,
        imdb_id=tmdb_data.get("external_ids", {}).get("imdb_id"),
        name=tmdb_data.get("name"),
        original_name=tmdb_data.get("original_name"),
        slug=slug,
        overview=tmdb_data.get("overview"),
        tagline=tmdb_data.get("tagline"),
        first_air_date=tmdb_data.get("first_air_date"),
        last_air_date=tmdb_data.get("last_air_date"),
        year=int(tmdb_data.get("first_air_date", "")[:4]) if tmdb_data.get("first_air_date") else None,
        status=tmdb_data.get("status"),
        in_production=tmdb_data.get("in_production", False),
        number_of_seasons=tmdb_data.get("number_of_seasons", 0),
        number_of_episodes=tmdb_data.get("number_of_episodes", 0),
        original_language=tmdb_data.get("original_language"),
        poster_path=tmdb_data.get("poster_path"),
        backdrop_path=tmdb_data.get("backdrop_path"),
        vote_average=tmdb_data.get("vote_average"),
        vote_count=tmdb_data.get("vote_count"),
        popularity=tmdb_data.get("popularity"),
        adult=tmdb_data.get("adult", False)
    )

    db.add(series)
    db.flush()

    # Ajouter les genres
    for genre_data in tmdb_data.get("genres", []):
        genre = db.query(Genre).filter(Genre.tmdb_id == genre_data["id"]).first()
        if genre:
            series.genres.append(genre)

    # Importer les saisons si demandé
    if import_seasons:
        for season_data in tmdb_data.get("seasons", []):
            season_number = season_data.get("season_number", 0)

            # Créer la saison
            season = Season(
                series_id=series.id,
                tmdb_id=season_data.get("id"),
                season_number=season_number,
                name=season_data.get("name", f"Saison {season_number}"),
                overview=season_data.get("overview"),
                air_date=season_data.get("air_date"),
                episode_count=season_data.get("episode_count", 0),
                poster_path=season_data.get("poster_path")
            )
            db.add(season)

    db.commit()
    db.refresh(series)

    return series
