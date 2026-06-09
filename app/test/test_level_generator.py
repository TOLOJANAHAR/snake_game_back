"""
tests/test_level_generator.py
Tests unitaires pour le générateur de niveaux.
"""
import pytest
from collections import deque
from app.services.level_generator import (
    generate_level,
    get_or_generate,
    _is_connected,
    _is_safe_zone,
    SNAKE_START,
    SAFE_RADIUS,
    GRID_W,
    GRID_H,
)


# ─── _is_safe_zone ────────────────────────────────────────────────────────

def test_safe_zone_center():
    sx, sy = SNAKE_START
    assert _is_safe_zone(sx, sy) is True

def test_safe_zone_edge():
    sx, sy = SNAKE_START
    assert _is_safe_zone(sx + SAFE_RADIUS, sy) is True

def test_safe_zone_outside():
    sx, sy = SNAKE_START
    assert _is_safe_zone(sx + SAFE_RADIUS + 1, sy) is False


# ─── _is_connected ────────────────────────────────────────────────────────

def test_connected_empty_grid():
    assert _is_connected(set(), GRID_W, GRID_H) is True

def test_connected_one_obstacle():
    obstacles = {(5, 5)}
    assert _is_connected(obstacles, GRID_W, GRID_H) is True

def test_disconnected_wall():
    # Mur vertical complet qui coupe la grille en deux
    obstacles = {(5, y) for y in range(GRID_H)}
    assert _is_connected(obstacles, GRID_W, GRID_H) is False


# ─── generate_level ───────────────────────────────────────────────────────

@pytest.mark.parametrize("level_num", [1, 3, 5, 8, 10])
def test_generate_returns_valid_structure(level_num):
    data = generate_level(level_num)
    assert "number" in data
    assert "obstacles" in data
    assert "base_speed_ms" in data
    assert "food_weights" in data
    assert data["number"] == level_num

def test_level_1_no_obstacles():
    """Le niveau 1 est toujours libre d'obstacles (density=0)."""
    data = generate_level(1)
    assert data["obstacles"] == []

def test_obstacles_increase_with_level():
    data_low = generate_level(2, seed=99)
    data_high = generate_level(9, seed=99)
    assert len(data_high["obstacles"]) >= len(data_low["obstacles"])

def test_obstacles_not_in_safe_zone():
    data = generate_level(10, seed=42)
    sx, sy = SNAKE_START
    for obs in data["obstacles"]:
        assert not (abs(obs["x"] - sx) <= SAFE_RADIUS and abs(obs["y"] - sy) <= SAFE_RADIUS), \
            f"Obstacle {obs} dans la safe zone !"

def test_grid_remains_connected():
    """Vérifie que la grille générée est toujours connexe (jouable)."""
    for n in [3, 5, 7, 10]:
        data = generate_level(n, seed=n * 7)
        obstacles = {(o["x"], o["y"]) for o in data["obstacles"]}
        assert _is_connected(obstacles, GRID_W, GRID_H), \
            f"Niveau {n} grille non connexe !"

def test_food_weights_sum_to_one():
    for n in [1, 5, 10]:
        data = generate_level(n)
        total = sum(data["food_weights"].values())
        assert abs(total - 1.0) < 0.01, f"Poids food niveau {n} ne somment pas à 1 : {total}"

def test_speed_decreases_with_level():
    speeds = [generate_level(n)["base_speed_ms"] for n in range(1, 11)]
    for i in range(len(speeds) - 1):
        assert speeds[i] >= speeds[i + 1], "La vitesse doit augmenter (ms diminue) avec le niveau"

def test_get_or_generate_deterministic():
    """Même niveau → même résultat (seed fixe)."""
    a = get_or_generate(5)
    b = get_or_generate(5)
    assert a["obstacles"] == b["obstacles"]