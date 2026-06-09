"""
main.py
Point d'entrée de l'application FastAPI — Snake Évolution Backend.

Démarrage :
    uvicorn app.main:app --reload --port 8000
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db, SessionLocal
from app.routers import players_router, scores_router, levels_router
from app.services.level_generator import get_or_generate
from app.models.level import Level


# ─── Lifespan : init DB + seed des 10 premiers niveaux ────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Exécuté au démarrage du serveur :
      1. Crée les tables SQLite si elles n'existent pas.
      2. Pré-génère les 10 premiers niveaux pour éviter
         la latence de génération lors de la première requête.
    """
    init_db()
    _seed_initial_levels()
    yield
    # (optionnel) cleanup au shutdown


def _seed_initial_levels():
    db = SessionLocal()
    try:
        for n in range(1, 11):
            exists = db.query(Level).filter(Level.number == n).first()
            if not exists:
                data = get_or_generate(n)
                level = Level(
                    number=data["number"],
                    grid_width=data["grid_width"],
                    grid_height=data["grid_height"],
                    obstacles=data["obstacles"],
                    base_speed_ms=data["base_speed_ms"],
                    food_count=data["food_count"],
                    food_weights=data["food_weights"],
                    name=data["name"],
                )
                db.add(level)
        db.commit()
    finally:
        db.close()


# ─── Application ──────────────────────────────────────────────────────────

app = FastAPI(
    title="Snake Évolution — API",
    description=(
        "Backend FastAPI pour Snake Évolution : "
        "gestion des joueurs, scores, leaderboard et génération de niveaux."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# ─── CORS (dev : tout autoriser, prod : restreindre à l'origine React) ─────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Routers ──────────────────────────────────────────────────────────────

app.include_router(players_router)
app.include_router(scores_router)
app.include_router(levels_router)


# ─── Routes utilitaires ───────────────────────────────────────────────────

@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "Snake Évolution API is running 🐍"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}