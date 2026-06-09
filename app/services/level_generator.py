import random
from collections import deque
from typing import List, Dict, Tuple, Any


#Constantes par niveau 

LEVEL_CONFIGS: Dict[int, Dict[str, Any]] = {
    1:  {"obstacle_density": 0.00, "speed_ms": 220, "food_count": 1},
    2:  {"obstacle_density": 0.04, "speed_ms": 205, "food_count": 1},
    3:  {"obstacle_density": 0.07, "speed_ms": 190, "food_count": 1},
    4:  {"obstacle_density": 0.09, "speed_ms": 175, "food_count": 2},
    5:  {"obstacle_density": 0.11, "speed_ms": 160, "food_count": 2},
    6:  {"obstacle_density": 0.13, "speed_ms": 148, "food_count": 2},
    7:  {"obstacle_density": 0.15, "speed_ms": 136, "food_count": 2},
    8:  {"obstacle_density": 0.17, "speed_ms": 124, "food_count": 3},
    9:  {"obstacle_density": 0.19, "speed_ms": 112, "food_count": 3},
    10: {"obstacle_density": 0.21, "speed_ms": 100, "food_count": 3},
}

FOOD_WEIGHTS_BY_LEVEL: Dict[int, Dict[str, float]] = {
    1:  {"apple": 0.70, "golden": 0.15, "blue": 0.10, "red": 0.04, "skull": 0.01},
    3:  {"apple": 0.60, "golden": 0.18, "blue": 0.12, "red": 0.06, "skull": 0.04},
    5:  {"apple": 0.55, "golden": 0.20, "blue": 0.12, "red": 0.08, "skull": 0.05},
    8:  {"apple": 0.48, "golden": 0.22, "blue": 0.13, "red": 0.10, "skull": 0.07},
    10: {"apple": 0.40, "golden": 0.25, "blue": 0.14, "red": 0.12, "skull": 0.09},
}

GRID_W = 20
GRID_H = 20
SNAKE_START = (10, 10)   
SAFE_RADIUS = 3        


#Helpers

def _is_safe_zone(x: int, y: int) -> bool:
    sx, sy = SNAKE_START
    return abs(x - sx) <= SAFE_RADIUS and abs(y - sy) <= SAFE_RADIUS


def _is_connected(grid: set, width: int, height: int) -> bool:

    free = {
        (x, y)
        for x in range(width)
        for y in range(height)
        if (x, y) not in grid
    }
    if not free:
        return False

    start = next(iter(free))
    visited = set()
    queue = deque([start])

    while queue:
        cell = queue.popleft()
        if cell in visited:
            continue
        visited.add(cell)
        cx, cy = cell
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = cx + dx, cy + dy
            if (nx, ny) in free and (nx, ny) not in visited:
                queue.append((nx, ny))

    return visited == free


def _get_food_weights(level: int) -> Dict[str, float]:
    milestones = sorted(FOOD_WEIGHTS_BY_LEVEL.keys())
    selected = milestones[0]
    for m in milestones:
        if level >= m:
            selected = m
    return FOOD_WEIGHTS_BY_LEVEL[selected]


#Générateur principal

def generate_level(
    level_number: int,
    width: int = GRID_W,
    height: int = GRID_H,
    seed: int | None = None,
) -> Dict[str, Any]:
    rng = random.Random(seed)

    cfg_key = min(level_number, 10)
    cfg = LEVEL_CONFIGS.get(cfg_key, LEVEL_CONFIGS[10])

    density = cfg["obstacle_density"]
    speed_ms = cfg["speed_ms"]
    food_count = cfg["food_count"]
    food_weights = _get_food_weights(level_number)

    total_cells = width * height
    target_obstacles = int(total_cells * density)

    obstacles: set[Tuple[int, int]] = set()
    attempts = 0
    max_attempts = target_obstacles * 10

    while len(obstacles) < target_obstacles and attempts < max_attempts:
        attempts += 1
        x = rng.randint(0, width - 1)
        y = rng.randint(0, height - 1)

        if _is_safe_zone(x, y):
            continue

        candidate = obstacles | {(x, y)}
        if _is_connected(candidate, width, height):
            obstacles.add((x, y))

    return {
        "number": level_number,
        "grid_width": width,
        "grid_height": height,
        "obstacles": [{"x": x, "y": y} for x, y in sorted(obstacles)],
        "base_speed_ms": speed_ms,
        "food_count": food_count,
        "food_weights": food_weights,
        "name": f"Niveau {level_number}",
    }


def get_or_generate(level_number: int) -> Dict[str, Any]:
    return generate_level(level_number, seed=level_number * 42)