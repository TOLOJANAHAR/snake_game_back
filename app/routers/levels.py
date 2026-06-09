"""
routers/levels.py
Endpoints pour récupérer et générer les niveaux (grille + obstacles).
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.level import Level
from app.schemas.level import LevelRead, LevelCreate, Cell
from app.services.level_generator import get_or_generate

router = APIRouter(prefix="/levels", tags=["Levels"])


def _seed_level_if_missing(db: Session, level_number: int) -> Level:
    """
    Cherche le niveau en DB. S'il n'existe pas, le génère
    et le persiste automatiquement.
    """
    level = db.query(Level).filter(Level.number == level_number).first()
    if level:
        return level

    data = get_or_generate(level_number)
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
    db.refresh(level)
    return level


# ─── GET /levels/{number} ─────────────────────────────────────────────────

@router.get("/{level_number}", response_model=LevelRead)
def get_level(level_number: int, db: Session = Depends(get_db)):
    """
    Retourne la configuration d'un niveau (grille, obstacles, vitesse…).
    Si le niveau n'existe pas encore en base, il est généré à la volée.
    """
    if level_number < 1:
        raise HTTPException(status_code=400, detail="Le numéro de niveau doit être ≥ 1.")
    level = _seed_level_if_missing(db, level_number)
    return level


# ─── GET /levels ──────────────────────────────────────────────────────────

@router.get("/", response_model=List[LevelRead])
def list_levels(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Liste tous les niveaux présents en base."""
    return db.query(Level).order_by(Level.number).offset(skip).limit(limit).all()


# ─── POST /levels/generate ────────────────────────────────────────────────

@router.post("/generate/{level_number}", response_model=LevelRead)
def force_generate_level(
    level_number: int,
    seed: int | None = Query(None),
    db: Session = Depends(get_db),
):
    """
    (Re)génère un niveau avec un seed optionnel.
    Utile pour les admins ou les tests.
    Ecrase le niveau existant s'il y en a un.
    """
    if level_number < 1:
        raise HTTPException(status_code=400, detail="Numéro de niveau invalide.")

    from app.services.level_generator import generate_level
    data = generate_level(level_number, seed=seed)

    existing = db.query(Level).filter(Level.number == level_number).first()
    if existing:
        existing.grid_width = data["grid_width"]
        existing.grid_height = data["grid_height"]
        existing.obstacles = data["obstacles"]
        existing.base_speed_ms = data["base_speed_ms"]
        existing.food_count = data["food_count"]
        existing.food_weights = data["food_weights"]
        existing.name = data["name"]
        db.commit()
        db.refresh(existing)
        return existing

    level = Level(**{k: v for k, v in data.items()})
    db.add(level)
    db.commit()
    db.refresh(level)
    return level


# ─── GET /levels/{number}/obstacles ───────────────────────────────────────

@router.get("/{level_number}/obstacles", response_model=List[Cell])
def get_obstacles(level_number: int, db: Session = Depends(get_db)):
    """Retourne uniquement la liste des obstacles d'un niveau (payload léger)."""
    level = _seed_level_if_missing(db, level_number)
    return level.obstacles