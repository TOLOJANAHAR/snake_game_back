"""
tests/test_game_logic.py
Tests unitaires pour le service game_logic.
"""
import pytest
from app.services.game_logic import (
    compute_score,
    compute_evolution_stage,
    validate_powerup,
    apply_food_effect,
    get_level_multiplier,
)


# ─── compute_evolution_stage ──────────────────────────────────────────────

def test_evolution_larve():
    assert compute_evolution_stage(1) == "larve"
    assert compute_evolution_stage(7) == "larve"

def test_evolution_serpent():
    assert compute_evolution_stage(8) == "serpent"
    assert compute_evolution_stage(14) == "serpent"

def test_evolution_dragon():
    assert compute_evolution_stage(15) == "dragon"
    assert compute_evolution_stage(100) == "dragon"


# ─── get_level_multiplier ─────────────────────────────────────────────────

def test_multiplier_early():
    assert get_level_multiplier(1) == 1.0
    assert get_level_multiplier(3) == 1.0

def test_multiplier_mid():
    assert get_level_multiplier(4) == 1.5
    assert get_level_multiplier(6) == 1.5

def test_multiplier_high():
    assert get_level_multiplier(7) == 2.0
    assert get_level_multiplier(10) == 3.0


# ─── compute_score ────────────────────────────────────────────────────────

def test_score_zero():
    score = compute_score(0, 0, 0, 0, 0, level_reached=1, duration_seconds=0, snake_length=3)
    # bonus_longueur = 3*5 = 15
    assert score == 15

def test_score_apples_only():
    # 5 pommes × 10pts × mult 1.0 + bonus_survie(10s×0.5=5) + bonus_longueur(5×5=25)
    score = compute_score(5, 0, 0, 0, 0, level_reached=1, duration_seconds=10, snake_length=5)
    assert score == int(50 * 1.0 + 5 + 25)

def test_score_with_skull_penalty():
    # Crâne = -15 pts × mult
    score = compute_score(3, 0, 0, 0, 1, level_reached=1, duration_seconds=0, snake_length=3)
    # base = (30 - 15) * 1.0 = 15, bonus_longueur = 15
    assert score == 30

def test_score_never_negative():
    score = compute_score(0, 0, 0, 0, 10, level_reached=1, duration_seconds=0, snake_length=1)
    assert score >= 0

def test_score_high_level_multiplier():
    score_l1 = compute_score(5, 0, 0, 0, 0, level_reached=1, duration_seconds=0, snake_length=3)
    score_l10 = compute_score(5, 0, 0, 0, 0, level_reached=10, duration_seconds=0, snake_length=3)
    assert score_l10 > score_l1


# ─── validate_powerup ─────────────────────────────────────────────────────

def test_powerup_apple():
    p = validate_powerup("apple")
    assert p["effect"] == "grow"
    assert p["wall_pass"] is False
    assert p["shrink"] == 0

def test_powerup_golden():
    p = validate_powerup("golden")
    assert p["effect"] == "speed_boost"
    assert p["speed_factor"] == 1.6
    assert p["duration"] == 5.0

def test_powerup_blue():
    p = validate_powerup("blue")
    assert p["effect"] == "slow_motion"
    assert p["speed_factor"] < 1.0

def test_powerup_red():
    p = validate_powerup("red")
    assert p["wall_pass"] is True

def test_powerup_skull():
    p = validate_powerup("skull")
    assert p["effect"] == "shrink"
    assert p["shrink"] == 3


# ─── apply_food_effect ────────────────────────────────────────────────────

def test_apply_apple():
    length, cause = apply_food_effect(5, "apple")
    assert length == 6
    assert cause is None

def test_apply_golden():
    length, cause = apply_food_effect(5, "golden")
    assert length == 6
    assert cause is None

def test_apply_skull_survives():
    length, cause = apply_food_effect(5, "skull")
    assert length == 2   # 5 - 3
    assert cause is None

def test_apply_skull_game_over():
    length, cause = apply_food_effect(2, "skull")
    assert length == 0
    assert cause == "skull"

def test_apply_skull_exact_boundary():
    # longueur = 3, shrink = 3 → new = 0 → game over
    length, cause = apply_food_effect(3, "skull")
    assert cause == "skull"