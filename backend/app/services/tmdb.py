"""Service pour l'intégration avec l'API TMDB (The Movie Database)"""
import httpx
from typing import Optional, Dict, Any
from datetime import datetime

from app.config import settings


class TMDBService:
    """Service pour interagir avec l'API TMDB"""

    BASE_URL = "https://api.themoviedb.org/3"
    IMAGE_BASE_URL = "https://image.tmdb.org/t/p"

    def __init__(self):
        """Initialiser le service TMDB"""
        self.api_key = settings.TMDB_API_KEY
        self.read_token = settings.TMDB_API_READ_TOKEN

        if not self.api_key and not self.read_token:
            raise ValueError("TMDB_API_KEY or TMDB_API_READ_TOKEN must be set in .env")

    def _get_headers(self) -> Dict[str, str]:
        """Obtenir les headers pour les requêtes API"""
        if self.read_token:
            return {
                "Authorization": f"Bearer {self.read_token}",
                "Content-Type": "application/json;charset=utf-8"
            }
        return {}

    def _get_params(self, **kwargs) -> Dict[str, Any]:
        """Obtenir les paramètres de requête avec l'API key"""
        params = {"api_key": self.api_key} if self.api_key and not self.read_token else {}
        params.update(kwargs)
        return params

    async def _request(self, endpoint: str, **params) -> Optional[Dict[str, Any]]:
        """Faire une requête à l'API TMDB"""
        url = f"{self.BASE_URL}{endpoint}"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    url,
                    headers=self._get_headers(),
                    params=self._get_params(**params),
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                print(f"TMDB API Error: {e}")
                return None

    # ========================================================================
    # SEARCH
    # ========================================================================

    async def search_multi(self, query: str, page: int = 1, language: str = "fr-FR") -> Optional[Dict]:
        """
        Rechercher films et séries

        Args:
            query: Terme de recherche
            page: Numéro de page (défaut: 1)
            language: Code de langue (défaut: fr-FR)

        Returns:
            Résultats de recherche ou None en cas d'erreur
        """
        return await self._request(
            "/search/multi",
            query=query,
            page=page,
            language=language
        )

    async def search_movie(self, query: str, page: int = 1, year: Optional[int] = None, language: str = "fr-FR") -> Optional[Dict]:
        """
        Rechercher des films

        Args:
            query: Terme de recherche
            page: Numéro de page
            year: Année de sortie (optionnel)
            language: Code de langue

        Returns:
            Résultats de recherche ou None en cas d'erreur
        """
        params = {
            "query": query,
            "page": page,
            "language": language
        }
        if year:
            params["year"] = year

        return await self._request("/search/movie", **params)

    async def search_tv(self, query: str, page: int = 1, first_air_date_year: Optional[int] = None, language: str = "fr-FR") -> Optional[Dict]:
        """
        Rechercher des séries TV

        Args:
            query: Terme de recherche
            page: Numéro de page
            first_air_date_year: Année de première diffusion (optionnel)
            language: Code de langue

        Returns:
            Résultats de recherche ou None en cas d'erreur
        """
        params = {
            "query": query,
            "page": page,
            "language": language
        }
        if first_air_date_year:
            params["first_air_date_year"] = first_air_date_year

        return await self._request("/search/tv", **params)

    # ========================================================================
    # MOVIES
    # ========================================================================

    async def get_movie_details(self, movie_id: int, language: str = "fr-FR") -> Optional[Dict]:
        """
        Obtenir les détails d'un film

        Args:
            movie_id: ID TMDB du film
            language: Code de langue

        Returns:
            Détails du film ou None en cas d'erreur
        """
        return await self._request(
            f"/movie/{movie_id}",
            language=language,
            append_to_response="credits,videos,images,keywords,external_ids"
        )

    async def get_popular_movies(self, page: int = 1, language: str = "fr-FR") -> Optional[Dict]:
        """Obtenir les films populaires"""
        return await self._request(
            "/movie/popular",
            page=page,
            language=language
        )

    async def get_top_rated_movies(self, page: int = 1, language: str = "fr-FR") -> Optional[Dict]:
        """Obtenir les films les mieux notés"""
        return await self._request(
            "/movie/top_rated",
            page=page,
            language=language
        )

    async def get_upcoming_movies(self, page: int = 1, language: str = "fr-FR") -> Optional[Dict]:
        """Obtenir les films à venir"""
        return await self._request(
            "/movie/upcoming",
            page=page,
            language=language
        )

    async def get_now_playing_movies(self, page: int = 1, language: str = "fr-FR") -> Optional[Dict]:
        """Obtenir les films actuellement au cinéma"""
        return await self._request(
            "/movie/now_playing",
            page=page,
            language=language
        )

    # ========================================================================
    # TV SHOWS
    # ========================================================================

    async def get_tv_details(self, tv_id: int, language: str = "fr-FR") -> Optional[Dict]:
        """
        Obtenir les détails d'une série TV

        Args:
            tv_id: ID TMDB de la série
            language: Code de langue

        Returns:
            Détails de la série ou None en cas d'erreur
        """
        return await self._request(
            f"/tv/{tv_id}",
            language=language,
            append_to_response="credits,videos,images,keywords,external_ids"
        )

    async def get_tv_season(self, tv_id: int, season_number: int, language: str = "fr-FR") -> Optional[Dict]:
        """
        Obtenir les détails d'une saison

        Args:
            tv_id: ID TMDB de la série
            season_number: Numéro de la saison
            language: Code de langue

        Returns:
            Détails de la saison ou None en cas d'erreur
        """
        return await self._request(
            f"/tv/{tv_id}/season/{season_number}",
            language=language
        )

    async def get_tv_episode(self, tv_id: int, season_number: int, episode_number: int, language: str = "fr-FR") -> Optional[Dict]:
        """
        Obtenir les détails d'un épisode

        Args:
            tv_id: ID TMDB de la série
            season_number: Numéro de la saison
            episode_number: Numéro de l'épisode
            language: Code de langue

        Returns:
            Détails de l'épisode ou None en cas d'erreur
        """
        return await self._request(
            f"/tv/{tv_id}/season/{season_number}/episode/{episode_number}",
            language=language
        )

    async def get_popular_tv(self, page: int = 1, language: str = "fr-FR") -> Optional[Dict]:
        """Obtenir les séries populaires"""
        return await self._request(
            "/tv/popular",
            page=page,
            language=language
        )

    async def get_top_rated_tv(self, page: int = 1, language: str = "fr-FR") -> Optional[Dict]:
        """Obtenir les séries les mieux notées"""
        return await self._request(
            "/tv/top_rated",
            page=page,
            language=language
        )

    async def get_on_the_air_tv(self, page: int = 1, language: str = "fr-FR") -> Optional[Dict]:
        """Obtenir les séries actuellement diffusées"""
        return await self._request(
            "/tv/on_the_air",
            page=page,
            language=language
        )

    async def get_airing_today_tv(self, page: int = 1, language: str = "fr-FR") -> Optional[Dict]:
        """Obtenir les séries diffusées aujourd'hui"""
        return await self._request(
            "/tv/airing_today",
            page=page,
            language=language
        )

    # ========================================================================
    # GENRES
    # ========================================================================

    async def get_movie_genres(self, language: str = "fr-FR") -> Optional[Dict]:
        """Obtenir la liste des genres de films"""
        return await self._request(
            "/genre/movie/list",
            language=language
        )

    async def get_tv_genres(self, language: str = "fr-FR") -> Optional[Dict]:
        """Obtenir la liste des genres de séries"""
        return await self._request(
            "/genre/tv/list",
            language=language
        )

    # ========================================================================
    # IMAGES
    # ========================================================================

    def get_image_url(self, path: Optional[str], size: str = "original") -> Optional[str]:
        """
        Construire l'URL complète d'une image

        Args:
            path: Chemin de l'image (ex: "/abc123.jpg")
            size: Taille de l'image (w92, w154, w185, w342, w500, w780, original)

        Returns:
            URL complète de l'image ou None
        """
        if not path:
            return None
        return f"{self.IMAGE_BASE_URL}/{size}{path}"

    def get_poster_url(self, path: Optional[str], size: str = "w500") -> Optional[str]:
        """Obtenir l'URL d'un poster"""
        return self.get_image_url(path, size)

    def get_backdrop_url(self, path: Optional[str], size: str = "w1280") -> Optional[str]:
        """Obtenir l'URL d'un backdrop"""
        return self.get_image_url(path, size)

    def get_profile_url(self, path: Optional[str], size: str = "w185") -> Optional[str]:
        """Obtenir l'URL d'une photo de profil"""
        return self.get_image_url(path, size)


# Instance globale du service
tmdb_service = TMDBService() if settings.TMDB_API_KEY or settings.TMDB_API_READ_TOKEN else None
