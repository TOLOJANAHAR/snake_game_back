from app.services.game_logic import (
    compute_score, compute_evolution_stage,
    validate_powerup, apply_food_effect,
)
from app.services.level_generator import generate_level, get_or_generate
from app.services.leaderboard import (
    save_score, get_global_leaderboard, get_player_stats,
    get_player_best, get_scores_by_player,
)

__all__ = [
    "compute_score", "compute_evolution_stage", "validate_powerup", "apply_food_effect",
    "generate_level", "get_or_generate",
    "save_score", "get_global_leaderboard", "get_player_stats",
    "get_player_best", "get_scores_by_player",
]