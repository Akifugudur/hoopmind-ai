"""
Database Seeder
Run once to populate PostgreSQL with generated NBA data.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import logging
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import Team, Player, Game, Shot, AdvancedStats
from data.generate_data import (
    generate_teams, generate_players, generate_games,
    generate_shots, generate_advanced_stats
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def seed(db: Session) -> None:
    # ── Check if already seeded ──────────────────────────────────
    if db.query(Team).count() > 0:
        logger.info("Database already seeded. Skipping.")
        return

    logger.info("🌱 Seeding database...")

    # ── Teams ────────────────────────────────────────────────────
    logger.info("Inserting teams...")
    team_data = generate_teams()
    team_objs = [Team(**t) for t in team_data]
    db.add_all(team_objs)
    db.flush()
    team_ids = [t.id for t in team_objs]
    team_map = {t.abbreviation: t.id for t in team_objs}
    logger.info(f"  ✓ {len(team_objs)} teams inserted")

    # ── Players ──────────────────────────────────────────────────
    logger.info("Inserting players...")
    player_data = generate_players({abbr: id_ for abbr, id_ in team_map.items()})
    player_objs = [Player(**p) for p in player_data]
    db.add_all(player_objs)
    db.flush()
    player_ids = [p.id for p in player_objs]
    logger.info(f"  ✓ {len(player_objs)} players inserted")

    # ── Games ────────────────────────────────────────────────────
    logger.info("Inserting games...")
    game_data = generate_games(team_ids, n_games=300)
    game_objs = [Game(**g) for g in game_data]
    db.add_all(game_objs)
    db.flush()
    game_ids = [g.id for g in game_objs]
    logger.info(f"  ✓ {len(game_objs)} games inserted")

    # ── Shots ────────────────────────────────────────────────────
    logger.info("Generating shot data (this may take a moment)...")
    from data.generate_data import NBA_PLAYERS
    shot_df = generate_shots(player_data, player_ids, game_ids, n_shots=60000)

    # Bulk insert shots in batches of 5000
    BATCH = 5000
    total = 0
    for i in range(0, len(shot_df), BATCH):
        batch = shot_df.iloc[i:i+BATCH]
        shot_records = []
        for _, row in batch.iterrows():
            shot_records.append(Shot(
                player_id=int(row["player_id"]),
                game_id=int(row["game_id"]),
                loc_x=float(row["loc_x"]),
                loc_y=float(row["loc_y"]),
                shot_distance=float(row["shot_distance"]),
                shot_angle=float(row["shot_angle"]),
                shot_type=str(row["shot_type"]),
                shot_zone=str(row["shot_zone"]),
                action_type=str(row["action_type"]),
                is_three_pointer=bool(row["is_three_pointer"]),
                is_catch_and_shoot=bool(row["is_catch_and_shoot"]),
                quarter=int(row["quarter"]),
                time_remaining_seconds=float(row["time_remaining_seconds"]),
                shot_clock=float(row["shot_clock"]) if row["shot_clock"] is not None else None,
                defender_distance=float(row["defender_distance"]),
                dribbles_before_shot=int(row["dribbles_before_shot"]),
                touch_time=float(row["touch_time"]),
                score_margin=int(row["score_margin"]),
                is_home=bool(row["is_home"]),
                shot_made=bool(row["shot_made"]),
                shot_value=int(row["shot_value"]),
            ))
        db.add_all(shot_records)
        db.flush()
        total += len(shot_records)
        logger.info(f"  ... {total:,} shots inserted")

    logger.info(f"  ✓ {total:,} shots total")

    # ── Advanced Stats ───────────────────────────────────────────
    logger.info("Inserting advanced stats...")
    adv_data = generate_advanced_stats(player_ids, player_data)
    adv_objs = [AdvancedStats(**a) for a in adv_data]
    db.add_all(adv_objs)

    # ── Commit ───────────────────────────────────────────────────
    db.commit()
    logger.info("✅ Database seeding complete!")
    logger.info(f"   Teams: {len(team_objs)} | Players: {len(player_objs)} | Games: {len(game_objs)} | Shots: {total:,}")


def main():
    db = SessionLocal()
    try:
        seed(db)
    except Exception as e:
        logger.error(f"Seeding failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
