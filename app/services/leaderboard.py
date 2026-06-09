"""
leaderboard.py
Service pour la gestion du classement global et des stats par joueur.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List

from app.models.score import Score
from app.models.player import Player
from app.schemas.score import LeaderboardEntry, ScoreCreate, ScoreRead
from app.schemas.player import PlayerStats, PlayerRead
from app.services.game_logic import compute_evolution_stage


#Scores

def save_score(db: Session, data: ScoreCreate) -> Score:
    evolution = compute_evolution_stage(data.snake_length)

    score = Score(
        player_id=data.player_id,
        points=data.points,
        level_reached=data.level_reached,
        snake_length=data.snake_length,
        duration_seconds=data.duration_seconds,
        evolution_stage=evolution,
        death_cause=data.death_cause,
    )
    db.add(score)
    db.commit()
    db.refresh(score)
    return score


def get_score_by_id(db: Session, score_id: int) -> Score | None:
    return db.query(Score).filter(Score.id == score_id).first()


def get_scores_by_player(db: Session, player_id: int, limit: int = 20) -> List[Score]:
    return (
        db.query(Score)
        .filter(Score.player_id == player_id)
        .order_by(desc(Score.played_at))
        .limit(limit)
        .all()
    )


#Leaderboard

def get_global_leaderboard(db: Session, limit: int = 10) -> List[LeaderboardEntry]:

    rows = (
        db.query(Score, Player.username)
        .join(Player, Score.player_id == Player.id)
        .order_by(desc(Score.points))
        .limit(limit)
        .all()
    )

    result = []
    for rank, (score, username) in enumerate(rows, start=1):
        result.append(LeaderboardEntry(
            rank=rank,
            username=username,
            points=score.points,
            level_reached=score.level_reached,
            snake_length=score.snake_length,
            evolution_stage=score.evolution_stage,
            played_at=score.played_at,
        ))
    return result


def get_player_best(db: Session, player_id: int) -> Score | None:
    return (
        db.query(Score)
        .filter(Score.player_id == player_id)
        .order_by(desc(Score.points))
        .first()
    )


#Stats joueur

def get_player_stats(db: Session, player_id: int) -> PlayerStats | None:
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        return None

    agg = (
        db.query(
            func.count(Score.id).label("total_games"),
            func.max(Score.points).label("best_score"),
            func.max(Score.level_reached).label("best_level"),
            func.max(Score.snake_length).label("best_length"),
            func.avg(Score.duration_seconds).label("avg_duration"),
        )
        .filter(Score.player_id == player_id)
        .one()
    )

    return PlayerStats(
        player=PlayerRead.model_validate(player),
        total_games=agg.total_games or 0,
        best_score=agg.best_score or 0,
        best_level=agg.best_level or 1,
        best_snake_length=agg.best_length or 3,
        avg_duration_seconds=round(agg.avg_duration or 0.0, 2),
    )