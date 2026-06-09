"""
routers/scores.py
Endpoints pour soumettre et consulter les scores.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.player import Player
from app.schemas.score import ScoreCreate, ScoreRead, LeaderboardEntry
from app.services.leaderboard import (
    save_score,
    get_score_by_id,
    get_scores_by_player,
    get_global_leaderboard,
)
from app.services.game_logic import compute_score, compute_evolution_stage

router = APIRouter(prefix="/scores", tags=["Scores"])


# ─── POST /scores ──────────────────────────────────────────────────────────

@router.post("/", response_model=ScoreRead, status_code=status.HTTP_201_CREATED)
def submit_score(payload: ScoreCreate, db: Session = Depends(get_db)):
    """
    Soumet le score d'une partie terminée.
    Vérifie que le joueur existe, puis persiste le score.
    """
    player = db.query(Player).filter(Player.id == payload.player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Joueur introuvable.")

    score = save_score(db, payload)
    return score


# ─── POST /scores/compute ─────────────────────────────────────────────────

@router.post("/compute")
def compute_final_score(
    apples: int = Query(0, ge=0),
    golden: int = Query(0, ge=0),
    blue: int = Query(0, ge=0),
    red: int = Query(0, ge=0),
    skulls: int = Query(0, ge=0),
    level: int = Query(1, ge=1),
    duration: float = Query(0.0, ge=0),
    snake_length: int = Query(3, ge=1),
):
    """
    Calcule le score final à partir des statistiques de partie.
    Endpoint utilitaire appelé par le frontend en fin de partie.
    """
    total = compute_score(
        apples_eaten=apples,
        golden_eaten=golden,
        blue_eaten=blue,
        red_eaten=red,
        skulls_eaten=skulls,
        level_reached=level,
        duration_seconds=duration,
        snake_length=snake_length,
    )
    evolution = compute_evolution_stage(snake_length)
    return {
        "points": total,
        "evolution_stage": evolution,
        "level_reached": level,
        "snake_length": snake_length,
    }


# ─── GET /scores/leaderboard ──────────────────────────────────────────────

@router.get("/leaderboard", response_model=List[LeaderboardEntry])
def leaderboard(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Retourne le classement global (top scores toutes parties confondues)."""
    return get_global_leaderboard(db, limit=limit)


# ─── GET /scores/{id} ─────────────────────────────────────────────────────

@router.get("/{score_id}", response_model=ScoreRead)
def get_score(score_id: int, db: Session = Depends(get_db)):
    score = get_score_by_id(db, score_id)
    if not score:
        raise HTTPException(status_code=404, detail="Score introuvable.")
    return score


# ─── GET /scores/player/{player_id} ───────────────────────────────────────

@router.get("/player/{player_id}", response_model=List[ScoreRead])
def scores_by_player(
    player_id: int,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Retourne l'historique des parties d'un joueur."""
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Joueur introuvable.")
    return get_scores_by_player(db, player_id, limit=limit)