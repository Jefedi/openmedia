"""Schemas pour les films, séries et épisodes"""
from datetime import date
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, Field


# ============================================================================
# GENRE SCHEMAS
# ============================================================================

class GenreBase(BaseModel):
    """Schema de base pour un genre"""
    name: str
    slug: str


class GenreCreate(GenreBase):
    """Schema pour créer un genre"""
    tmdb_id: Optional[int] = None


class GenreResponse(GenreBase):
    """Schema de réponse pour un genre"""
    id: int
    tmdb_id: Optional[int] = None

    class Config:
        from_attributes = True


# ============================================================================
# MOVIE SCHEMAS
# ============================================================================

class MovieBase(BaseModel):
    """Schema de base pour un film"""
    title: str
    original_title: Optional[str] = None
    overview: Optional[str] = None
    tagline: Optional[str] = None
    release_date: Optional[date] = None
    runtime: Optional[int] = None
    original_language: Optional[str] = None
    status: Optional[str] = "released"
    budget: Optional[int] = None
    revenue: Optional[int] = None
    poster_path: Optional[str] = None
    backdrop_path: Optional[str] = None
    adult: bool = False


class MovieCreate(MovieBase):
    """Schema pour créer un film"""
    imdb_id: Optional[str] = None
    tmdb_id: Optional[int] = None
    slug: str
    year: Optional[int] = None
    vote_average: Optional[Decimal] = None
    vote_count: int = 0
    popularity: Optional[Decimal] = None


class MovieUpdate(BaseModel):
    """Schema pour mettre à jour un film"""
    title: Optional[str] = None
    original_title: Optional[str] = None
    overview: Optional[str] = None
    tagline: Optional[str] = None
    release_date: Optional[date] = None
    runtime: Optional[int] = None
    status: Optional[str] = None
    poster_path: Optional[str] = None
    backdrop_path: Optional[str] = None


class MovieResponse(MovieBase):
    """Schema de réponse pour un film"""
    id: int
    slug: str
    year: Optional[int] = None
    imdb_id: Optional[str] = None
    tmdb_id: Optional[int] = None
    vote_average: Optional[Decimal] = None
    vote_count: int
    popularity: Optional[Decimal] = None
    genres: list[GenreResponse] = []
    created_at: date
    updated_at: date

    class Config:
        from_attributes = True


class MovieListResponse(BaseModel):
    """Schema de réponse pour une liste de films"""
    movies: list[MovieResponse]
    total: int
    page: int
    page_size: int


# ============================================================================
# TV SHOW (SERIES) SCHEMAS
# ============================================================================

class SeriesBase(BaseModel):
    """Schema de base pour une série"""
    name: str
    original_name: Optional[str] = None
    overview: Optional[str] = None
    tagline: Optional[str] = None
    first_air_date: Optional[date] = None
    last_air_date: Optional[date] = None
    status: Optional[str] = None
    in_production: bool = False
    number_of_seasons: int = 0
    number_of_episodes: int = 0
    original_language: Optional[str] = None
    poster_path: Optional[str] = None
    backdrop_path: Optional[str] = None
    adult: bool = False


class SeriesCreate(SeriesBase):
    """Schema pour créer une série"""
    imdb_id: Optional[str] = None
    tmdb_id: Optional[int] = None
    slug: str
    year: Optional[int] = None
    vote_average: Optional[Decimal] = None
    vote_count: int = 0
    popularity: Optional[Decimal] = None


class SeriesUpdate(BaseModel):
    """Schema pour mettre à jour une série"""
    name: Optional[str] = None
    original_name: Optional[str] = None
    overview: Optional[str] = None
    tagline: Optional[str] = None
    first_air_date: Optional[date] = None
    last_air_date: Optional[date] = None
    status: Optional[str] = None
    in_production: Optional[bool] = None
    number_of_seasons: Optional[int] = None
    number_of_episodes: Optional[int] = None
    poster_path: Optional[str] = None
    backdrop_path: Optional[str] = None


class SeriesResponse(SeriesBase):
    """Schema de réponse pour une série"""
    id: int
    slug: str
    year: Optional[int] = None
    imdb_id: Optional[str] = None
    tmdb_id: Optional[int] = None
    vote_average: Optional[Decimal] = None
    vote_count: int
    popularity: Optional[Decimal] = None
    genres: list[GenreResponse] = []
    created_at: date
    updated_at: date

    class Config:
        from_attributes = True


class SeriesListResponse(BaseModel):
    """Schema de réponse pour une liste de séries"""
    series: list[SeriesResponse]
    total: int
    page: int
    page_size: int


# ============================================================================
# SEASON SCHEMAS
# ============================================================================

class SeasonBase(BaseModel):
    """Schema de base pour une saison"""
    name: str
    season_number: int
    overview: Optional[str] = None
    air_date: Optional[date] = None
    episode_count: int = 0
    poster_path: Optional[str] = None


class SeasonCreate(SeasonBase):
    """Schema pour créer une saison"""
    series_id: int
    tmdb_id: Optional[int] = None


class SeasonUpdate(BaseModel):
    """Schema pour mettre à jour une saison"""
    name: Optional[str] = None
    overview: Optional[str] = None
    air_date: Optional[date] = None
    episode_count: Optional[int] = None
    poster_path: Optional[str] = None


class SeasonResponse(SeasonBase):
    """Schema de réponse pour une saison"""
    id: int
    series_id: int
    tmdb_id: Optional[int] = None
    created_at: date
    updated_at: date

    class Config:
        from_attributes = True


# ============================================================================
# EPISODE SCHEMAS
# ============================================================================

class EpisodeBase(BaseModel):
    """Schema de base pour un épisode"""
    name: str
    episode_number: int
    season_number: int
    overview: Optional[str] = None
    air_date: Optional[date] = None
    runtime: Optional[int] = None
    still_path: Optional[str] = None


class EpisodeCreate(EpisodeBase):
    """Schema pour créer un épisode"""
    series_id: int
    season_id: int
    imdb_id: Optional[str] = None
    tmdb_id: Optional[int] = None
    vote_average: Optional[Decimal] = None
    vote_count: int = 0


class EpisodeUpdate(BaseModel):
    """Schema pour mettre à jour un épisode"""
    name: Optional[str] = None
    overview: Optional[str] = None
    air_date: Optional[date] = None
    runtime: Optional[int] = None
    still_path: Optional[str] = None


class EpisodeResponse(EpisodeBase):
    """Schema de réponse pour un épisode"""
    id: int
    series_id: int
    season_id: int
    imdb_id: Optional[str] = None
    tmdb_id: Optional[int] = None
    vote_average: Optional[Decimal] = None
    vote_count: int
    created_at: date
    updated_at: date

    class Config:
        from_attributes = True


# ============================================================================
# TMDB SEARCH SCHEMAS
# ============================================================================

class TMDBSearchResult(BaseModel):
    """Schema pour un résultat de recherche TMDB"""
    id: int
    media_type: str  # "movie" or "tv"
    title: Optional[str] = None  # Pour les films
    name: Optional[str] = None  # Pour les séries
    original_title: Optional[str] = None
    original_name: Optional[str] = None
    overview: Optional[str] = None
    release_date: Optional[str] = None  # Pour les films
    first_air_date: Optional[str] = None  # Pour les séries
    poster_path: Optional[str] = None
    backdrop_path: Optional[str] = None
    vote_average: Optional[float] = None
    vote_count: Optional[int] = None
    popularity: Optional[float] = None


class TMDBSearchResponse(BaseModel):
    """Schema de réponse pour une recherche TMDB"""
    results: list[TMDBSearchResult]
    total_results: int
    page: int
    total_pages: int


# ============================================================================
# OMDB SEARCH SCHEMAS
# ============================================================================

class OMDbSearchResult(BaseModel):
    """Schema pour un rÃ©sultat de recherche OMDb"""
    Title: str
    Year: str
    imdbID: str
    Type: str  # "movie", "series", "episode"
    Poster: Optional[str] = None

    class Config:
        # Permettre les noms de champs avec majuscules
        populate_by_name = True


class OMDbSearchResponse(BaseModel):
    """Schema de rÃ©ponse pour une recherche OMDb"""
    Search: Optional[list[OMDbSearchResult]] = None
    totalResults: str
    Response: str

    class Config:
        populate_by_name = True


class OMDbDetailResponse(BaseModel):
    """Schema de rÃ©ponse dÃ©taillÃ©e OMDb"""
    Title: Optional[str] = None
    Year: Optional[str] = None
    Rated: Optional[str] = None
    Released: Optional[str] = None
    Runtime: Optional[str] = None
    Genre: Optional[str] = None
    Director: Optional[str] = None
    Writer: Optional[str] = None
    Actors: Optional[str] = None
    Plot: Optional[str] = None
    Language: Optional[str] = None
    Country: Optional[str] = None
    Awards: Optional[str] = None
    Poster: Optional[str] = None
    Ratings: Optional[list[dict]] = None
    Metascore: Optional[str] = None
    imdbRating: Optional[str] = None
    imdbVotes: Optional[str] = None
    imdbID: Optional[str] = None
    Type: Optional[str] = None
    DVD: Optional[str] = None
    BoxOffice: Optional[str] = None
    Production: Optional[str] = None
    Website: Optional[str] = None
    Response: Optional[str] = None
    # Champs pour sÃ©ries
    totalSeasons: Optional[str] = None
    # Champs pour saisons
    Season: Optional[str] = None
    Episodes: Optional[list[dict]] = None

    class Config:
        populate_by_name = True
