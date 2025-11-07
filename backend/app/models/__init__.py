"""Modèles de base de données"""
from app.models.base import Base
from app.models.user import User, APIKey, RefreshToken
from app.models.media import Movie, Series, Episode, Season, Genre, Person, Cast, Crew, SeriesCast, SeriesCrew, Video
from app.models.tracking import (
    UserWatchlist,
    UserProgress,
    UserRating,
    UserHistory,
)
from app.models.availability import Availability, Platform

__all__ = [
    "Base",
    "User",
    "APIKey",
    "RefreshToken",
    "Movie",
    "Series",
    "Episode",
    "Season",
    "Genre",
    "Person",
    "Cast",
    "Crew",
    "SeriesCast",
    "SeriesCrew",
    "Video",
    "UserWatchlist",
    "UserProgress",
    "UserRating",
    "UserHistory",
    "Availability",
    "Platform",
]
