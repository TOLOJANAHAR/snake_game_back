"""
tests/test_api.py
Tests d'intégration des endpoints REST.
"""
import pytest


# ─── Health ───────────────────────────────────────────────────────────────

def test_root(client):
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200


# ─── Players ──────────────────────────────────────────────────────────────

def test_create_player(client):
    r = client.post("/players/", json={"username": "neo"})
    assert r.status_code == 201
    data = r.json()
    assert data["username"] == "neo"
    assert "id" in data

def test_create_player_duplicate(client):
    client.post("/players/", json={"username": "trinity"})
    r = client.post("/players/", json={"username": "trinity"})
    assert r.status_code == 409

def test_get_player(client):
    r = client.post("/players/", json={"username": "morpheus"})
    pid = r.json()["id"]
    r2 = client.get(f"/players/{pid}")
    assert r2.status_code == 200
    assert r2.json()["username"] == "morpheus"

def test_get_player_not_found(client):
    r = client.get("/players/99999")
    assert r.status_code == 404

def test_get_player_by_username(client):
    client.post("/players/", json={"username": "agent_smith"})
    r = client.get("/players/username/agent_smith")
    assert r.status_code == 200

def test_player_stats_empty(client):
    r = client.post("/players/", json={"username": "oracle"})
    pid = r.json()["id"]
    r2 = client.get(f"/players/{pid}/stats")
    assert r2.status_code == 200
    data = r2.json()
    assert data["total_games"] == 0
    assert data["best_score"] == 0

def test_delete_player(client):
    r = client.post("/players/", json={"username": "to_delete"})
    pid = r.json()["id"]
    r2 = client.delete(f"/players/{pid}")
    assert r2.status_code == 204
    r3 = client.get(f"/players/{pid}")
    assert r3.status_code == 404


# ─── Scores ───────────────────────────────────────────────────────────────

def _create_player(client, username):
    return client.post("/players/", json={"username": username}).json()["id"]

def test_submit_score(client):
    pid = _create_player(client, "scorer_1")
    payload = {
        "player_id": pid,
        "points": 250,
        "level_reached": 3,
        "snake_length": 8,
        "duration_seconds": 45.5,
        "evolution_stage": "serpent",
        "death_cause": "wall",
    }
    r = client.post("/scores/", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert data["points"] == 250
    assert data["evolution_stage"] == "serpent"

def test_submit_score_unknown_player(client):
    r = client.post("/scores/", json={
        "player_id": 99999,
        "points": 100,
        "level_reached": 1,
        "snake_length": 3,
        "duration_seconds": 10.0,
    })
    assert r.status_code == 404

def test_compute_score_endpoint(client):
    r = client.post("/scores/compute?apples=5&level=3&duration=30&snake_length=8")
    assert r.status_code == 200
    data = r.json()
    assert "points" in data
    assert data["points"] > 0
    assert data["evolution_stage"] == "serpent"

def test_leaderboard(client):
    pid = _create_player(client, "top_player")
    client.post("/scores/", json={
        "player_id": pid, "points": 9999,
        "level_reached": 10, "snake_length": 20,
        "duration_seconds": 300.0, "evolution_stage": "dragon",
    })
    r = client.get("/scores/leaderboard?limit=5")
    assert r.status_code == 200
    entries = r.json()
    assert len(entries) >= 1
    assert entries[0]["rank"] == 1

def test_scores_by_player(client):
    pid = _create_player(client, "history_player")
    for pts in [100, 200, 300]:
        client.post("/scores/", json={
            "player_id": pid, "points": pts,
            "level_reached": 1, "snake_length": 4,
            "duration_seconds": 20.0,
        })
    r = client.get(f"/scores/player/{pid}")
    assert r.status_code == 200
    assert len(r.json()) == 3


# ─── Levels ───────────────────────────────────────────────────────────────

def test_get_level_1(client):
    r = client.get("/levels/1")
    assert r.status_code == 200
    data = r.json()
    assert data["number"] == 1
    assert data["obstacles"] == []   # niveau 1 = pas d'obstacles

def test_get_level_5(client):
    r = client.get("/levels/5")
    assert r.status_code == 200
    data = r.json()
    assert data["number"] == 5
    assert data["base_speed_ms"] < 200   # plus rapide que niveau 1

def test_get_level_invalid(client):
    r = client.get("/levels/0")
    assert r.status_code == 400

def test_get_obstacles(client):
    r = client.get("/levels/5/obstacles")
    assert r.status_code == 200
    obstacles = r.json()
    assert isinstance(obstacles, list)
    for obs in obstacles:
        assert "x" in obs and "y" in obs

def test_force_generate_level(client):
    r = client.post("/levels/generate/15?seed=777")
    assert r.status_code == 200
    data = r.json()
    assert data["number"] == 15