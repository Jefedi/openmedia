"""Modèles pour le suivi utilisateur (watchlist, progression, ratings)"""
from datetime import datetime
from typing import Optional
from decimal import Decimal

from sqlalchemy import (
    String, Integer, Numeric, DateTime, ForeignKey,
    UniqueConstraint, Index, CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class UserWatchlist(Base):
    """Liste de films/séries à regarder de l'utilisateur"""

    __tablename__ = "user_watchlist"

    # Relations
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Type de média (movie ou series)
    media_type: Mapped[str] = mapped_column(String(10), nullable=False)

    # ID du média (movie_id ou series_id)
    media_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    # Priorité (optionnel)
    priority: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Notes personnelles
    notes: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    __table_args__ = (
        UniqueConstraint("user_id", "media_type", "media_id", name="uq_user_watchlist"),
        CheckConstraint(
            "media_type IN ('movie', 'series')",
            name="check_watchlist_media_type"
        ),
        Index("idx_user_watchlist_lookup", "user_id", "media_type", "media_id"),
    )

    def __repr__(self) -> str:
        return f"UserWatchlist(user_id={self.user_id}, media_type={self.media_type}, media_id={self.media_id})"


class UserProgress(Base):
    """Progression de visionnage de l'utilisateur"""

    __tablename__ = "user_progress"

    # Relations
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Type de média
    media_type: Mapped[str] = mapped_column(String(10), nullable=False)
    media_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    # Pour les séries
    season_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    episode_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    episode_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("episodes.id", ondelete="CASCADE"),
        nullable=True
    )

    # Statut
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="watching"  # watching, completed, paused, dropped
    )

    # Progression en pourcentage (0-100) pour les films ou épisodes
    progress_percentage: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Temps regardé en secondes
    watched_duration: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Dates
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_watched_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # Nombre de fois regardé
    watch_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "user_id", "media_type", "media_id", "episode_id",
            name="uq_user_progress"
        ),
        CheckConstraint(
            "media_type IN ('movie', 'series', 'episode')",
            name="check_progress_media_type"
        ),
        CheckConstraint(
            "status IN ('watching', 'completed', 'paused', 'dropped')",
            name="check_progress_status"
        ),
        CheckConstraint(
            "progress_percentage >= 0 AND progress_percentage <= 100",
            name="check_progress_percentage"
        ),
        Index("idx_user_progress_lookup", "user_id", "media_type", "media_id"),
        Index("idx_user_progress_status", "user_id", "status"),
    )

    def __repr__(self) -> str:
        return (
            f"UserProgress(user_id={self.user_id}, media_type={self.media_type}, "
            f"media_id={self.media_id}, status={self.status})"
        )


class UserRating(Base):
    """Notations de l'utilisateur"""

    __tablename__ = "user_ratings"

    # Relations
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Type de média
    media_type: Mapped[str] = mapped_column(String(10), nullable=False)
    media_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    # Pour les épisodes
    episode_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("episodes.id", ondelete="CASCADE"),
        nullable=True
    )

    # Note (0-10 avec décimale)
    rating: Mapped[Decimal] = mapped_column(
        Numeric(3, 1),
        nullable=False
    )

    # Avis textuel (optionnel)
    review: Mapped[Optional[str]] = mapped_column(String(5000), nullable=True)

    # Spoilers ?
    contains_spoilers: Mapped[bool] = mapped_column(Integer, default=False, nullable=False)

    # Date de notation
    rated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id", "media_type", "media_id", "episode_id",
            name="uq_user_rating"
        ),
        CheckConstraint(
            "media_type IN ('movie', 'series', 'episode')",
            name="check_rating_media_type"
        ),
        CheckConstraint(
            "rating >= 0 AND rating <= 10",
            name="check_rating_value"
        ),
        Index("idx_user_ratings_lookup", "user_id", "media_type", "media_id"),
    )

    def __repr__(self) -> str:
        return (
            f"UserRating(user_id={self.user_id}, media_type={self.media_type}, "
            f"media_id={self.media_id}, rating={self.rating})"
        )


class UserHistory(Base):
    """Historique de visionnage de l'utilisateur"""

    __tablename__ = "user_history"

    # Relations
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Type de média
    media_type: Mapped[str] = mapped_column(String(10), nullable=False)
    media_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    # Pour les épisodes
    episode_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("episodes.id", ondelete="CASCADE"),
        nullable=True
    )
    season_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    episode_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Date de visionnage
    watched_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )

    # Source de synchronisation (manual, trakt, etc.)
    source: Mapped[str] = mapped_column(
        String(20),
        default="manual",
        nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "media_type IN ('movie', 'series', 'episode')",
            name="check_history_media_type"
        ),
        Index("idx_user_history_lookup", "user_id", "media_type", "media_id"),
        Index("idx_user_history_date", "user_id", "watched_at"),
    )

    def __repr__(self) -> str:
        return (
            f"UserHistory(user_id={self.user_id}, media_type={self.media_type}, "
            f"media_id={self.media_id}, watched_at={self.watched_at})"
        )
