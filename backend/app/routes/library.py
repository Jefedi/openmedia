"""Routes API pour la bibliothèque personnelle des utilisateurs"""
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from app.db.session import get_db
from app.models.user import User
from app.models.media import Movie, Series, Episode
from app.models.tracking import UserWatchlist, UserProgress, UserRating, UserHistory
from app.routes.auth import get_current_active_user
from app.schemas.media import MovieResponse, SeriesResponse

router = APIRouter(prefix="/library", tags=["Library"])


# ============================================================================
# WATCHLIST ENDPOINTS
# ============================================================================

@router.post("/watchlist")
def add_to_watchlist(
    media_type: str,
    media_id: int,
    priority: Optional[int] = None,
    notes: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Ajouter un film ou une série à la watchlist"""

    # Valider le type de média
    if media_type not in ["movie", "series"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="media_type must be 'movie' or 'series'"
        )

    # Vérifier si le média existe
    if media_type == "movie":
        media = db.query(Movie).filter(Movie.id == media_id).first()
    else:
        media = db.query(Series).filter(Series.id == media_id).first()

    if not media:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{media_type.capitalize()} not found"
        )

    # Vérifier si déjà dans la watchlist
    existing = db.query(UserWatchlist).filter(
        and_(
            UserWatchlist.user_id == current_user.id,
            UserWatchlist.media_type == media_type,
            UserWatchlist.media_id == media_id
        )
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Item already in watchlist"
        )

    # Ajouter à la watchlist
    watchlist_item = UserWatchlist(
        user_id=current_user.id,
        media_type=media_type,
        media_id=media_id,
        priority=priority,
        notes=notes
    )

    db.add(watchlist_item)
    db.commit()
    db.refresh(watchlist_item)

    return {
        "message": f"{media_type.capitalize()} added to watchlist",
        "item": {
            "id": watchlist_item.id,
            "media_type": watchlist_item.media_type,
            "media_id": watchlist_item.media_id,
            "priority": watchlist_item.priority,
            "notes": watchlist_item.notes,
            "added_at": watchlist_item.created_at
        }
    }


@router.delete("/watchlist/{media_type}/{media_id}")
def remove_from_watchlist(
    media_type: str,
    media_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Retirer un film ou une série de la watchlist"""

    # Valider le type de média
    if media_type not in ["movie", "series"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="media_type must be 'movie' or 'series'"
        )

    # Chercher l'item dans la watchlist
    watchlist_item = db.query(UserWatchlist).filter(
        and_(
            UserWatchlist.user_id == current_user.id,
            UserWatchlist.media_type == media_type,
            UserWatchlist.media_id == media_id
        )
    ).first()

    if not watchlist_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found in watchlist"
        )

    db.delete(watchlist_item)
    db.commit()

    return {"message": f"{media_type.capitalize()} removed from watchlist"}


@router.get("/watchlist")
def get_watchlist(
    media_type: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtenir la watchlist de l'utilisateur"""

    query = db.query(UserWatchlist).filter(UserWatchlist.user_id == current_user.id)

    if media_type:
        if media_type not in ["movie", "series"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="media_type must be 'movie' or 'series'"
            )
        query = query.filter(UserWatchlist.media_type == media_type)

    watchlist_items = query.order_by(desc(UserWatchlist.created_at)).all()

    # Enrichir avec les détails du média
    result = []
    for item in watchlist_items:
        if item.media_type == "movie":
            media = db.query(Movie).filter(Movie.id == item.media_id).first()
            if media:
                result.append({
                    "id": item.id,
                    "media_type": "movie",
                    "media_id": media.id,
                    "title": media.title,
                    "year": media.year,
                    "poster_path": media.poster_path,
                    "vote_average": float(media.vote_average) if media.vote_average else None,
                    "priority": item.priority,
                    "notes": item.notes,
                    "added_at": item.created_at
                })
        else:
            media = db.query(Series).filter(Series.id == item.media_id).first()
            if media:
                result.append({
                    "id": item.id,
                    "media_type": "series",
                    "media_id": media.id,
                    "title": media.name,
                    "year": media.year,
                    "poster_path": media.poster_path,
                    "vote_average": float(media.vote_average) if media.vote_average else None,
                    "priority": item.priority,
                    "notes": item.notes,
                    "added_at": item.created_at
                })

    return {"watchlist": result}


# ============================================================================
# PROGRESS ENDPOINTS
# ============================================================================

@router.post("/progress")
def update_progress(
    media_type: str,
    media_id: int,
    status: str,
    episode_id: Optional[int] = None,
    season_number: Optional[int] = None,
    episode_number: Optional[int] = None,
    progress_percentage: Optional[int] = None,
    watched_duration: Optional[int] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Mettre à jour la progression de visionnage"""

    # Valider le type de média
    valid_media_types = ["movie", "series", "episode"]
    if media_type not in valid_media_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"media_type must be one of {valid_media_types}"
        )

    # Valider le statut
    valid_statuses = ["watching", "completed", "paused", "dropped"]
    if status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"status must be one of {valid_statuses}"
        )

    # Chercher la progression existante
    progress = db.query(UserProgress).filter(
        and_(
            UserProgress.user_id == current_user.id,
            UserProgress.media_type == media_type,
            UserProgress.media_id == media_id,
            UserProgress.episode_id == episode_id if episode_id else True
        )
    ).first()

    now = datetime.utcnow()

    if progress:
        # Mettre à jour la progression existante
        progress.status = status
        progress.season_number = season_number
        progress.episode_number = episode_number
        progress.progress_percentage = progress_percentage
        progress.watched_duration = watched_duration
        progress.last_watched_at = now

        if status == "watching" and not progress.started_at:
            progress.started_at = now
        elif status == "completed":
            progress.completed_at = now
            progress.watch_count += 1
    else:
        # Créer une nouvelle entrée de progression
        progress = UserProgress(
            user_id=current_user.id,
            media_type=media_type,
            media_id=media_id,
            episode_id=episode_id,
            season_number=season_number,
            episode_number=episode_number,
            status=status,
            progress_percentage=progress_percentage,
            watched_duration=watched_duration,
            started_at=now if status == "watching" else None,
            completed_at=now if status == "completed" else None,
            last_watched_at=now
        )
        db.add(progress)

    db.commit()
    db.refresh(progress)

    return {
        "message": "Progress updated",
        "progress": {
            "id": progress.id,
            "media_type": progress.media_type,
            "media_id": progress.media_id,
            "status": progress.status,
            "progress_percentage": progress.progress_percentage,
            "last_watched_at": progress.last_watched_at
        }
    }


@router.get("/progress/{media_type}/{media_id}")
def get_progress(
    media_type: str,
    media_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtenir la progression de visionnage d'un média"""

    progress_list = db.query(UserProgress).filter(
        and_(
            UserProgress.user_id == current_user.id,
            UserProgress.media_type == media_type,
            UserProgress.media_id == media_id
        )
    ).order_by(desc(UserProgress.last_watched_at)).all()

    if not progress_list:
        return {"progress": []}

    result = []
    for progress in progress_list:
        result.append({
            "id": progress.id,
            "media_type": progress.media_type,
            "media_id": progress.media_id,
            "episode_id": progress.episode_id,
            "season_number": progress.season_number,
            "episode_number": progress.episode_number,
            "status": progress.status,
            "progress_percentage": progress.progress_percentage,
            "watched_duration": progress.watched_duration,
            "watch_count": progress.watch_count,
            "started_at": progress.started_at,
            "completed_at": progress.completed_at,
            "last_watched_at": progress.last_watched_at
        })

    return {"progress": result}


# ============================================================================
# RATING ENDPOINTS
# ============================================================================

@router.post("/ratings")
def rate_media(
    media_type: str,
    media_id: int,
    rating: float,
    review: Optional[str] = None,
    contains_spoilers: bool = False,
    episode_id: Optional[int] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Noter un film, série ou épisode"""

    # Valider le type de média
    valid_media_types = ["movie", "series", "episode"]
    if media_type not in valid_media_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"media_type must be one of {valid_media_types}"
        )

    # Valider la note
    if rating < 0 or rating > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rating must be between 0 and 10"
        )

    # Chercher la note existante
    existing_rating = db.query(UserRating).filter(
        and_(
            UserRating.user_id == current_user.id,
            UserRating.media_type == media_type,
            UserRating.media_id == media_id,
            UserRating.episode_id == episode_id if episode_id else True
        )
    ).first()

    if existing_rating:
        # Mettre à jour la note existante
        existing_rating.rating = rating
        existing_rating.review = review
        existing_rating.contains_spoilers = contains_spoilers
        existing_rating.rated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing_rating)
        rating_obj = existing_rating
    else:
        # Créer une nouvelle note
        rating_obj = UserRating(
            user_id=current_user.id,
            media_type=media_type,
            media_id=media_id,
            episode_id=episode_id,
            rating=rating,
            review=review,
            contains_spoilers=contains_spoilers
        )
        db.add(rating_obj)
        db.commit()
        db.refresh(rating_obj)

    return {
        "message": "Rating saved",
        "rating": {
            "id": rating_obj.id,
            "media_type": rating_obj.media_type,
            "media_id": rating_obj.media_id,
            "rating": float(rating_obj.rating),
            "review": rating_obj.review,
            "rated_at": rating_obj.rated_at
        }
    }


@router.get("/ratings")
def get_ratings(
    media_type: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtenir les notes de l'utilisateur"""

    query = db.query(UserRating).filter(UserRating.user_id == current_user.id)

    if media_type:
        if media_type not in ["movie", "series", "episode"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="media_type must be 'movie', 'series', or 'episode'"
            )
        query = query.filter(UserRating.media_type == media_type)

    ratings = query.order_by(desc(UserRating.rated_at)).all()

    result = []
    for rating_obj in ratings:
        result.append({
            "id": rating_obj.id,
            "media_type": rating_obj.media_type,
            "media_id": rating_obj.media_id,
            "episode_id": rating_obj.episode_id,
            "rating": float(rating_obj.rating),
            "review": rating_obj.review,
            "contains_spoilers": rating_obj.contains_spoilers,
            "rated_at": rating_obj.rated_at
        })

    return {"ratings": result}


# ============================================================================
# HISTORY ENDPOINTS
# ============================================================================

@router.post("/history")
def add_to_history(
    media_type: str,
    media_id: int,
    episode_id: Optional[int] = None,
    season_number: Optional[int] = None,
    episode_number: Optional[int] = None,
    watched_at: Optional[datetime] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Ajouter une entrée à l'historique de visionnage"""

    # Valider le type de média
    valid_media_types = ["movie", "series", "episode"]
    if media_type not in valid_media_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"media_type must be one of {valid_media_types}"
        )

    # Créer l'entrée d'historique
    history_entry = UserHistory(
        user_id=current_user.id,
        media_type=media_type,
        media_id=media_id,
        episode_id=episode_id,
        season_number=season_number,
        episode_number=episode_number,
        watched_at=watched_at or datetime.utcnow()
    )

    db.add(history_entry)
    db.commit()
    db.refresh(history_entry)

    return {
        "message": "Added to history",
        "history": {
            "id": history_entry.id,
            "media_type": history_entry.media_type,
            "media_id": history_entry.media_id,
            "watched_at": history_entry.watched_at
        }
    }


@router.get("/history")
def get_history(
    media_type: Optional[str] = None,
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtenir l'historique de visionnage de l'utilisateur"""

    query = db.query(UserHistory).filter(UserHistory.user_id == current_user.id)

    if media_type:
        if media_type not in ["movie", "series", "episode"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="media_type must be 'movie', 'series', or 'episode'"
            )
        query = query.filter(UserHistory.media_type == media_type)

    # Compter le total
    total = query.count()

    # Paginer
    history_entries = query.order_by(desc(UserHistory.watched_at)).limit(limit).offset(offset).all()

    # Enrichir avec les détails du média
    result = []
    for entry in history_entries:
        entry_data = {
            "id": entry.id,
            "media_type": entry.media_type,
            "media_id": entry.media_id,
            "episode_id": entry.episode_id,
            "season_number": entry.season_number,
            "episode_number": entry.episode_number,
            "watched_at": entry.watched_at,
            "source": entry.source
        }

        # Ajouter les détails du média
        if entry.media_type == "movie":
            media = db.query(Movie).filter(Movie.id == entry.media_id).first()
            if media:
                entry_data["media_title"] = media.title
                entry_data["poster_path"] = media.poster_path
        elif entry.media_type in ["series", "episode"]:
            media = db.query(Series).filter(Series.id == entry.media_id).first()
            if media:
                entry_data["media_title"] = media.name
                entry_data["poster_path"] = media.poster_path

        result.append(entry_data)

    return {
        "history": result,
        "total": total,
        "limit": limit,
        "offset": offset
    }


# ============================================================================
# CHECK ENDPOINTS (pour savoir si un média est dans la watchlist, etc.)
# ============================================================================

@router.get("/check/{media_type}/{media_id}")
def check_library_status(
    media_type: str,
    media_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Vérifier le statut d'un média dans la bibliothèque de l'utilisateur"""

    # Vérifier watchlist
    in_watchlist = db.query(UserWatchlist).filter(
        and_(
            UserWatchlist.user_id == current_user.id,
            UserWatchlist.media_type == media_type,
            UserWatchlist.media_id == media_id
        )
    ).first() is not None

    # Vérifier progression
    progress = db.query(UserProgress).filter(
        and_(
            UserProgress.user_id == current_user.id,
            UserProgress.media_type == media_type,
            UserProgress.media_id == media_id
        )
    ).first()

    # Vérifier note
    rating = db.query(UserRating).filter(
        and_(
            UserRating.user_id == current_user.id,
            UserRating.media_type == media_type,
            UserRating.media_id == media_id
        )
    ).first()

    return {
        "in_watchlist": in_watchlist,
        "progress": {
            "status": progress.status if progress else None,
            "progress_percentage": progress.progress_percentage if progress else None
        } if progress else None,
        "rating": {
            "value": float(rating.rating) if rating else None,
            "review": rating.review if rating else None
        } if rating else None
    }
