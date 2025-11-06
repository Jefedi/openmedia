"""Routes de l'API"""
from fastapi import APIRouter

from app.routes import auth

# Créer le router principal
api_router = APIRouter()

# Enregistrer les routes d'authentification
api_router.include_router(auth.router)

# TODO: Ajouter d'autres routes
# from app.routes import users, movies, series, tracking, search
# api_router.include_router(users.router, prefix="/users", tags=["users"])
# api_router.include_router(movies.router, prefix="/movies", tags=["movies"])
# api_router.include_router(series.router, prefix="/series", tags=["series"])
# api_router.include_router(tracking.router, prefix="/tracking", tags=["tracking"])
# api_router.include_router(search.router, prefix="/search", tags=["search"])
