from pydantic import BaseModel, Field
from typing import List, Dict, Optional


class Cell(BaseModel):
    x: int = Field(..., ge=0)
    y: int = Field(..., ge=0)


class FoodWeights(BaseModel):
    apple: float = 0.55
    golden: float = 0.20
    blue: float = 0.12
    red: float = 0.08
    skull: float = 0.05


class LevelRead(BaseModel):
    id: int
    number: int
    grid_width: int
    grid_height: int
    obstacles: List[Cell]
    base_speed_ms: int
    food_count: int
    food_weights: Dict[str, float]
    name: Optional[str]

    model_config = {"from_attributes": True}


class LevelCreate(BaseModel):
    number: int = Field(..., ge=1)
    grid_width: int = Field(20, ge=10, le=50)
    grid_height: int = Field(20, ge=10, le=50)
    obstacles: List[Cell] = []
    base_speed_ms: int = Field(200, ge=50, le=500)
    food_count: int = Field(1, ge=1, le=5)
    food_weights: Dict[str, float] = Field(default_factory=lambda: {
        "apple": 0.55, "golden": 0.20,
        "blue": 0.12, "red": 0.08, "skull": 0.05
    })
    name: Optional[str] = None