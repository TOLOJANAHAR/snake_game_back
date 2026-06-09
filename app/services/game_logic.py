"""
game_logic.py
Valide et calcule les règles de jeu côté serveur :
  - calcul du score final
  - détermination du stade d'évolution
  - validation des power-ups
"""
from typing import Optional


# ─── Constantes ───────────────────────────────────────────────────────────

# Points par type de nourriture mangée
FOOD_POINTS = {
    "apple":  10,
    "golden": 30,
    "blue":   20,
    "red":    25,
    "skull":  -15,  # pénalité (si le joueur survit)
}

# Bonus de points multiplicateur selon le niveau
LEVEL_MULTIPLIER = {
    range(1, 4):  1.0,
    range(4, 7):  1.5,
    range(7, 10): 2.0,
    range(10, 99): 3.0,
}

# Stades d'évolution selon la longueur du serpent
EVOLUTION_THRESHOLDS = {
    "larve":   (1, 7),    # de 1 à 7 segments
    "serpent": (8, 14),   # de 8 à 14 segments
    "dragon":  (15, 999), # 15 segments et plus
}

# Durée des power-ups en secondes
POWERUP_DURATIONS = {
    "golden": 5.0,   # boost de vitesse
    "blue":   5.0,   # slow-mo
    "red":    1,     # 1 utilisation = traverser 1 mur
}

# Malus de longueur pour le crâne
SKULL_SHRINK = 3


# ─── Fonctions ────────────────────────────────────────────────────────────

def get_level_multiplier(level: int) -> float:
    for r, mult in LEVEL_MULTIPLIER.items():
        if level in r:
            return mult
    return 3.0


def compute_evolution_stage(snake_length: int) -> str:
    """Retourne le stade d'évolution selon la longueur du serpent."""
    for stage, (low, high) in EVOLUTION_THRESHOLDS.items():
        if low <= snake_length <= high:
            return stage
    return "dragon"


def compute_score(
    apples_eaten: int,
    golden_eaten: int,
    blue_eaten: int,
    red_eaten: int,
    skulls_eaten: int,
    level_reached: int,
    duration_seconds: float,
    snake_length: int,
) -> int:
    """
    Calcule le score final d'une partie.

    Formule :
      base = somme des points de chaque food × multiplicateur de niveau
      bonus_survie = durée_en_secondes × 0.5
      bonus_longueur = longueur_serpent × 5
      total = int(base + bonus_survie + bonus_longueur)
    """
    multiplier = get_level_multiplier(level_reached)

    base = (
        apples_eaten  * FOOD_POINTS["apple"]  +
        golden_eaten  * FOOD_POINTS["golden"] +
        blue_eaten    * FOOD_POINTS["blue"]   +
        red_eaten     * FOOD_POINTS["red"]    +
        skulls_eaten  * FOOD_POINTS["skull"]
    ) * multiplier

    bonus_survie   = duration_seconds * 0.5
    bonus_longueur = snake_length * 5

    total = int(max(0, base + bonus_survie + bonus_longueur))
    return total


def validate_powerup(food_type: str) -> dict:
    """
    Retourne la configuration d'effet d'un power-up.

    Retourne :
      {
        "type": str,
        "duration": float | int,
        "effect": str,        # description courte pour le frontend
        "speed_factor": float | None,
        "wall_pass": bool,
        "shrink": int,
      }
    """
    base = {
        "type": food_type,
        "duration": POWERUP_DURATIONS.get(food_type, 0),
        "effect": "",
        "speed_factor": None,
        "wall_pass": False,
        "shrink": 0,
    }

    if food_type == "golden":
        base["effect"] = "speed_boost"
        base["speed_factor"] = 1.6   # 60% plus rapide

    elif food_type == "blue":
        base["effect"] = "slow_motion"
        base["speed_factor"] = 0.4   # 60% plus lent (GSAP timeScale)

    elif food_type == "red":
        base["effect"] = "wall_pass"
        base["wall_pass"] = True

    elif food_type == "skull":
        base["effect"] = "shrink"
        base["shrink"] = SKULL_SHRINK

    elif food_type == "apple":
        base["effect"] = "grow"

    return base


def apply_food_effect(
    snake_length: int,
    food_type: str,
) -> tuple[int, Optional[str]]:
    """
    Applique l'effet de la nourriture sur la longueur du serpent.

    Retourne (nouvelle_longueur, death_cause | None).
    """
    if food_type == "apple":
        return snake_length + 1, None

    elif food_type in ("golden", "blue", "red"):
        return snake_length + 1, None   # grandit aussi + power-up activé

    elif food_type == "skull":
        new_length = snake_length - SKULL_SHRINK
        if new_length < 1:
            return 0, "skull"   # game over
        return new_length, None

    return snake_length, None