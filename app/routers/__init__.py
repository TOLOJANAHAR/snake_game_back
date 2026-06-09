# routers/__init__.py
from app.routers.players import router as players_router
from app.routers.scores import router as scores_router
from app.routers.levels import router as levels_router

__all__ = ["players_router", "scores_router", "levels_router"]
