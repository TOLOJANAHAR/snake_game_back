from sqlalchemy import Column, Integer, String, JSON, Float
from app.database import Base


class Level(Base):
    __tablename__ = "levels"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(Integer, unique=True, nullable=False, index=True)

    # Dimensions de la grille
    grid_width = Column(Integer, nullable=False, default=20)
    grid_height = Column(Integer, nullable=False, default=20)

    # Obstacles
    obstacles = Column(JSON, nullable=False, default=list)

    # Config de vitesse
    base_speed_ms = Column(Integer, nullable=False, default=200)

    # Nombre de food items simultanés sur la grille
    food_count = Column(Integer, nullable=False, default=1)

    # Probabilités d'apparition de chaque food
    food_weights = Column(JSON, nullable=False, default=lambda: {
        "apple": 0.55,
        "golden": 0.20,
        "blue": 0.12,
        "red": 0.08,
        "skull": 0.05,
    })

    # Nom
    name = Column(String(60), nullable=True)

    def __repr__(self):
        return f"<Level number={self.number} obstacles={len(self.obstacles or [])}>"