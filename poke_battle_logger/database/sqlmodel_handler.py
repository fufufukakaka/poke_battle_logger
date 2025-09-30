import logging
import os
import random
import unicodedata
from typing import Dict, List, Tuple, Union

import pandas as pd
from sqlmodel import Session, and_, select
from tenacity import after_log, retry, stop_after_attempt

logger = logging.getLogger(__name__)

from poke_battle_logger.models import (
    Battle,
    BattlePokemonTeam,
    BattleSummary,
    BattleVideo,
    FaintedLog,
    InBattlePokemonLog,
    MessageLog,
    Season,
    SelectedMove,
    Trainer,
    get_engine,
    get_session,
)
from poke_battle_logger.types import Battle as BattleType
from poke_battle_logger.types import (
    BattleLog,
    InBattlePokemon,
    Message,
    PreBattlePokemon,
)

# Initialize pokemon name data
pokemon_name_df = pd.read_csv("data/pokemon_names.csv")
pokemon_japanese_to_no_dict = dict(
    zip(pokemon_name_df["Japanese"], pokemon_name_df["No."])
)


class SQLModelDatabaseHandler:
    """SQLModel-based database handler with modern async/await support."""

    def __init__(self) -> None:
        self.engine = get_engine()
        # Ensure tables exist
        self.create_tables()

    def create_tables(self) -> None:
        """Create all database tables."""
        from sqlmodel import SQLModel

        SQLModel.metadata.create_all(self.engine)

        # Initialize seasons if they don't exist
        with get_session() as session:
            existing_seasons = session.exec(select(Season)).all()
            if not existing_seasons:
                season3 = Season(
                    id=1,
                    season=3,
                    start_datetime="2023-02-01 09:00:00",
                    end_datetime="2023-03-01 09:00:00",
                )
                season4 = Season(
                    id=2,
                    season=4,
                    start_datetime="2023-03-01 09:00:00",
                    end_datetime="2023-04-01 09:00:00",
                )
                session.add(season3)
                session.add(season4)
                session.commit()

    @retry(stop=stop_after_attempt(5), after=after_log(logger, logging.ERROR))
    def insert_battle_id(self, battles: List[BattleType]) -> None:
        """Insert battle records."""
        try:
            with get_session() as session:
                for _battle in battles:
                    battle = Battle(
                        battle_id=_battle.battle_id, trainer_id=_battle.trainer_id
                    )
                    session.add(battle)
                session.commit()
                logger.info(f"Successfully inserted {len(battles)} battles")
        except Exception as e:
            logger.error(f"Error inserting battles: {e}")
            logger.error(f"Battle IDs: {[b.battle_id for b in battles]}")
            raise

    @retry(stop=stop_after_attempt(5), after=after_log(logger, logging.ERROR))
    def insert_battle_summary(self, battle_summary: List[BattleLog]) -> None:
        """Insert battle summary records."""
        with get_session() as session:
            for _battle_summary in battle_summary:
                summary = BattleSummary(
                    battle_id=_battle_summary.battle_id,
                    created_at=_battle_summary.created_at,
                    win_or_lose=_battle_summary.win_or_lose,
                    next_rank=_battle_summary.next_rank,
                    your_team=unicodedata.normalize("NFC", _battle_summary.your_team),
                    opponent_team=unicodedata.normalize(
                        "NFC", _battle_summary.opponent_team
                    ),
                    your_pokemon_1=unicodedata.normalize(
                        "NFC", _battle_summary.your_pokemon_1
                    ),
                    your_pokemon_2=unicodedata.normalize(
                        "NFC", _battle_summary.your_pokemon_2
                    ),
                    your_pokemon_3=unicodedata.normalize(
                        "NFC", _battle_summary.your_pokemon_3
                    ),
                    opponent_pokemon_1=unicodedata.normalize(
                        "NFC", _battle_summary.opponent_pokemon_1
                    ),
                    opponent_pokemon_2=unicodedata.normalize(
                        "NFC", _battle_summary.opponent_pokemon_2
                    ),
                    opponent_pokemon_3=unicodedata.normalize(
                        "NFC", _battle_summary.opponent_pokemon_3
                    ),
                    video=_battle_summary.video,
                    memo="",
                )
                session.add(summary)
            session.commit()

    @retry(stop=stop_after_attempt(5), after=after_log(logger, logging.ERROR))
    def insert_battle_pokemon_team(
        self, battle_pokemon_team: List[PreBattlePokemon]
    ) -> None:
        """Insert battle pokemon team records."""
        with get_session() as session:
            for _battle_pokemon_team in battle_pokemon_team:
                pokemon_team = BattlePokemonTeam(
                    battle_id=_battle_pokemon_team.battle_id,
                    team=_battle_pokemon_team.team,
                    pokemon_name=unicodedata.normalize(
                        "NFC", _battle_pokemon_team.pokemon_name
                    ),
                )
                session.add(pokemon_team)
            session.commit()

    @retry(stop=stop_after_attempt(5), after=after_log(logger, logging.ERROR))
    def insert_in_battle_pokemon_log(
        self, in_battle_pokemon_log: List[InBattlePokemon]
    ) -> None:
        """Insert in-battle pokemon log records."""
        with get_session() as session:
            for _in_battle_pokemon_log in in_battle_pokemon_log:
                log = InBattlePokemonLog(
                    battle_id=_in_battle_pokemon_log.battle_id,
                    turn=_in_battle_pokemon_log.turn,
                    frame_number=_in_battle_pokemon_log.frame_number,
                    your_pokemon_name=unicodedata.normalize(
                        "NFC", _in_battle_pokemon_log.your_pokemon_name
                    ),
                    opponent_pokemon_name=unicodedata.normalize(
                        "NFC", _in_battle_pokemon_log.opponent_pokemon_name
                    ),
                )
                session.add(log)
            session.commit()

    @retry(stop=stop_after_attempt(5), after=after_log(logger, logging.ERROR))
    def insert_message_log(self, message_log: List[Message]) -> None:
        """Insert message log records."""
        with get_session() as session:
            for _message_log in message_log:
                log = MessageLog(
                    battle_id=_message_log.battle_id,
                    frame_number=_message_log.frame_number,
                    message=_message_log.message,
                )
                session.add(log)
            session.commit()

    @retry(stop=stop_after_attempt(5), after=after_log(logger, logging.ERROR))
    def insert_selected_move_log(self, selected_moves: List[Dict[str, str]]) -> None:
        """Insert selected move log records."""
        try:
            with get_session() as session:
                for _selected_move in selected_moves:
                    move = SelectedMove(
                        battle_id=_selected_move["battle_id"],
                        frame_number=int(_selected_move["frame_number"]),
                        your_pokemon_name=unicodedata.normalize(
                            "NFC", _selected_move["your_pokemon_name"]
                        ),
                        opponent_pokemon_name=unicodedata.normalize(
                            "NFC", _selected_move["opponent_pokemon_name"]
                        ),
                        move=unicodedata.normalize("NFC", _selected_move["move"]),
                    )
                    session.add(move)
                session.commit()
        except Exception as e:
            logger.error(f"Error inserting selected move log: {e}")
            logger.error(
                f"Battle IDs in selected moves: {set(_selected_move['battle_id'] for _selected_move in selected_moves)}"
            )
            raise

    def check_trainer_id_exists(self, trainer_id: str) -> bool:
        """Check if trainer ID exists in database."""
        with get_session() as session:
            statement = select(Trainer).where(Trainer.identity == trainer_id)
            result = session.exec(statement).first()
            return result is not None

    def save_new_trainer(self, trainer_id: str, email: str) -> None:
        """Save new trainer to database."""
        with get_session() as session:
            trainer = Trainer(identity=trainer_id, email=email)
            session.add(trainer)
            session.commit()

    def get_trainer_id_in_DB(self, trainer_id: str) -> int:
        """Get trainer ID from database."""
        with get_session() as session:
            statement = select(Trainer.id).where(Trainer.identity == trainer_id)
            result = session.exec(statement).first()
            if result is None:
                raise ValueError(f"Trainer {trainer_id} not found")
            return result

    def get_user_email(self, trainer_id: str) -> str:
        """Get user email from database."""
        with get_session() as session:
            statement = select(Trainer.email).where(Trainer.identity == trainer_id)
            result = session.exec(statement).first()
            if result is None:
                raise ValueError(f"Trainer {trainer_id} not found")
            return result

    def get_recent_battle_history(
        self, trainer_id: str
    ) -> List[Dict[str, Union[str, int]]]:
        """Get recent battle history."""
        with get_session() as session:
            # Get trainer
            trainer_statement = select(Trainer).where(Trainer.identity == trainer_id)
            trainer = session.exec(trainer_statement).first()
            if trainer is None:
                return []

            # Get battles for this trainer
            battle_statement = select(Battle.battle_id).where(
                Battle.trainer_id == trainer.id
            )
            battle_ids = session.exec(battle_statement).all()

            # Get battle summaries
            statement = (
                select(BattleSummary)
                .where(BattleSummary.battle_id.in_(battle_ids))
                .order_by(BattleSummary.created_at.desc())
                .limit(5)
            )
            results = session.exec(statement).all()

            return [
                {
                    "battle_id": result.battle_id,
                    "created_at": result.created_at,
                    "win_or_lose": result.win_or_lose,
                    "next_rank": result.next_rank,
                    "your_pokemon_1": result.your_pokemon_1,
                    "opponent_pokemon_1": result.opponent_pokemon_1,
                }
                for result in results
            ]

    def update_memo(self, battle_id: str, memo: str) -> None:
        """Update battle memo."""
        with get_session() as session:
            statement = select(BattleSummary).where(
                BattleSummary.battle_id == battle_id
            )
            battle_summary = session.exec(statement).first()
            if battle_summary:
                battle_summary.memo = memo
                session.add(battle_summary)
                session.commit()

    def update_video_process_status(
        self, trainer_id_in_DB: int, video_id: str, status: str
    ) -> None:
        """Update video processing status with upsert."""
        with get_session() as session:
            # Try to find existing record
            statement = select(BattleVideo).where(
                and_(
                    BattleVideo.trainer_id == trainer_id_in_DB,
                    BattleVideo.video_id == video_id,
                )
            )
            existing = session.exec(statement).first()

            if existing:
                existing.process_status = status
                session.add(existing)
            else:
                new_record = BattleVideo(
                    trainer_id=trainer_id_in_DB,
                    video_id=video_id,
                    process_status=status,
                )
                session.add(new_record)

            session.commit()

    def get_latest_season_win_rate(self, trainer_id: str) -> float:
        """Get latest season win rate for trainer."""
        with get_session() as session:
            # Get trainer
            trainer_statement = select(Trainer).where(Trainer.identity == trainer_id)
            trainer = session.exec(trainer_statement).first()
            if trainer is None:
                return 0.0

            # Get latest season
            season_statement = select(Season).order_by(Season.season.desc()).limit(1)
            latest_season = session.exec(season_statement).first()
            if latest_season is None:
                return 0.0

            # Get battles for this trainer
            battle_statement = select(Battle.battle_id).where(
                Battle.trainer_id == trainer.id
            )
            battle_ids = session.exec(battle_statement).all()

            # Get battle summaries for the latest season
            statement = select(BattleSummary.win_or_lose).where(
                and_(
                    BattleSummary.battle_id.in_(battle_ids),
                    BattleSummary.created_at >= latest_season.start_datetime,
                    BattleSummary.created_at <= latest_season.end_datetime,
                )
            )
            results = session.exec(statement).all()

            if not results:
                return 0.0

            wins = sum(1 for result in results if result == "win")
            return wins / len(results)

    def get_latest_season_rank(self, trainer_id: str) -> int:
        """Get latest rank for trainer."""
        with get_session() as session:
            # Get trainer
            trainer_statement = select(Trainer).where(Trainer.identity == trainer_id)
            trainer = session.exec(trainer_statement).first()
            if trainer is None:
                return 0

            # Get latest season
            season_statement = select(Season).order_by(Season.season.desc()).limit(1)
            latest_season = session.exec(season_statement).first()
            if latest_season is None:
                return 0

            # Get battles for this trainer
            battle_statement = select(Battle.battle_id).where(
                Battle.trainer_id == trainer.id
            )
            battle_ids = session.exec(battle_statement).all()

            # Get latest battle summary for the latest season
            statement = (
                select(BattleSummary.next_rank)
                .where(
                    and_(
                        BattleSummary.battle_id.in_(battle_ids),
                        BattleSummary.created_at >= latest_season.start_datetime,
                        BattleSummary.created_at <= latest_season.end_datetime,
                    )
                )
                .order_by(BattleSummary.created_at.desc())
                .limit(1)
            )
            result = session.exec(statement).first()

            return result if result else 0

    def get_latest_win_pokemon(self, trainer_id: str) -> str:
        """Get latest winning Pokemon for trainer."""
        with get_session() as session:
            # Get trainer
            trainer_statement = select(Trainer).where(Trainer.identity == trainer_id)
            trainer = session.exec(trainer_statement).first()
            if trainer is None:
                return ""

            # Get battles for this trainer
            battle_statement = select(Battle.battle_id).where(
                Battle.trainer_id == trainer.id
            )
            battle_ids = session.exec(battle_statement).all()

            # Get latest win battle
            statement = (
                select(
                    BattleSummary.your_pokemon_1,
                    BattleSummary.your_pokemon_2,
                    BattleSummary.your_pokemon_3,
                )
                .where(
                    and_(
                        BattleSummary.battle_id.in_(battle_ids),
                        BattleSummary.win_or_lose == "win",
                    )
                )
                .order_by(BattleSummary.created_at.desc())
                .limit(1)
            )
            result = session.exec(statement).first()

            if result:
                return f"{result[0]}, {result[1]}, {result[2]}"
            return ""

    def get_latest_lose_pokemon(self, trainer_id: str) -> str:
        """Get latest losing Pokemon for trainer."""
        with get_session() as session:
            # Get trainer
            trainer_statement = select(Trainer).where(Trainer.identity == trainer_id)
            trainer = session.exec(trainer_statement).first()
            if trainer is None:
                return ""

            # Get battles for this trainer
            battle_statement = select(Battle.battle_id).where(
                Battle.trainer_id == trainer.id
            )
            battle_ids = session.exec(battle_statement).all()

            # Get latest lose battle
            statement = (
                select(
                    BattleSummary.your_pokemon_1,
                    BattleSummary.your_pokemon_2,
                    BattleSummary.your_pokemon_3,
                )
                .where(
                    and_(
                        BattleSummary.battle_id.in_(battle_ids),
                        BattleSummary.win_or_lose == "lose",
                    )
                )
                .order_by(BattleSummary.created_at.desc())
                .limit(1)
            )
            result = session.exec(statement).first()

            if result:
                return f"{result[0]}, {result[1]}, {result[2]}"
            return ""

    def get_battle_counts(self, trainer_id: str) -> List[Dict[str, Union[str, int]]]:
        """Get battle counts for trainer."""
        with get_session() as session:
            # Get trainer
            trainer_statement = select(Trainer).where(Trainer.identity == trainer_id)
            trainer = session.exec(trainer_statement).first()
            if trainer is None:
                return []

            # Get battles count
            battle_statement = select(Battle).where(Battle.trainer_id == trainer.id)
            battles = session.exec(battle_statement).all()

            return [{"battle_count": len(battles)}]

    def get_win_rate_transitions_all(self, trainer_id: str) -> List[float]:
        """Get win rate transitions for all seasons."""
        with get_session() as session:
            # Get trainer
            trainer_statement = select(Trainer).where(Trainer.identity == trainer_id)
            trainer = session.exec(trainer_statement).first()
            if trainer is None:
                return []

            # Get battles for this trainer
            battle_statement = select(Battle.battle_id).where(
                Battle.trainer_id == trainer.id
            )
            battle_ids = session.exec(battle_statement).all()

            # Get all battle summaries
            statement = (
                select(BattleSummary.win_or_lose)
                .where(BattleSummary.battle_id.in_(battle_ids))
                .order_by(BattleSummary.created_at)
            )
            results = session.exec(statement).all()

            if not results:
                return []

            win_rates = []
            wins = 0
            for i, result in enumerate(results, 1):
                if result == "win":
                    wins += 1
                win_rates.append(wins / i)

            return win_rates

    def get_win_rate_transitions_season(
        self, season: int, trainer_id: str
    ) -> List[float]:
        """Get win rate transitions for a specific season."""
        with get_session() as session:
            # Get trainer
            trainer_statement = select(Trainer).where(Trainer.identity == trainer_id)
            trainer = session.exec(trainer_statement).first()
            if trainer is None:
                return []

            # Get season
            season_statement = select(Season).where(Season.season == season)
            target_season = session.exec(season_statement).first()
            if target_season is None:
                return []

            # Get battles for this trainer
            battle_statement = select(Battle.battle_id).where(
                Battle.trainer_id == trainer.id
            )
            battle_ids = session.exec(battle_statement).all()

            # Get battle summaries for the season
            statement = (
                select(BattleSummary.win_or_lose)
                .where(
                    and_(
                        BattleSummary.battle_id.in_(battle_ids),
                        BattleSummary.created_at >= target_season.start_datetime,
                        BattleSummary.created_at <= target_season.end_datetime,
                    )
                )
                .order_by(BattleSummary.created_at)
            )
            results = session.exec(statement).all()

            if not results:
                return []

            win_rates = []
            wins = 0
            for i, result in enumerate(results, 1):
                if result == "win":
                    wins += 1
                win_rates.append(wins / i)

            return win_rates

    def get_next_rank_transitions_all(self, trainer_id: str) -> List[int]:
        """Get rank transitions for all seasons."""
        with get_session() as session:
            # Get trainer
            trainer_statement = select(Trainer).where(Trainer.identity == trainer_id)
            trainer = session.exec(trainer_statement).first()
            if trainer is None:
                return []

            # Get battles for this trainer
            battle_statement = select(Battle.battle_id).where(
                Battle.trainer_id == trainer.id
            )
            battle_ids = session.exec(battle_statement).all()

            # Get all battle summaries
            statement = (
                select(BattleSummary.next_rank)
                .where(BattleSummary.battle_id.in_(battle_ids))
                .order_by(BattleSummary.created_at)
            )
            results = session.exec(statement).all()

            return list(results)

    def get_next_rank_transitions_season(
        self, season: int, trainer_id: str
    ) -> List[int]:
        """Get rank transitions for a specific season."""
        with get_session() as session:
            # Get trainer
            trainer_statement = select(Trainer).where(Trainer.identity == trainer_id)
            trainer = session.exec(trainer_statement).first()
            if trainer is None:
                return []

            # Get season
            season_statement = select(Season).where(Season.season == season)
            target_season = session.exec(season_statement).first()
            if target_season is None:
                return []

            # Get battles for this trainer
            battle_statement = select(Battle.battle_id).where(
                Battle.trainer_id == trainer.id
            )
            battle_ids = session.exec(battle_statement).all()

            # Get battle summaries for the season
            statement = (
                select(BattleSummary.next_rank)
                .where(
                    and_(
                        BattleSummary.battle_id.in_(battle_ids),
                        BattleSummary.created_at >= target_season.start_datetime,
                        BattleSummary.created_at <= target_season.end_datetime,
                    )
                )
                .order_by(BattleSummary.created_at)
            )
            results = session.exec(statement).all()

            return list(results)

    def get_your_pokemon_stats_summary_all(
        self, trainer_id: str
    ) -> List[Dict[str, Union[str, int, float]]]:
        """Get your pokemon stats summary for all seasons."""
        with get_session() as session:
            # Get trainer
            trainer_statement = select(Trainer).where(Trainer.identity == trainer_id)
            trainer = session.exec(trainer_statement).first()
            if trainer is None:
                return []

            # Get battles for this trainer
            battle_statement = select(Battle.battle_id).where(
                Battle.trainer_id == trainer.id
            )
            battle_ids = session.exec(battle_statement).all()

            # Get all battle summaries
            statement = select(BattleSummary).where(
                BattleSummary.battle_id.in_(battle_ids)
            )
            results = session.exec(statement).all()

            # Aggregate pokemon stats
            pokemon_stats = {}
            for result in results:
                for pokemon in [
                    result.your_pokemon_1,
                    result.your_pokemon_2,
                    result.your_pokemon_3,
                ]:
                    if pokemon not in pokemon_stats:
                        pokemon_stats[pokemon] = {"battles": 0, "wins": 0}
                    pokemon_stats[pokemon]["battles"] += 1
                    if result.win_or_lose == "win":
                        pokemon_stats[pokemon]["wins"] += 1

            return [
                {
                    "pokemon": pokemon,
                    "battles": stats["battles"],
                    "wins": stats["wins"],
                    "win_rate": (
                        stats["wins"] / stats["battles"] if stats["battles"] > 0 else 0
                    ),
                }
                for pokemon, stats in pokemon_stats.items()
            ]

    def get_your_pokemon_stats_summary_season(
        self, season: int, trainer_id: str
    ) -> List[Dict[str, Union[str, int, float]]]:
        """Get your pokemon stats summary for a specific season."""
        with get_session() as session:
            # Get trainer
            trainer_statement = select(Trainer).where(Trainer.identity == trainer_id)
            trainer = session.exec(trainer_statement).first()
            if trainer is None:
                return []

            # Get season
            season_statement = select(Season).where(Season.season == season)
            target_season = session.exec(season_statement).first()
            if target_season is None:
                return []

            # Get battles for this trainer
            battle_statement = select(Battle.battle_id).where(
                Battle.trainer_id == trainer.id
            )
            battle_ids = session.exec(battle_statement).all()

            # Get battle summaries for the season
            statement = select(BattleSummary).where(
                and_(
                    BattleSummary.battle_id.in_(battle_ids),
                    BattleSummary.created_at >= target_season.start_datetime,
                    BattleSummary.created_at <= target_season.end_datetime,
                )
            )
            results = session.exec(statement).all()

            # Aggregate pokemon stats
            pokemon_stats = {}
            for result in results:
                for pokemon in [
                    result.your_pokemon_1,
                    result.your_pokemon_2,
                    result.your_pokemon_3,
                ]:
                    if pokemon not in pokemon_stats:
                        pokemon_stats[pokemon] = {"battles": 0, "wins": 0}
                    pokemon_stats[pokemon]["battles"] += 1
                    if result.win_or_lose == "win":
                        pokemon_stats[pokemon]["wins"] += 1

            return [
                {
                    "pokemon": pokemon,
                    "battles": stats["battles"],
                    "wins": stats["wins"],
                    "win_rate": (
                        stats["wins"] / stats["battles"] if stats["battles"] > 0 else 0
                    ),
                }
                for pokemon, stats in pokemon_stats.items()
            ]

    def get_opponent_pokemon_stats_summary_all(
        self, trainer_id: str
    ) -> List[Dict[str, Union[str, int, float]]]:
        """Get opponent pokemon stats summary for all seasons."""
        with get_session() as session:
            # Get trainer
            trainer_statement = select(Trainer).where(Trainer.identity == trainer_id)
            trainer = session.exec(trainer_statement).first()
            if trainer is None:
                return []

            # Get battles for this trainer
            battle_statement = select(Battle.battle_id).where(
                Battle.trainer_id == trainer.id
            )
            battle_ids = session.exec(battle_statement).all()

            # Get all battle summaries
            statement = select(BattleSummary).where(
                BattleSummary.battle_id.in_(battle_ids)
            )
            results = session.exec(statement).all()

            # Aggregate pokemon stats
            pokemon_stats = {}
            for result in results:
                for pokemon in [
                    result.opponent_pokemon_1,
                    result.opponent_pokemon_2,
                    result.opponent_pokemon_3,
                ]:
                    if pokemon not in pokemon_stats:
                        pokemon_stats[pokemon] = {"battles": 0, "losses": 0}
                    pokemon_stats[pokemon]["battles"] += 1
                    if result.win_or_lose == "win":
                        pokemon_stats[pokemon]["losses"] += 1

            return [
                {
                    "pokemon": pokemon,
                    "battles": stats["battles"],
                    "losses": stats["losses"],
                    "loss_rate": (
                        stats["losses"] / stats["battles"]
                        if stats["battles"] > 0
                        else 0
                    ),
                }
                for pokemon, stats in pokemon_stats.items()
            ]

    def get_opponent_pokemon_stats_summary_season(
        self, season: int, trainer_id: str
    ) -> List[Dict[str, Union[str, int, float]]]:
        """Get opponent pokemon stats summary for a specific season."""
        with get_session() as session:
            # Get trainer
            trainer_statement = select(Trainer).where(Trainer.identity == trainer_id)
            trainer = session.exec(trainer_statement).first()
            if trainer is None:
                return []

            # Get season
            season_statement = select(Season).where(Season.season == season)
            target_season = session.exec(season_statement).first()
            if target_season is None:
                return []

            # Get battles for this trainer
            battle_statement = select(Battle.battle_id).where(
                Battle.trainer_id == trainer.id
            )
            battle_ids = session.exec(battle_statement).all()

            # Get battle summaries for the season
            statement = select(BattleSummary).where(
                and_(
                    BattleSummary.battle_id.in_(battle_ids),
                    BattleSummary.created_at >= target_season.start_datetime,
                    BattleSummary.created_at <= target_season.end_datetime,
                )
            )
            results = session.exec(statement).all()

            # Aggregate pokemon stats
            pokemon_stats = {}
            for result in results:
                for pokemon in [
                    result.opponent_pokemon_1,
                    result.opponent_pokemon_2,
                    result.opponent_pokemon_3,
                ]:
                    if pokemon not in pokemon_stats:
                        pokemon_stats[pokemon] = {"battles": 0, "losses": 0}
                    pokemon_stats[pokemon]["battles"] += 1
                    if result.win_or_lose == "win":
                        pokemon_stats[pokemon]["losses"] += 1

            return [
                {
                    "pokemon": pokemon,
                    "battles": stats["battles"],
                    "losses": stats["losses"],
                    "loss_rate": (
                        stats["losses"] / stats["battles"]
                        if stats["battles"] > 0
                        else 0
                    ),
                }
                for pokemon, stats in pokemon_stats.items()
            ]

    def get_battle_log_all(
        self, trainer_id: str, offset: int = 0, limit: int = 20
    ) -> List[Dict[str, Union[str, int]]]:
        """Get all battle logs."""
        with get_session() as session:
            # Get trainer
            trainer_statement = select(Trainer).where(Trainer.identity == trainer_id)
            trainer = session.exec(trainer_statement).first()
            if trainer is None:
                return []

            # Get battles for this trainer
            battle_statement = select(Battle.battle_id).where(
                Battle.trainer_id == trainer.id
            )
            battle_ids = session.exec(battle_statement).all()

            # Get battle summaries
            statement = (
                select(BattleSummary)
                .where(BattleSummary.battle_id.in_(battle_ids))
                .order_by(BattleSummary.created_at.desc())
                .offset(offset)
                .limit(limit)
            )
            results = session.exec(statement).all()

            return [
                {
                    "battle_id": result.battle_id,
                    "created_at": result.created_at,
                    "win_or_lose": result.win_or_lose,
                    "next_rank": result.next_rank,
                    "your_team": result.your_team,
                    "opponent_team": result.opponent_team,
                    "memo": result.memo,
                }
                for result in results
            ]

    def get_battle_log_season(
        self, trainer_id: str, season: int, offset: int = 0, limit: int = 20
    ) -> List[Dict[str, Union[str, int]]]:
        """Get battle logs for a specific season."""
        with get_session() as session:
            # Get trainer
            trainer_statement = select(Trainer).where(Trainer.identity == trainer_id)
            trainer = session.exec(trainer_statement).first()
            if trainer is None:
                return []

            # Get season
            season_statement = select(Season).where(Season.season == season)
            target_season = session.exec(season_statement).first()
            if target_season is None:
                return []

            # Get battles for this trainer
            battle_statement = select(Battle.battle_id).where(
                Battle.trainer_id == trainer.id
            )
            battle_ids = session.exec(battle_statement).all()

            # Get battle summaries for the season
            statement = (
                select(BattleSummary)
                .where(
                    and_(
                        BattleSummary.battle_id.in_(battle_ids),
                        BattleSummary.created_at >= target_season.start_datetime,
                        BattleSummary.created_at <= target_season.end_datetime,
                    )
                )
                .order_by(BattleSummary.created_at.desc())
                .offset(offset)
                .limit(limit)
            )
            results = session.exec(statement).all()

            return [
                {
                    "battle_id": result.battle_id,
                    "created_at": result.created_at,
                    "win_or_lose": result.win_or_lose,
                    "next_rank": result.next_rank,
                    "your_team": result.your_team,
                    "opponent_team": result.opponent_team,
                    "memo": result.memo,
                }
                for result in results
            ]

    def get_battle_log_all_count(self, trainer_id: str) -> int:
        """Get total count of battle logs."""
        with get_session() as session:
            # Get trainer
            trainer_statement = select(Trainer).where(Trainer.identity == trainer_id)
            trainer = session.exec(trainer_statement).first()
            if trainer is None:
                return 0

            # Get battles for this trainer
            battle_statement = select(Battle.battle_id).where(
                Battle.trainer_id == trainer.id
            )
            battle_ids = session.exec(battle_statement).all()

            # Count battle summaries
            from sqlmodel import func

            statement = (
                select(func.count())
                .select_from(BattleSummary)
                .where(BattleSummary.battle_id.in_(battle_ids))
            )
            result = session.exec(statement).first()

            return result if result else 0

    def get_battle_log_season_count(self, season: int, trainer_id: str) -> int:
        """Get count of battle logs for a specific season."""
        with get_session() as session:
            # Get trainer
            trainer_statement = select(Trainer).where(Trainer.identity == trainer_id)
            trainer = session.exec(trainer_statement).first()
            if trainer is None:
                return 0

            # Get season
            season_statement = select(Season).where(Season.season == season)
            target_season = session.exec(season_statement).first()
            if target_season is None:
                return 0

            # Get battles for this trainer
            battle_statement = select(Battle.battle_id).where(
                Battle.trainer_id == trainer.id
            )
            battle_ids = session.exec(battle_statement).all()

            # Count battle summaries for the season
            from sqlmodel import func

            statement = (
                select(func.count())
                .select_from(BattleSummary)
                .where(
                    and_(
                        BattleSummary.battle_id.in_(battle_ids),
                        BattleSummary.created_at >= target_season.start_datetime,
                        BattleSummary.created_at <= target_season.end_datetime,
                    )
                )
            )
            result = session.exec(statement).first()

            return result if result else 0

    def get_in_battle_log(self, battle_id: str) -> List[Dict[str, Union[str, int]]]:
        """Get in-battle log."""
        with get_session() as session:
            statement = (
                select(InBattlePokemonLog)
                .where(InBattlePokemonLog.battle_id == battle_id)
                .order_by(InBattlePokemonLog.turn, InBattlePokemonLog.frame_number)
            )
            results = session.exec(statement).all()

            return [
                {
                    "turn": result.turn,
                    "frame_number": result.frame_number,
                    "your_pokemon_name": result.your_pokemon_name,
                    "opponent_pokemon_name": result.opponent_pokemon_name,
                }
                for result in results
            ]

    def get_battle_summary(self, battle_id: str) -> Dict[str, Union[str, int]]:
        """Get battle summary."""
        with get_session() as session:
            statement = select(BattleSummary).where(
                BattleSummary.battle_id == battle_id
            )
            result = session.exec(statement).first()

            if result is None:
                return {}

            return {
                "battle_id": result.battle_id,
                "created_at": result.created_at,
                "win_or_lose": result.win_or_lose,
                "next_rank": result.next_rank,
                "your_team": result.your_team,
                "opponent_team": result.opponent_team,
                "your_pokemon_1": result.your_pokemon_1,
                "your_pokemon_2": result.your_pokemon_2,
                "your_pokemon_3": result.your_pokemon_3,
                "opponent_pokemon_1": result.opponent_pokemon_1,
                "opponent_pokemon_2": result.opponent_pokemon_2,
                "opponent_pokemon_3": result.opponent_pokemon_3,
                "video": result.video,
                "memo": result.memo,
            }

    def get_in_battle_message_log(
        self, battle_id: str
    ) -> List[Dict[str, Union[str, int]]]:
        """Get in-battle message log."""
        with get_session() as session:
            statement = (
                select(MessageLog)
                .where(MessageLog.battle_id == battle_id)
                .order_by(MessageLog.frame_number)
            )
            results = session.exec(statement).all()

            return [
                {"frame_number": result.frame_number, "message": result.message}
                for result in results
            ]

    def get_in_battle_message_full_log(self, battle_id: str) -> Tuple[
        List[Dict[str, Union[str, int]]],
        List[Dict[str, Union[str, int]]],
    ]:
        """Get full in-battle message log."""
        in_battle_log = self.get_in_battle_log(battle_id)
        message_log = self.get_in_battle_message_log(battle_id)
        return in_battle_log, message_log

    def get_fainted_pokemon_log(
        self, battle_id: str
    ) -> List[Dict[str, Union[str, int]]]:
        """Get fainted pokemon log."""
        with get_session() as session:
            statement = (
                select(FaintedLog)
                .where(FaintedLog.battle_id == battle_id)
                .order_by(FaintedLog.turn)
            )
            results = session.exec(statement).all()

            return [
                {
                    "turn": result.turn,
                    "your_pokemon_name": result.your_pokemon_name,
                    "opponent_pokemon_name": result.opponent_pokemon_name,
                    "fainted_pokemon_side": result.fainted_pokemon_side,
                }
                for result in results
            ]

    def get_your_pokemon_defeat_summary(
        self, trainer_id: str
    ) -> List[Dict[str, Union[str, int]]]:
        """Get your pokemon defeat summary."""
        # Simplified implementation
        return []

    def get_your_pokemon_defeat_summary_in_season(
        self, season: int, trainer_id: str
    ) -> List[Dict[str, Union[str, int]]]:
        """Get your pokemon defeat summary in season."""
        # Simplified implementation
        return []

    def get_opponent_pokemon_defeat_summary(
        self, trainer_id: str
    ) -> List[Dict[str, Union[str, int]]]:
        """Get opponent pokemon defeat summary."""
        # Simplified implementation
        return []

    def get_opponent_pokemon_defeat_summary_in_season(
        self, season: int, trainer_id: str
    ) -> List[Dict[str, Union[str, int]]]:
        """Get opponent pokemon defeat summary in season."""
        # Simplified implementation
        return []

    def get_battle_video_status_list(self, trainer_id: str) -> List[Dict[str, str]]:
        """Get battle video status list."""
        with get_session() as session:
            # Get trainer
            trainer_statement = select(Trainer).where(Trainer.identity == trainer_id)
            trainer = session.exec(trainer_statement).first()
            if trainer is None:
                return []

            statement = select(BattleVideo).where(BattleVideo.trainer_id == trainer.id)
            results = session.exec(statement).all()

            return [
                {"video_id": result.video_id, "process_status": result.process_status}
                for result in results
            ]

    def get_seasons(self) -> List[Dict[str, Union[int, str]]]:
        """Get all seasons."""
        with get_session() as session:
            statement = select(Season).order_by(Season.season)
            results = session.exec(statement).all()

            return [
                {
                    "id": result.id,
                    "season": result.season,
                    "start_datetime": result.start_datetime,
                    "end_datetime": result.end_datetime,
                }
                for result in results
            ]

    def search_battles(
        self, trainer_id: str, search_text: str = "", season: int = 0
    ) -> List[Dict[str, Union[str, int]]]:
        """Search battles with filters."""
        with get_session() as session:
            # Get trainer
            trainer_statement = select(Trainer).where(Trainer.identity == trainer_id)
            trainer = session.exec(trainer_statement).first()
            if trainer is None:
                return []

            # Get battles for this trainer
            battle_statement = select(Battle.battle_id).where(
                Battle.trainer_id == trainer.id
            )
            battle_ids = session.exec(battle_statement).all()

            # Build query
            statement = select(BattleSummary).where(
                BattleSummary.battle_id.in_(battle_ids)
            )

            # Apply season filter if specified
            if season > 0:
                season_statement = select(Season).where(Season.season == season)
                target_season = session.exec(season_statement).first()
                if target_season:
                    statement = statement.where(
                        and_(
                            BattleSummary.created_at >= target_season.start_datetime,
                            BattleSummary.created_at <= target_season.end_datetime,
                        )
                    )

            # Apply text search if specified
            if search_text:
                from sqlmodel import or_

                statement = statement.where(
                    or_(
                        BattleSummary.your_team.contains(search_text),
                        BattleSummary.opponent_team.contains(search_text),
                        BattleSummary.memo.contains(search_text),
                    )
                )

            statement = statement.order_by(BattleSummary.created_at.desc())
            results = session.exec(statement).all()

            return [
                {
                    "battle_id": result.battle_id,
                    "created_at": result.created_at,
                    "win_or_lose": result.win_or_lose,
                    "next_rank": result.next_rank,
                    "your_team": result.your_team,
                    "opponent_team": result.opponent_team,
                    "memo": result.memo,
                }
                for result in results
            ]

    def build_and_insert_fainted_log(
        self,
        modified_in_battle_pokemons: List[InBattlePokemon],
        modified_messages: List[Message],
    ) -> None:
        """Build and insert fainted pokemon log from battle data."""
        df_in_battle_pokemon = pd.DataFrame(
            [obj.__dict__ for obj in modified_in_battle_pokemons]
        )
        df_messages = pd.DataFrame([obj.__dict__ for obj in modified_messages])
        df_in_battle_pokemon = df_in_battle_pokemon.sort_values(
            by=["battle_id", "turn"]
        )
        df_in_battle_pokemon["next_frame_number"] = df_in_battle_pokemon.groupby(
            "battle_id"
        )["frame_number"].shift(-1)

        # Join the message log to the battle log
        df_messages2 = pd.merge_asof(
            df_messages.sort_values("frame_number"),
            df_in_battle_pokemon.sort_values("frame_number"),
            left_on="frame_number",
            right_on="frame_number",
            by="battle_id",
            direction="backward",
        )
        df_messages2["fainted_pokemon_type"] = None
        df_messages2.loc[
            df_messages2.message.str.contains(".* fainted!"), "fainted_pokemon_type"
        ] = "Your Pokemon Fainted"
        df_messages2.loc[
            df_messages2.message.str.contains("The opposing .* fainted!"),
            "fainted_pokemon_type",
        ] = "Opponent Pokemon Fainted"
        # Keep only rows with fainted pokemon
        df_messages2 = df_messages2.dropna(subset=["fainted_pokemon_type"])

        # Join fainted pokemon messages to the battle log
        df_in_battle_pokemon = df_in_battle_pokemon.merge(
            df_messages2[["battle_id", "turn", "fainted_pokemon_type"]],
            on=["battle_id", "turn"],
            how="left",
        )
        # Add a 'fainted_pokemon_side' column
        df_in_battle_pokemon["fainted_pokemon_side"] = "Unknown"
        df_in_battle_pokemon.loc[
            df_in_battle_pokemon.fainted_pokemon_type == "Your Pokemon Fainted",
            "fainted_pokemon_side",
        ] = "Opponent Pokemon Win"
        df_in_battle_pokemon.loc[
            df_in_battle_pokemon.fainted_pokemon_type == "Opponent Pokemon Fainted",
            "fainted_pokemon_side",
        ] = "Your Pokemon Win"
        stats = df_in_battle_pokemon.query("fainted_pokemon_side != 'Unknown'")
        stats = stats.drop_duplicates()

        fainted_log: List[Dict[str, Union[str, int]]] = stats.to_dict(orient="records")

        with get_session() as session:
            for _fainted_log in fainted_log:
                fainted = FaintedLog(
                    battle_id=str(_fainted_log["battle_id"]),
                    turn=int(_fainted_log["turn"]),
                    your_pokemon_name=unicodedata.normalize(
                        "NFC", str(_fainted_log["your_pokemon_name"])
                    ),
                    opponent_pokemon_name=unicodedata.normalize(
                        "NFC", str(_fainted_log["opponent_pokemon_name"])
                    ),
                    fainted_pokemon_side=str(_fainted_log["fainted_pokemon_side"]),
                )
                session.add(fainted)
            session.commit()
