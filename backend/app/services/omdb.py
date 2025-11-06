"""Service pour l'intégration avec l'API OMDb (Open Movie Database)"""
import httpx
from typing import Optional, Dict, Any, List
from datetime import datetime

from app.config import settings


class OMDbService:
    """Service pour interagir avec l'API OMDb"""

    BASE_URL = "http://www.omdbapi.com/"

    def __init__(self):
        """Initialiser le service OMDb"""
        self.api_key = settings.OMDB_API_KEY

        if not self.api_key:
            raise ValueError("OMDB_API_KEY must be set in .env")

    async def _request(self, **params) -> Optional[Dict[str, Any]]:
        """
        Faire une requête à l'API OMDb

        Args:
            **params: Paramètres de requête

        Returns:
            Réponse JSON ou None en cas d'erreur
        """
        params["apikey"] = self.api_key

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    self.BASE_URL,
                    params=params,
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()

                # OMDb retourne une erreur dans le JSON si la requête échoue
                if data.get("Response") == "False":
                    print(f"OMDb API Error: {data.get('Error', 'Unknown error')}")
                    return None

                return data
            except httpx.HTTPError as e:
                print(f"OMDb API Error: {e}")
                return None

    # ========================================================================
    # SEARCH
    # ========================================================================

    async def search(self, query: str, media_type: Optional[str] = None, year: Optional[int] = None, page: int = 1) -> Optional[Dict]:
        """
        Rechercher films et séries

        Args:
            query: Terme de recherche
            media_type: Type de média ("movie", "series", "episode") ou None pour tous
            year: Année de sortie (optionnel)
            page: Numéro de page (1-100)

        Returns:
            Résultats de recherche ou None en cas d'erreur

        Response format:
        {
            "Search": [...],
            "totalResults": "123",
            "Response": "True"
        }
        """
        params = {
            "s": query,
            "page": page
        }

        if media_type:
            params["type"] = media_type

        if year:
            params["y"] = year

        return await self._request(**params)

    async def search_movies(self, query: str, year: Optional[int] = None, page: int = 1) -> Optional[Dict]:
        """Rechercher des films uniquement"""
        return await self.search(query=query, media_type="movie", year=year, page=page)

    async def search_series(self, query: str, year: Optional[int] = None, page: int = 1) -> Optional[Dict]:
        """Rechercher des séries uniquement"""
        return await self.search(query=query, media_type="series", year=year, page=page)

    # ========================================================================
    # GET DETAILS
    # ========================================================================

    async def get_by_imdb_id(self, imdb_id: str, plot: str = "full") -> Optional[Dict]:
        """
        Obtenir les détails par ID IMDb

        Args:
            imdb_id: ID IMDb (ex: "tt0111161")
            plot: "short" ou "full"

        Returns:
            Détails du film/série ou None en cas d'erreur
        """
        return await self._request(i=imdb_id, plot=plot)

    async def get_by_title(self, title: str, year: Optional[int] = None, media_type: Optional[str] = None, plot: str = "full") -> Optional[Dict]:
        """
        Obtenir les détails par titre

        Args:
            title: Titre du film/série
            year: Année (optionnel)
            media_type: "movie" ou "series" (optionnel)
            plot: "short" ou "full"

        Returns:
            Détails du film/série ou None en cas d'erreur
        """
        params = {
            "t": title,
            "plot": plot
        }

        if year:
            params["y"] = year

        if media_type:
            params["type"] = media_type

        return await self._request(**params)

    async def get_season(self, imdb_id: str, season_number: int) -> Optional[Dict]:
        """
        Obtenir les détails d'une saison

        Args:
            imdb_id: ID IMDb de la série
            season_number: Numéro de la saison

        Returns:
            Détails de la saison avec liste des épisodes
        """
        return await self._request(i=imdb_id, Season=season_number)

    async def get_episode(self, imdb_id: str, season: int, episode: int) -> Optional[Dict]:
        """
        Obtenir les détails d'un épisode

        Args:
            imdb_id: ID IMDb de la série
            season: Numéro de saison
            episode: Numéro d'épisode

        Returns:
            Détails de l'épisode
        """
        return await self._request(i=imdb_id, Season=season, Episode=episode)

    # ========================================================================
    # UTILITY FUNCTIONS
    # ========================================================================

    def parse_rating(self, rating_str: Optional[str]) -> Optional[float]:
        """
        Convertir une note OMDb (ex: "8.5/10") en float

        Args:
            rating_str: Note au format "X.X/10" ou "N/A"

        Returns:
            Note en float ou None
        """
        if not rating_str or rating_str == "N/A":
            return None

        try:
            if "/" in rating_str:
                return float(rating_str.split("/")[0])
            return float(rating_str)
        except (ValueError, IndexError):
            return None

    def parse_runtime(self, runtime_str: Optional[str]) -> Optional[int]:
        """
        Convertir une durée OMDb (ex: "142 min") en int

        Args:
            runtime_str: Durée au format "XXX min" ou "N/A"

        Returns:
            Durée en minutes ou None
        """
        if not runtime_str or runtime_str == "N/A":
            return None

        try:
            return int(runtime_str.replace(" min", "").strip())
        except ValueError:
            return None

    def parse_year(self, year_str: Optional[str]) -> Optional[int]:
        """
        Extraire l'année (ex: "2010", "2010–2015", "2010–")

        Args:
            year_str: Année au format OMDb

        Returns:
            Année en int ou None
        """
        if not year_str or year_str == "N/A":
            return None

        try:
            # Prendre la première année si c'est une plage
            year = year_str.split("–")[0].strip()
            return int(year)
        except (ValueError, IndexError):
            return None

    def parse_genres(self, genre_str: Optional[str]) -> List[str]:
        """
        Convertir les genres OMDb (ex: "Action, Drama") en liste

        Args:
            genre_str: Genres séparés par virgules

        Returns:
            Liste de genres
        """
        if not genre_str or genre_str == "N/A":
            return []

        return [g.strip() for g in genre_str.split(",")]

    def parse_ratings(self, ratings: Optional[List[Dict]]) -> Dict[str, str]:
        """
        Parser les différentes sources de notation

        Args:
            ratings: Liste des notations depuis OMDb

        Returns:
            Dict avec les sources de notation
        """
        if not ratings:
            return {}

        result = {}
        for rating in ratings:
            source = rating.get("Source", "")
            value = rating.get("Value", "")

            if "Internet Movie Database" in source:
                result["imdb"] = value
            elif "Rotten Tomatoes" in source:
                result["rotten_tomatoes"] = value
            elif "Metacritic" in source:
                result["metacritic"] = value

        return result

    def get_poster_url(self, poster_path: Optional[str]) -> Optional[str]:
        """
        Obtenir l'URL du poster (OMDb retourne déjà l'URL complète)

        Args:
            poster_path: URL du poster depuis OMDb

        Returns:
            URL du poster ou None
        """
        if not poster_path or poster_path == "N/A":
            return None
        return poster_path


# Instance globale du service
omdb_service = OMDbService() if settings.OMDB_API_KEY else None
