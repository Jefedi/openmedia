"""Modèles pour les films, séries et contenus associés"""
from datetime import date, datetime
from typing import Optional
from decimal import Decimal

from sqlalchemy import (
    String, Text, Integer, Date, Numeric, JSON, Boolean,
    ForeignKey, Table, Column, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


# Tables d'association Many-to-Many
movie_genres = Table(
    "movie_genres",
    Base.metadata,
    Column("movie_id", Integer, ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True),
    Column("genre_id", Integer, ForeignKey("genres.id", ondelete="CASCADE"), primary_key=True),
)

series_genres = Table(
    "series_genres",
    Base.metadata,
    Column("series_id", Integer, ForeignKey("series.id", ondelete="CASCADE"), primary_key=True),
    Column("genre_id", Integer, ForeignKey("genres.id", ondelete="CASCADE"), primary_key=True),
)


class Genre(Base):
    """Genres de films/séries"""

    __tablename__ = "genres"

    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)

    # Relations
    movies: Mapped[list["Movie"]] = relationship(
        "Movie",
        secondary=movie_genres,
        back_populates="genres"
    )
    series: Mapped[list["Series"]] = relationship(
        "Series",
        secondary=series_genres,
        back_populates="genres"
    )

    def __repr__(self) -> str:
        return f"Genre(id={self.id}, name={self.name})"


class Movie(Base):
    """Modèle pour les films"""

    __tablename__ = "movies"

    # Identifiants externes
    imdb_id: Mapped[Optional[str]] = mapped_column(String(20), unique=True, index=True, nullable=True)
    tmdb_id: Mapped[Optional[int]] = mapped_column(Integer, unique=True, index=True, nullable=True)

    # Informations de base
    title: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    original_title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    slug: Mapped[str] = mapped_column(String(550), unique=True, nullable=False, index=True)

    # Description
    tagline: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    overview: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Dates
    release_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True, index=True)
    year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)

    # Durée en minutes
    runtime: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Langue et pays
    original_language: Mapped[Optional[str]] = mapped_column(String(10), nullable=True, index=True)
    production_countries: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

    # Statut
    status: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        default="released"  # released, post_production, in_production, planned, canceled
    )

    # Budget et revenus (en USD)
    budget: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    revenue: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Images
    poster_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    backdrop_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Ratings
    vote_average: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(3, 1),
        nullable=True,
        index=True
    )
    vote_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Popularité
    popularity: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)

    # Métadonnées additionnelles (JSON pour données externes)
    extra_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Adulte
    adult: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relations
    genres: Mapped[list["Genre"]] = relationship(
        "Genre",
        secondary=movie_genres,
        back_populates="movies"
    )
    cast: Mapped[list["Cast"]] = relationship(
        "Cast",
        back_populates="movie",
        cascade="all, delete-orphan"
    )
    crew: Mapped[list["Crew"]] = relationship(
        "Crew",
        back_populates="movie",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"Movie(id={self.id}, title={self.title}, year={self.year})"


class Series(Base):
    """Modèle pour les séries TV"""

    __tablename__ = "series"

    # Identifiants externes
    imdb_id: Mapped[Optional[str]] = mapped_column(String(20), unique=True, index=True, nullable=True)
    tmdb_id: Mapped[Optional[int]] = mapped_column(Integer, unique=True, index=True, nullable=True)

    # Informations de base
    name: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    original_name: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    slug: Mapped[str] = mapped_column(String(550), unique=True, nullable=False, index=True)

    # Description
    tagline: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    overview: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Dates
    first_air_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True, index=True)
    last_air_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)

    # Statut
    status: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        index=True  # returning, planned, in_production, ended, canceled
    )
    in_production: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Épisodes
    number_of_seasons: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    number_of_episodes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Durée moyenne d'un épisode en minutes
    episode_run_time: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

    # Langue et pays
    original_language: Mapped[Optional[str]] = mapped_column(String(10), nullable=True, index=True)
    origin_country: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

    # Images
    poster_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    backdrop_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Ratings
    vote_average: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(3, 1),
        nullable=True,
        index=True
    )
    vote_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Popularité
    popularity: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)

    # Métadonnées additionnelles (JSON pour données externes)
    extra_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Adulte
    adult: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relations
    genres: Mapped[list["Genre"]] = relationship(
        "Genre",
        secondary=series_genres,
        back_populates="series"
    )
    seasons: Mapped[list["Season"]] = relationship(
        "Season",
        back_populates="series",
        cascade="all, delete-orphan",
        order_by="Season.season_number"
    )

    def __repr__(self) -> str:
        return f"Series(id={self.id}, name={self.name}, year={self.year})"


class Season(Base):
    """Saisons d'une série"""

    __tablename__ = "seasons"

    # Relation avec la série
    series_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("series.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    series: Mapped["Series"] = relationship("Series", back_populates="seasons")

    # Identifiants externes
    tmdb_id: Mapped[Optional[int]] = mapped_column(Integer, unique=True, index=True, nullable=True)

    # Informations
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    season_number: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    overview: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    air_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    episode_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    poster_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relations
    episodes: Mapped[list["Episode"]] = relationship(
        "Episode",
        back_populates="season",
        cascade="all, delete-orphan",
        order_by="Episode.episode_number"
    )

    __table_args__ = (
        UniqueConstraint("series_id", "season_number", name="uq_series_season"),
    )

    def __repr__(self) -> str:
        return f"Season(id={self.id}, series_id={self.series_id}, season={self.season_number})"


class Episode(Base):
    """Épisodes d'une série"""

    __tablename__ = "episodes"

    # Relations
    series_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("series.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    season_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("seasons.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    season: Mapped["Season"] = relationship("Season", back_populates="episodes")

    # Identifiants externes
    imdb_id: Mapped[Optional[str]] = mapped_column(String(20), unique=True, index=True, nullable=True)
    tmdb_id: Mapped[Optional[int]] = mapped_column(Integer, unique=True, index=True, nullable=True)

    # Informations
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    episode_number: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    season_number: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    overview: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    air_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True, index=True)

    runtime: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    still_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Ratings
    vote_average: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 1), nullable=True)
    vote_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "series_id", "season_number", "episode_number",
            name="uq_series_season_episode"
        ),
    )

    def __repr__(self) -> str:
        return (
            f"Episode(id={self.id}, series_id={self.series_id}, "
            f"S{self.season_number:02d}E{self.episode_number:02d})"
        )


class Person(Base):
    """Personnes (acteurs, réalisateurs, etc.)"""

    __tablename__ = "people"

    # Identifiants externes
    imdb_id: Mapped[Optional[str]] = mapped_column(String(20), unique=True, index=True, nullable=True)
    tmdb_id: Mapped[Optional[int]] = mapped_column(Integer, unique=True, index=True, nullable=True)

    # Informations
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(270), unique=True, nullable=False, index=True)

    biography: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    birthday: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    deathday: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    place_of_birth: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    profile_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    popularity: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)

    # Métadonnées (JSON pour données externes)
    extra_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    def __repr__(self) -> str:
        return f"Person(id={self.id}, name={self.name})"


class Cast(Base):
    """Distribution (acteurs) d'un film"""

    __tablename__ = "cast"

    # Relations
    movie_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("movies.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    movie: Mapped["Movie"] = relationship("Movie", back_populates="cast")

    person_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("people.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    person: Mapped["Person"] = relationship("Person")

    # Informations
    character: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    order: Mapped[int] = mapped_column(Integer, nullable=False)  # Ordre d'apparition

    __table_args__ = (
        UniqueConstraint("movie_id", "person_id", "character", name="uq_movie_cast"),
    )

    def __repr__(self) -> str:
        return f"Cast(movie_id={self.movie_id}, person_id={self.person_id}, character={self.character})"


class Crew(Base):
    """Équipe technique d'un film"""

    __tablename__ = "crew"

    # Relations
    movie_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("movies.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    movie: Mapped["Movie"] = relationship("Movie", back_populates="crew")

    person_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("people.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    person: Mapped["Person"] = relationship("Person")

    # Informations
    job: Mapped[str] = mapped_column(String(100), nullable=False)  # Director, Producer, Writer, etc.
    department: Mapped[str] = mapped_column(String(100), nullable=False)  # Production, Directing, Writing, etc.

    __table_args__ = (
        UniqueConstraint("movie_id", "person_id", "job", name="uq_movie_crew"),
    )

    def __repr__(self) -> str:
        return f"Crew(movie_id={self.movie_id}, person_id={self.person_id}, job={self.job})"
