"""Routes de l'API"""
from fastapi import APIRouter

from app.routes import auth, movies, series, search

# Créer le router principal
api_router = APIRouter()

# Enregistrer les routes d'authentification
api_router.include_router(auth.router)

# Enregistrer les routes pour les films et séries
api_router.include_router(movies.router)
api_router.include_router(series.router)

# Enregistrer la route de recherche intelligente
api_router.include_router(search.router)

# TODO: Ajouter d'autres routes
# from app.routes import users, tracking
# api_router.include_router(users.router, prefix="/users", tags=["users"])
# api_router.include_router(tracking.router, prefix="/tracking", tags=["tracking"])
