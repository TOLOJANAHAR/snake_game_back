from pydantic import BaseModel, Field
from datetime import datetime


class PlayerCreate(BaseModel):
    username: str = Field(..., min_length=2, max_length=50, pattern=r"^[a-zA-Z0-9_\-]+$")


class PlayerRead(BaseModel):
    id: int
    username: str
    created_at: datetime

    model_config = {"from_attributes": True}


class PlayerStats(BaseModel):
    player: PlayerRead
    total_games: int
    best_score: int
    best_level: int
    best_snake_length: int
    avg_duration_seconds: float