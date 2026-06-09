from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class Score(Base):
    __tablename__ = "scores"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    points = Column(Integer, nullable=False, default=0)
    level_reached = Column(Integer, nullable=False, default=1)
    snake_length = Column(Integer, nullable=False, default=3)
    duration_seconds = Column(Float, nullable=False, default=0.0)

    # Puissance atteinte : "larve" | "serpent" | "dragon"
    evolution_stage = Column(String(20), nullable=False, default="larve")

    # Cause du game over
    death_cause = Column(String(30), nullable=True)  # "wall" | "self" | "skull" | None

    played_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relations
    player = relationship("Player", back_populates="scores")

    def __repr__(self):
        return f"<Score id={self.id} player_id={self.player_id} points={self.points}>"