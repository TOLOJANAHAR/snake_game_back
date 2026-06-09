from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Literal


EvolutionStage = Literal["larve", "serpent", "dragon"]
DeathCause = Literal["wall", "self", "skull"]


class ScoreCreate(BaseModel):
    player_id: int
    points: int = Field(..., ge=0)
    level_reached: int = Field(..., ge=1)
    snake_length: int = Field(..., ge=1)
    duration_seconds: float = Field(..., ge=0.0)
    evolution_stage: EvolutionStage = "larve"
    death_cause: Optional[DeathCause] = None


class ScoreRead(BaseModel):
    id: int
    player_id: int
    points: int
    level_reached: int
    snake_length: int
    duration_seconds: float
    evolution_stage: EvolutionStage
    death_cause: Optional[DeathCause]
    played_at: datetime

    model_config = {"from_attributes": True}


class LeaderboardEntry(BaseModel):
    rank: int
    username: str
    points: int
    level_reached: int
    snake_length: int
    evolution_stage: EvolutionStage
    played_at: datetime