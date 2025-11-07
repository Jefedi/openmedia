"""Service pour l'intégration avec l'API TMDB (The Movie Database)"""
import httpx
from typing import Optional, Dict, Any, List
from app.config import settings


class TMDBService:
    """Service pour interagir avec l'API TMDB"""

    BASE_URL = "https://api.themoviedb.org/3"
    IMAGE_BASE_URL = "https://image.tmdb.org/t/p"

    def __init__(self):
        """Initialiser le service TMDB"""
        self.api_key = settings.TMDB_API_KEY

        if not self.api_key:
            raise ValueError("TMDB_API_KEY must be set in .env")

    async def _request(self, endpoint: str, **params) -> Optional[Dict[str, Any]]:
        """
        Faire une requête à l'API TMDB

        Args:
            endpoint: Endpoint de l'API (ex: "/movie/123")
            **params: Paramètres de requête

        Returns:
            Réponse JSON ou None en cas d'erreur
        """
        params["api_key"] = self.api_key
        params.setdefault("language", "fr-FR")  # Français par défaut

        url = f"{self.BASE_URL}{endpoint}"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params, timeout=30.0)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                print(f"TMDB API Error: {e}")
                return None

    # ========================================================================
    # MOVIES
    # ========================================================================

    async def get_movie_credits(self, tmdb_id: int) -> Optional[Dict]:
        """
        Obtenir le cast et crew d'un film

        Args:
            tmdb_id: ID TMDB du film

        Returns:
            {
                "cast": [{"id", "name", "character", "order", "profile_path"}, ...],
                "crew": [{"id", "name", "job", "department", "profile_path"}, ...]
            }
        """
        return await self._request(f"/movie/{tmdb_id}/credits")

    async def get_movie_videos(self, tmdb_id: int) -> Optional[Dict]:
        """
        Obtenir les vidéos (trailers, teasers) d'un film

        Args:
            tmdb_id: ID TMDB du film

        Returns:
            {
                "results": [{
                    "key": "xyz",  # YouTube video ID
                    "name": "Official Trailer",
                    "type": "Trailer",
                    "site": "YouTube",
                    "size": 1080,
                    "official": true
                }, ...]
            }
        """
        return await self._request(f"/movie/{tmdb_id}/videos")

    async def get_movie_details(self, tmdb_id: int) -> Optional[Dict]:
        """Obtenir tous les détails d'un film"""
        return await self._request(f"/movie/{tmdb_id}")

    # ========================================================================
    # TV SERIES
    # ========================================================================

    async def get_series_credits(self, tmdb_id: int) -> Optional[Dict]:
        """
        Obtenir le cast et crew d'une série

        Args:
            tmdb_id: ID TMDB de la série

        Returns:
            {
                "cast": [{"id", "name", "character", "order", "profile_path"}, ...],
                "crew": [{"id", "name", "job", "department", "profile_path"}, ...]
            }
        """
        return await self._request(f"/tv/{tmdb_id}/aggregate_credits")

    async def get_series_videos(self, tmdb_id: int) -> Optional[Dict]:
        """
        Obtenir les vidéos (trailers, teasers) d'une série

        Args:
            tmdb_id: ID TMDB de la série

        Returns:
            Format identique à get_movie_videos
        """
        return await self._request(f"/tv/{tmdb_id}/videos")

    async def get_series_details(self, tmdb_id: int) -> Optional[Dict]:
        """Obtenir tous les détails d'une série"""
        return await self._request(f"/tv/{tmdb_id}")

    # ========================================================================
    # PEOPLE / PERSONS
    # ========================================================================

    async def get_person_details(self, tmdb_person_id: int) -> Optional[Dict]:
        """
        Obtenir les détails d'une personne

        Args:
            tmdb_person_id: ID TMDB de la personne

        Returns:
            {
                "id": 123,
                "name": "Tom Hanks",
                "biography": "...",
                "birthday": "1956-07-09",
                "place_of_birth": "...",
                "profile_path": "/path.jpg",
                "imdb_id": "nm0000158"
            }
        """
        return await self._request(f"/person/{tmdb_person_id}")

    async def search_person(self, query: str) -> Optional[Dict]:
        """
        Rechercher une personne

        Args:
            query: Nom de la personne

        Returns:
            {"results": [{"id", "name", "profile_path"}, ...]}
        """
        return await self._request("/search/person", query=query)

    # ========================================================================
    # UTILITY FUNCTIONS
    # ========================================================================

    def get_image_url(self, path: Optional[str], size: str = "original") -> Optional[str]:
        """
        Construire l'URL complète d'une image TMDB

        Args:
            path: Chemin de l'image (ex: "/abc123.jpg")
            size: Taille de l'image
                - poster: "w92", "w154", "w185", "w342", "w500", "w780", "original"
                - backdrop: "w300", "w780", "w1280", "original"
                - profile: "w45", "w185", "h632", "original"

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

    def get_youtube_url(self, key: str) -> str:
        """
        Construire l'URL YouTube depuis une clé

        Args:
            key: Clé vidéo YouTube

        Returns:
            URL complète YouTube
        """
        return f"https://www.youtube.com/watch?v={key}"


# Instance globale du service
tmdb_service = TMDBService() if settings.TMDB_API_KEY else None
