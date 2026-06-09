from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.player import Player
from app.schemas.player import PlayerCreate, PlayerRead, PlayerStats
from app.services.leaderboard import get_player_stats

router = APIRouter(prefix="/players", tags=["Players"])


#POST /players

@router.post("/", response_model=PlayerRead, status_code=status.HTTP_201_CREATED)
def create_player(payload: PlayerCreate, db: Session = Depends(get_db)):

    existing = db.query(Player).filter(Player.username == payload.username).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Le username '{payload.username}' est déjà utilisé.",
        )
    player = Player(username=payload.username)
    db.add(player)
    db.commit()
    db.refresh(player)
    return player


#GET /players/{id}

@router.get("/{player_id}", response_model=PlayerRead)
def get_player(player_id: int, db: Session = Depends(get_db)):
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Joueur introuvable.")
    return player


#GET /players/username/{username}

@router.get("/username/{username}", response_model=PlayerRead)
def get_player_by_username(username: str, db: Session = Depends(get_db)):
    """Recherche un joueur par son username (utile au login)."""
    player = db.query(Player).filter(Player.username == username).first()
    if not player:
        raise HTTPException(status_code=404, detail="Joueur introuvable.")
    return player


#GET /players/{id}/stats

@router.get("/{player_id}/stats", response_model=PlayerStats)
def player_stats(player_id: int, db: Session = Depends(get_db)):
    """Retourne les statistiques agrégées d'un joueur."""
    stats = get_player_stats(db, player_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Joueur introuvable.")
    return stats


#DELETE /players/{id

@router.delete("/{player_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_player(player_id: int, db: Session = Depends(get_db)):
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Joueur introuvable.")
    db.delete(player)
    db.commit()