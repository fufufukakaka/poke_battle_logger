import os
import random
import unicodedata
from typing import Dict, List, Tuple, Union, cast

import pandas as pd
from peewee import (
    ForeignKeyField,
    IntegerField,
    Model,
    PostgresqlDatabase,
    SqliteDatabase,
    TextField,
)
from tenacity import retry, stop_after_attempt

from poke_battle_logger.types import Battle as BattleType
from poke_battle_logger.types import (
    BattleLog,
    InBattlePokemon,
    Message,
    PreBattlePokemon,
)


def build_db_connection() -> Union[SqliteDatabase, PostgresqlDatabase]:
    env = os.environ.get("ENV", "local")
    if env == "local":
        db = SqliteDatabase("poke_battle_logger.db")
    elif env == "production":
        db = PostgresqlDatabase(
            os.environ.get("POSTGRES_DB", "postgres"),
            user=os.environ.get("POSTGRES_USER", "postgres"),
            password=os.environ.get("POSTGRES_PASSWORD", "postgres"),
            host=os.environ.get("POSTGRES_HOST", "localhost"),
            port=os.environ.get("POSTGRES_PORT", 5432),
        )
    else:
        raise ValueError("ENV must be local or production")
    return db


pokemon_name_df = pd.read_csv("data/pokemon_names.csv")
pokemon_japanese_to_no_dict = dict(
    zip(pokemon_name_df["Japanese"], pokemon_name_df["No."])
)


class BaseModel(Model):  # type: ignore
    class Meta:
        database = build_db_connection()


class Battle(BaseModel):  # type: ignore
    battle_id = TextField(unique=True)
    trainer_id = IntegerField()


class BattleSummary(BaseModel):  # type: ignore
    battle_id = ForeignKeyField(Battle, backref="battleSummarys")
    created_at = TextField()
    win_or_lose = TextField()
    next_rank = IntegerField()
    your_team = TextField()
    opponent_team = TextField()
    your_pokemon_1 = TextField()
    your_pokemon_2 = TextField()
    your_pokemon_3 = TextField()
    opponent_pokemon_1 = TextField()
    opponent_pokemon_2 = TextField()
    opponent_pokemon_3 = TextField()
    video = TextField()
    memo = TextField()


class InBattlePokemonLog(BaseModel):  # type: ignore
    battle_id = ForeignKeyField(Battle, backref="battlePokemonTeams")
    turn = IntegerField()
    frame_number = IntegerField()
    your_pokemon_name = TextField()
    opponent_pokemon_name = TextField()


class MessageLog(BaseModel):  # type: ignore
    battle_id = ForeignKeyField(Battle, backref="battleMessages")
    frame_number = IntegerField()
    message = TextField()


class BattlePokemonTeam(BaseModel):  # type: ignore
    battle_id = ForeignKeyField(Battle, backref="inBattlePokemonLogs")
    team = TextField()
    pokemon_name = TextField()


class Season(BaseModel):  # type: ignore
    season = IntegerField()
    start_datetime = TextField()
    end_datetime = TextField()


class Trainer(BaseModel):  # type: ignore
    identity = TextField()
    email = TextField()


class FaintedLog(BaseModel):  # type: ignore
    battle_id = TextField()
    turn = IntegerField()
    your_pokemon_name = TextField()
    opponent_pokemon_name = TextField()
    fainted_pokemon_side = TextField()


class BattleVideo(BaseModel):  # type: ignore
    trainer_id = IntegerField()
    video_id = TextField()
    process_status = TextField()


class DatabaseHandler:
    def __init__(self) -> None:
        self.db = build_db_connection()

    def create_tables(self) -> None:
        with self.db:
            if not Battle.table_exists():
                self.db.create_tables([Battle])
            if not BattleSummary.table_exists():
                self.db.create_tables([BattleSummary])
            if not BattlePokemonTeam.table_exists():
                self.db.create_tables([BattlePokemonTeam])
            if not InBattlePokemonLog.table_exists():
                self.db.create_tables([InBattlePokemonLog])
            if not MessageLog.table_exists():
                self.db.create_tables([MessageLog])
            if not Season.table_exists():
                self.db.create_tables([Season])
                with self.db:
                    Season.create(
                        id=1,
                        season=3,
                        start_datetime="2023-02-01 09:00:00",
                        end_datetime="2023-03-01 09:00:00",
                    )
                    Season.create(
                        id=2,
                        season=4,
                        start_datetime="2023-03-01 09:00:00",
                        end_datetime="2023-04-01 09:00:00",
                    )

    @retry(stop=stop_after_attempt(5))
    def insert_battle_id(self, battles: List[BattleType]) -> None:
        self.db.connect()
        for _battle in battles:
            _battle_id = _battle.battle_id
            _trainer_id = _battle.trainer_id
            Battle.create(battle_id=_battle_id, trainer_id=_trainer_id)
        self.db.close()

    @retry(stop=stop_after_attempt(5))
    def insert_battle_summary(self, battle_summary: List[BattleLog]) -> None:
        self.db.connect()
        for _battle_summary in battle_summary:
            BattleSummary.create(
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
        self.db.close()

    @retry(stop=stop_after_attempt(5))
    def insert_battle_pokemon_team(
        self, battle_pokemon_team: List[PreBattlePokemon]
    ) -> None:
        self.db.connect()
        for _battle_pokemon_team in battle_pokemon_team:
            BattlePokemonTeam.create(
                battle_id=_battle_pokemon_team.battle_id,
                team=_battle_pokemon_team.team,
                pokemon_name=unicodedata.normalize(
                    "NFC", _battle_pokemon_team.pokemon_name
                ),
            )
        self.db.close()

    @retry(stop=stop_after_attempt(5))
    def insert_in_battle_pokemon_log(
        self, in_battle_pokemon_log: List[InBattlePokemon]
    ) -> None:
        self.db.connect()
        for _in_battle_pokemon_log in in_battle_pokemon_log:
            InBattlePokemonLog.create(
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
        self.db.close()

    @retry(stop=stop_after_attempt(5))
    def insert_message_log(self, message_log: List[Message]) -> None:
        self.db.connect()
        for _message_log in message_log:
            MessageLog.create(
                battle_id=_message_log.battle_id,
                frame_number=_message_log.frame_number,
                message=_message_log.message,
            )
        self.db.close()

    def get_latest_season_win_rate(self, trainer_id: str) -> float:
        sql = f"""
        with target_trainer as (
            select
                id
            from
                trainer
            where
                identity = '{trainer_id}'
        ),
        target_trainer_battles as (
            select
                battle_id
            from
                battle
            where
                trainer_id in (select id from target_trainer)
        ),
        latest_season_start_end as (
            select
                start_datetime,
                end_datetime
            from
                season
            order by
                season desc
            limit 1
        ),
        target_battle_summary as (
            select * from battlesummary
            where
                created_at between(
                    select
                        start_datetime from latest_season_start_end)
                and(
                    select
                        end_datetime from latest_season_start_end)
                and battle_id in(
                    select
                        battle_id from target_trainer_battles)
            order by
                created_at
        )
        select
            CAST(sum(
                    case when win_or_lose = 'win' then
                        1
                    else
                        0
                    end) as float) / count(1) as win_rate
        from
            target_battle_summary
        """
        self.db.connect()
        win_rate = cast(float, self.db.execute_sql(sql).fetchone()[0])
        self.db.close()
        return win_rate

    def get_latest_season_rank(self, trainer_id: str) -> int:
        sql = f"""
        with target_trainer as (
            select
                id
            from
                trainer
            where
                identity = '{trainer_id}'
        ),
        target_trainer_battles as (
            select
                battle_id
            from
                battle
            where
                trainer_id in (select id from target_trainer)
        ),
        latest_season_start_end as (
            select
                start_datetime,
                end_datetime
            from
                season
            order by season desc
            limit 1
        )
        select
            next_rank
        from
            battlesummary
        where
            created_at between(
                select
                    start_datetime from latest_season_start_end)
            and(
                select
                    end_datetime from latest_season_start_end)
            and battle_id in(
                select
                    battle_id from target_trainer_battles)
        order by
            created_at desc
        limit 1
        """
        self.db.connect()
        latest_season_rank = cast(int, self.db.execute_sql(sql).fetchone()[0])
        self.db.close()
        return latest_season_rank

    def get_latest_win_pokemon(self, trainer_id: str) -> str:
        sql = f"""
        with target_trainer as (
            select
                id
            from
                trainer
            where
                identity = '{trainer_id}'
        ),
        target_trainer_battles as (
            select
                battle_id
            from
                battle
            where
                trainer_id in (select id from target_trainer)
        )
        select
            opponent_pokemon_1, opponent_pokemon_2, opponent_pokemon_3
        from
            battlesummary
        where
            win_or_lose = 'win'
            and battle_id in (
                select
                    battle_id from target_trainer_battles)
        order by
            created_at desc
        limit 1
        """
        self.db.connect()
        latest_win_pokemons = self.db.execute_sql(sql).fetchone()
        self.db.close()
        # ランダムに1匹選ぶ
        latest_win_pokemon = cast(str, random.choice(latest_win_pokemons))
        return latest_win_pokemon

    def get_latest_lose_pokemon(self, trainer_id: str) -> str:
        sql = f"""
        with target_trainer as (
            select
                id
            from
                trainer
            where
                identity = '{trainer_id}'
        ),
        target_trainer_battles as (
            select
                battle_id
            from
                battle
            where
                trainer_id in (select id from target_trainer)
        )
        select
            opponent_pokemon_1, opponent_pokemon_2, opponent_pokemon_3
        from
            battlesummary
        where
            win_or_lose = 'lose'
            and battle_id in (
                select
                    battle_id from target_trainer_battles)
        order by
            created_at desc
        limit 1
        """
        self.db.connect()
        latest_lose_pokemons = self.db.execute_sql(sql).fetchone()
        self.db.close()
        # Unseen を除いてランダムに1匹選ぶ
        latest_lose_pokemon = cast(
            str,
            random.choice(
                [pokemon for pokemon in latest_lose_pokemons if pokemon != "Unseen"]
            ),
        )
        return latest_lose_pokemon

    def get_win_rate_transitions_season(
        self, season: int, trainer_id: str
    ) -> List[float]:
        sql = f"""
        with season_start_end as (
            select
                start_datetime,
                end_datetime
            from
                season
            where
                season = {season}
        ),
        target_trainer as (
            select
                id
            from
                trainer
            where
                identity = '{trainer_id}'
        ),
        target_trainer_battles as (
            select
                battle_id
            from
                battle
            where
                trainer_id in (select id from target_trainer)
        )
        select
            (
                select
                    SUM(
                        case when win_or_lose = 'win' then
                            1.0
                        else
                            0.0
                        end)
                from
                    battlesummary as t2
                where
                    t2.created_at <= t1.created_at and created_at between(
                    select
                        start_datetime from season_start_end)
                and(
                    select
                        end_datetime from season_start_end)) / (
                    select
                        COUNT(*)
                    from
                        battlesummary as t3
                    where
                        t3.created_at <= t1.created_at and created_at between(
                    select
                        start_datetime from season_start_end)
                and(
                    select
                        end_datetime from season_start_end)) as win_rate
                from
                    battlesummary as t1
                where created_at between(
                    select
                        start_datetime from season_start_end)
                and(
                    select
                        end_datetime from season_start_end)
                and battle_id in (
                    select
                        battle_id from target_trainer_battles)
                order by
                    created_at asc
        """
        self.db.connect()
        _win_rate_transitions = cast(
            List[Tuple[float]], self.db.execute_sql(sql).fetchall()
        )
        self.db.close()
        win_rate_transitions = [
            win_rate_transition[0] for win_rate_transition in _win_rate_transitions
        ]
        return win_rate_transitions

    def get_win_rate_transitions_all(self, trainer_id: str) -> List[float]:
        sql = f"""
        with target_trainer as (
            select
                id
            from
                trainer
            where
                identity = '{trainer_id}'
        ),
        target_trainer_battles as (
            select
                battle_id
            from
                battle
            where
                trainer_id in (select id from target_trainer)
        ),
        target_battle_summary as (
            select * from battlesummary
            where
                battle_id in (
                    select
                        battle_id from target_trainer_battles)
        )
        select
            (
                select
                    SUM(
                        case when win_or_lose = 'win' then
                            1.0
                        else
                            0.0
                        end)
                from
                    target_battle_summary as t2
                where
                    t2.created_at <= t1.created_at) / (
                    select
                        COUNT(*)
                    from
                        target_battle_summary as t3
                    where
                        t3.created_at <= t1.created_at) as win_rate
                from
                    target_battle_summary as t1
                order by
                    created_at asc
        """
        self.db.connect()
        _win_rate_transitions: List[Tuple[float]] = self.db.execute_sql(sql).fetchall()
        self.db.close()
        win_rate_transitions: List[float] = [
            win_rate_transition[0] for win_rate_transition in _win_rate_transitions
        ]
        return win_rate_transitions

    def get_next_rank_transitions_season(
        self, season: int, trainer_id: str
    ) -> List[int]:
        sql = f"""
        with target_trainer as (
            select
                id
            from
                trainer
            where
                identity = '{trainer_id}'
        ),
        target_trainer_battles as (
            select
                battle_id
            from
                battle
            where
                trainer_id in (select id from target_trainer)
        ),
        target_battle_summary as (
            select * from battlesummary
            where
                battle_id in (
                    select
                        battle_id from target_trainer_battles)
        ),
        season_start_end as (
            select
                start_datetime,
                end_datetime
            from
                season
            where
                season = {season}
        )
        select
            next_rank
        from
            target_battle_summary
        where
            created_at between(
                select
                    start_datetime from season_start_end)
            and(
                select
                    end_datetime from season_start_end)
        order by
            created_at
        """
        self.db.connect()
        _next_rank_transitions = cast(
            List[Tuple[int]], self.db.execute_sql(sql).fetchall()
        )
        self.db.close()
        next_rank_transitions = [
            next_rank_transition[0] for next_rank_transition in _next_rank_transitions
        ]
        return next_rank_transitions

    def get_next_rank_transitions_all(self, trainer_id: str) -> List[int]:
        sql = f"""
        with target_trainer as (
            select
                id
            from
                trainer
            where
                identity = '{trainer_id}'
        ),
        target_trainer_battles as (
            select
                battle_id
            from
                battle
            where
                trainer_id in (select id from target_trainer)
        ),
        target_battle_summary as (
            select * from battlesummary
            where
                battle_id in (
                    select
                        battle_id from target_trainer_battles)
        )
        select
            next_rank
        from
            target_battle_summary
        order by
            created_at
        """
        self.db.connect()
        _next_rank_transitions: List[Tuple[int]] = self.db.execute_sql(sql).fetchall()
        self.db.close()
        next_rank_transitions: List[int] = [
            next_rank_transition[0] for next_rank_transition in _next_rank_transitions
        ]
        return next_rank_transitions

    def get_recent_battle_history(
        self, trainer_id: str
    ) -> List[Dict[str, Union[str, int]]]:
        sql = f"""
        with target_trainer as (
            select
                id
            from
                trainer
            where
                identity = '{trainer_id}'
        ),
        target_trainer_battles as (
            select
                battle_id
            from
                battle
            where
                trainer_id in (select id from target_trainer)
        ),
        target_battle_summary as (
            select * from battlesummary
            where
                battle_id in (
                    select
                        battle_id from target_trainer_battles)
        )
        select
            battle_id,
            created_at,
            win_or_lose,
            next_rank,
            your_pokemon_1,
            opponent_pokemon_1
        from
            target_battle_summary
        order by
            created_at desc
        limit 5
        """
        self.db.connect()
        _recent_battle_history = self.db.execute_sql(sql).fetchall()
        self.db.close()

        recent_battle_history_dict: List[Dict[str, Union[str, int]]] = [
            {
                "battle_id": battle_id,
                "created_at": created_at,
                "win_or_lose": win_or_lose,
                "next_rank": next_rank,
                "your_pokemon_1": your_pokemon_1,
                "opponent_pokemon_1": opponent_pokemon_1,
            }
            for battle_id, created_at, win_or_lose, next_rank, your_pokemon_1, opponent_pokemon_1 in _recent_battle_history
        ]
        return recent_battle_history_dict

    def get_your_pokemon_stats_summary_all(
        self, trainer_id: str
    ) -> List[Dict[str, Union[str, int, float]]]:
        sql = (
            open("poke_battle_logger/database/sql/your_pokemon_stats_summary.sql")
            .read()
            .format(trainer_id=trainer_id)
        )

        self.db.connect()
        stats = self.db.execute_sql(sql).fetchall()
        self.db.close()

        # merge as pandas
        summary = pd.DataFrame(
            stats,
            columns=[
                "pokemon_name",
                "in_team_rate",
                "in_battle_rate",
                "in_battle_win_rate",
                "head_battle_rate",
                "in_team_count",
                "in_battle_count",
                "in_battle_win_count",
                "head_battle_count",
            ],
        )
        return list(summary.to_dict(orient="index").values())

    def get_your_pokemon_stats_summary_season(
        self, season: int, trainer_id: str
    ) -> List[Dict[str, Union[str, int, float]]]:
        sql = (
            open(
                "poke_battle_logger/database/sql/your_pokemon_stats_summary_in_season.sql"
            )
            .read()
            .format(trainer_id=trainer_id, season=season)
        )

        self.db.connect()
        stats = self.db.execute_sql(sql).fetchall()
        self.db.close()

        # merge as pandas
        summary = pd.DataFrame(
            stats,
            columns=[
                "pokemon_name",
                "in_team_rate",
                "in_battle_rate",
                "in_battle_win_rate",
                "head_battle_rate",
                "in_team_count",
                "in_battle_count",
                "in_battle_win_count",
                "head_battle_count",
            ],
        )
        return list(summary.to_dict(orient="index").values())

    def get_opponent_pokemon_stats_summary_all(
        self, trainer_id: str
    ) -> List[Dict[str, Union[str, int, float]]]:
        sql = (
            open("poke_battle_logger/database/sql/opponent_pokemon_stats_summary.sql")
            .read()
            .format(trainer_id=trainer_id)
        )

        self.db.connect()
        stats = self.db.execute_sql(sql).fetchall()
        self.db.close()

        # merge as pandas
        summary = pd.DataFrame(
            stats,
            columns=[
                "pokemon_name",
                "in_team_rate",
                "in_battle_rate",
                "in_battle_lose_rate",
                "head_battle_rate",
                "in_team_count",
                "in_battle_count",
                "in_battle_win_count",
                "head_battle_count",
            ],
        )
        return list(summary.to_dict(orient="index").values())

    def get_opponent_pokemon_stats_summary_season(
        self, season: int, trainer_id: str
    ) -> List[Dict[str, Union[str, int, float]]]:
        sql = (
            open(
                "poke_battle_logger/database/sql/opponent_pokemon_stats_summary_in_season.sql"
            )
            .read()
            .format(trainer_id=trainer_id, season=season)
        )

        self.db.connect()
        stats = self.db.execute_sql(sql).fetchall()
        self.db.close()

        # merge as pandas
        summary = pd.DataFrame(
            stats,
            columns=[
                "pokemon_name",
                "in_team_rate",
                "in_battle_rate",
                "in_battle_lose_rate",
                "head_battle_rate",
                "in_team_count",
                "in_battle_count",
                "in_battle_win_count",
                "head_battle_count",
            ],
        )
        return list(summary.to_dict(orient="index").values())

    def get_battle_log_all(
        self, trainer_id: str, page: int, size: int
    ) -> List[Dict[str, Union[str, int]]]:
        sql = f"""
        with target_trainer as (
            select
                id
            from
                trainer
            where
                identity = '{trainer_id}'
        ),
        target_trainer_battles as (
            select
                battle_id
            from
                battle
            where
                trainer_id in (select id from target_trainer)
        ),
        target_battle_summary as (
            select * from battlesummary
            where
                battle_id in (
                    select
                        battle_id from target_trainer_battles)
        )
        select
            battle_id,
            created_at,
            win_or_lose,
            next_rank,
            your_team,
            opponent_team,
            your_pokemon_1,
            your_pokemon_2,
            your_pokemon_3,
            opponent_pokemon_1,
            opponent_pokemon_2,
            opponent_pokemon_3,
            memo,
            video
        from
            target_battle_summary
        order by
            created_at desc
        limit {size} offset {size * (page - 1)}
        """
        self.db.connect()
        battle_logs = self.db.execute_sql(sql).fetchall()
        battle_logs_dict: List[Dict[str, Union[str, int]]] = [
            {
                "battle_id": battle_id,
                "battle_created_at": created_at,
                "win_or_lose": win_or_lose,
                "next_rank": next_rank,
                "your_pokemon_team": your_team,
                "opponent_pokemon_team": opponent_team,
                "your_pokemon_select1": your_pokemon_1,
                "your_pokemon_select2": your_pokemon_2,
                "your_pokemon_select3": your_pokemon_3,
                "opponent_pokemon_select1": opponent_pokemon_1,
                "opponent_pokemon_select2": opponent_pokemon_2,
                "opponent_pokemon_select3": opponent_pokemon_3,
                "memo": memo,
                "video": video,
            }
            for (
                battle_id,
                created_at,
                win_or_lose,
                next_rank,
                your_team,
                opponent_team,
                your_pokemon_1,
                your_pokemon_2,
                your_pokemon_3,
                opponent_pokemon_1,
                opponent_pokemon_2,
                opponent_pokemon_3,
                memo,
                video,
            ) in battle_logs
        ]
        self.db.close()
        return battle_logs_dict

    def get_battle_log_all_count(self, trainer_id: str) -> int:
        sql = f"""
        with target_trainer as (
            select
                id
            from
                trainer
            where
                identity = '{trainer_id}'
        ),
        target_trainer_battles as (
            select
                battle_id
            from
                battle
            where
                trainer_id in (select id from target_trainer)
        ),
        target_battle_summary as (
            select * from battlesummary
            where
                battle_id in (
                    select
                        battle_id from target_trainer_battles)
        )
        select
            count(1)
        from
            target_battle_summary
        """
        self.db.connect()
        battle_log_count = cast(int, self.db.execute_sql(sql).fetchone()[0])
        self.db.close()
        return battle_log_count

    def get_battle_log_season(
        self, trainer_id: str, season: int, page: int, size: int
    ) -> List[Dict[str, Union[str, int]]]:
        sql = f"""
        with target_trainer as (
            select
                id
            from
                trainer
            where
                identity = '{trainer_id}'
        ),
        target_trainer_battles as (
            select
                battle_id
            from
                battle
            where
                trainer_id in (select id from target_trainer)
        ),
        season_start_end as (
            select
                start_datetime,
                end_datetime
            from
                season
            where
                season = {season}
        ),
        target_battle_summary as (
            select * from battlesummary
            where
                battle_id in (
                    select
                        battle_id from target_trainer_battles)
                and created_at between(
                    select
                        start_datetime from season_start_end)
                and(
                    select
                        end_datetime from season_start_end)
        )
        select
            battle_id,
            created_at,
            win_or_lose,
            next_rank,
            your_team,
            opponent_team,
            your_pokemon_1,
            your_pokemon_2,
            your_pokemon_3,
            opponent_pokemon_1,
            opponent_pokemon_2,
            opponent_pokemon_3,
            memo,
            video
        from
            target_battle_summary
        order by
            created_at desc
        limit {size} offset {size * (page - 1)}
        """
        self.db.connect()
        battle_logs = self.db.execute_sql(sql).fetchall()
        battle_logs_dict: List[Dict[str, Union[str, int]]] = [
            {
                "battle_id": battle_id,
                "battle_created_at": created_at,
                "win_or_lose": win_or_lose,
                "next_rank": next_rank,
                "your_pokemon_team": your_team,
                "opponent_pokemon_team": opponent_team,
                "your_pokemon_select1": your_pokemon_1,
                "your_pokemon_select2": your_pokemon_2,
                "your_pokemon_select3": your_pokemon_3,
                "opponent_pokemon_select1": opponent_pokemon_1,
                "opponent_pokemon_select2": opponent_pokemon_2,
                "opponent_pokemon_select3": opponent_pokemon_3,
                "memo": memo,
                "video": video,
            }
            for (
                battle_id,
                created_at,
                win_or_lose,
                next_rank,
                your_team,
                opponent_team,
                your_pokemon_1,
                your_pokemon_2,
                your_pokemon_3,
                opponent_pokemon_1,
                opponent_pokemon_2,
                opponent_pokemon_3,
                memo,
                video,
            ) in battle_logs
        ]
        self.db.close()
        return battle_logs_dict

    def get_battle_log_season_count(self, trainer_id: str, season: int) -> int:
        sql = f"""
        with target_trainer as (
            select
                id
            from
                trainer
            where
                identity = '{trainer_id}'
        ),
        target_trainer_battles as (
            select
                battle_id
            from
                battle
            where
                trainer_id in (select id from target_trainer)
        ),
        season_start_end as (
            select
                start_datetime,
                end_datetime
            from
                season
            where
                season = {season}
        ),
        target_battle_summary as (
            select * from battlesummary
            where
                battle_id in (
                    select
                        battle_id from target_trainer_battles)
                and created_at between(
                    select
                        start_datetime from season_start_end)
                and(
                    select
                        end_datetime from season_start_end)
        )
        select
            count(1)
        from
            target_battle_summary
        """
        self.db.connect()
        battle_log_count = cast(int, self.db.execute_sql(sql).fetchone()[0])
        self.db.close()
        return battle_log_count

    def check_trainer_id_exists(self, trainer_id: str) -> bool:
        sql = f"""
        select
            count(*)
        from
            trainer
        where
            identity = '{trainer_id}'
        """
        self.db.connect()
        count = self.db.execute_sql(sql).fetchone()[0]
        self.db.close()
        _result = cast(bool, count > 0)
        return _result

    def save_new_trainer(self, trainer_id: str, email: str) -> None:
        sql = f"""
        insert into
            trainer (identity, email)
        values
            ('{trainer_id}', '{email}')
        """
        self.db.connect()
        self.db.execute_sql(sql)
        self.db.close()

    def get_battle_counts(self, trainer_id: str) -> List[Dict[str, Union[str, int]]]:
        sql = f"""
        with target_trainer as (
            select
                id
            from
                trainer
            where
                identity = '{trainer_id}'
        ),
        target_trainer_battles as (
            select
                battle_id
            from
                battle
            where
                trainer_id in (select id from target_trainer)
        ),
        date_counts as (
            select
                to_char(created_at::timestamp, 'YYYY-MM-DD') as battle_date, count(1) as count
            from
                battlesummary
            where
                battle_id in (
                    select
                        battle_id from target_trainer_battles)
            GROUP BY to_char(created_at::timestamp, 'YYYY-MM-DD')
        )
        select battle_date, sum(count)
        from date_counts
        group by battle_date
        """

        self.db.connect()
        stats = self.db.execute_sql(sql).fetchall()
        summary = pd.DataFrame(
            stats,
            columns=[
                "battle_date",
                "battle_count",
            ],
        )
        self.db.close()
        _res = cast(
            List[Dict[str, Union[str, int]]],
            list(summary.to_dict(orient="index").values()),
        )
        return _res

    def get_in_battle_log(self, battle_id: str) -> List[Dict[str, Union[str, int]]]:
        sql = f"""
        select
            turn,
            frame_number,
            your_pokemon_name,
            opponent_pokemon_name
        from
            inbattlepokemonlog
        where
            battle_id = '{battle_id}'
        """
        self.db.connect()
        stats = self.db.execute_sql(sql).fetchall()
        summary = pd.DataFrame(
            stats,
            columns=[
                "turn",
                "frame_number",
                "your_pokemon_name",
                "opponent_pokemon_name",
            ],
        )
        self.db.close()
        _res = cast(
            List[Dict[str, Union[str, int]]],
            list(summary.to_dict(orient="index").values()),
        )
        return _res

    def update_memo(self, battle_id: str, memo: str) -> None:
        sql = f"""
        update
            battlesummary
        set
            memo = '{memo}'
        where
            battle_id = '{battle_id}'
        """
        self.db.connect()
        self.db.execute_sql(sql)
        self.db.close()

    def get_trainer_id_in_DB(self, trainer_id: str) -> int:
        sql = f"""
        select
            id
        from
            trainer
        where
            identity = '{trainer_id}'
        """
        self.db.connect()
        trainer_id_in_DB: int = self.db.execute_sql(sql).fetchone()[0]
        self.db.close()
        return trainer_id_in_DB

    def get_user_email(self, trainer_id: str) -> str:
        sql = f"""
        select
            email
        from
            trainer
        where
            identity = '{trainer_id}'
        """
        self.db.connect()
        email: str = self.db.execute_sql(sql).fetchone()[0]
        self.db.close()
        return email

    def get_in_battle_message_log(
        self, battle_id: str
    ) -> List[Dict[str, Union[str, int]]]:
        sql = (
            open("poke_battle_logger/database/sql/in_battle_message_log.sql")
            .read()
            .format(battle_id=battle_id)
        )
        self.db.connect()
        stats = self.db.execute_sql(sql).fetchall()
        self.db.close()
        summary = pd.DataFrame(
            stats,
            columns=[
                "turn",
                "frame_number",
                "message",
            ],
        )
        _res = cast(
            List[Dict[str, Union[str, int]]],
            list(summary.to_dict(orient="index").values()),
        )
        return _res

    def build_and_insert_fainted_log(
        self,
        modified_in_battle_pokemons: List[InBattlePokemon],
        modified_messages: List[Message],
    ) -> None:
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
        for _fainted_log in fainted_log:
            FaintedLog.create(
                battle_id=_fainted_log["battle_id"],
                turn=_fainted_log["turn"],
                your_pokemon_name=unicodedata.normalize(
                    "NFC", cast(str, _fainted_log["your_pokemon_name"])
                ),
                opponent_pokemon_name=unicodedata.normalize(
                    "NFC", cast(str, _fainted_log["opponent_pokemon_name"])
                ),
                fainted_pokemon_side=_fainted_log["fainted_pokemon_side"],
            )
        self.db.close()

    def get_fainted_pokemon_log(
        self, battle_id: str
    ) -> List[Dict[str, Union[str, int]]]:
        sql = f"""
        select
            battle_id,
            turn,
            your_pokemon_name,
            opponent_pokemon_name,
            fainted_pokemon_side
        from
            faintedlog
        where
            battle_id = '{battle_id}'
        """
        self.db.connect()
        stats = self.db.execute_sql(sql).fetchall()
        self.db.close()
        summary = pd.DataFrame(
            stats,
            columns=[
                "battle_id",
                "turn",
                "your_pokemon_name",
                "opponent_pokemon_name",
                "fainted_pokemon_side",
            ],
        )
        _res = cast(
            List[Dict[str, Union[str, int]]],
            list(summary.to_dict(orient="index").values()),
        )
        return _res

    def get_your_pokemon_defeat_summary(
        self, trainer_id: str
    ) -> List[Dict[str, Union[str, int]]]:
        sql = (
            open("poke_battle_logger/database/sql/your_pokemon_defeat_summary.sql")
            .read()
            .format(trainer_id=trainer_id)
        )
        self.db.connect()
        stats = self.db.execute_sql(sql).fetchall()
        self.db.close()
        summary = pd.DataFrame(
            stats,
            columns=[
                "your_pokemon_name",
                "opponent_pokemon_name",
                "knock_out_count",
            ],
        )
        _res = cast(
            List[Dict[str, Union[str, int]]],
            list(summary.to_dict(orient="index").values()),
        )
        return _res

    def get_your_pokemon_defeat_summary_in_season(
        self, season: int, trainer_id: str
    ) -> List[Dict[str, Union[str, int]]]:
        sql = (
            open(
                "poke_battle_logger/database/sql/your_pokemon_defeat_summary_in_season.sql"
            )
            .read()
            .format(trainer_id=trainer_id, season=season)
        )
        self.db.connect()
        stats = self.db.execute_sql(sql).fetchall()
        self.db.close()
        summary = pd.DataFrame(
            stats,
            columns=[
                "your_pokemon_name",
                "opponent_pokemon_name",
                "knock_out_count",
            ],
        )
        _res = cast(
            List[Dict[str, Union[str, int]]],
            list(summary.to_dict(orient="index").values()),
        )
        return _res

    def get_opponent_pokemon_defeat_summary(
        self, trainer_id: str
    ) -> List[Dict[str, Union[str, int]]]:
        sql = (
            open("poke_battle_logger/database/sql/opponent_pokemon_defeat_summary.sql")
            .read()
            .format(trainer_id=trainer_id)
        )
        self.db.connect()
        stats = self.db.execute_sql(sql).fetchall()
        self.db.close()
        summary = pd.DataFrame(
            stats,
            columns=[
                "your_pokemon_name",
                "opponent_pokemon_name",
                "knock_out_count",
            ],
        )
        _res = cast(
            List[Dict[str, Union[str, int]]],
            list(summary.to_dict(orient="index").values()),
        )
        return _res

    def get_opponent_pokemon_defeat_summary_in_season(
        self, season: int, trainer_id: str
    ) -> List[Dict[str, Union[str, int]]]:
        sql = (
            open(
                "poke_battle_logger/database/sql/opponent_pokemon_defeat_summary_in_season.sql"
            )
            .read()
            .format(trainer_id=trainer_id, season=season)
        )
        self.db.connect()
        stats = self.db.execute_sql(sql).fetchall()
        self.db.close()
        summary = pd.DataFrame(
            stats,
            columns=[
                "your_pokemon_name",
                "opponent_pokemon_name",
                "knock_out_count",
            ],
        )
        _res = cast(
            List[Dict[str, Union[str, int]]],
            list(summary.to_dict(orient="index").values()),
        )
        return _res

    def update_video_process_status(
        self, trainer_id_in_DB: int, video_id: str, status: str
    ) -> None:
        # postgresql upsert
        sql = f"""
        insert into
            battlevideo (trainer_id, video_id, process_status)
        values
            ('{trainer_id_in_DB}', '{video_id}', '{status}')
        on conflict (trainer_id, video_id)
        do update set
            process_status = '{status}'
        """

        self.db.connect()
        self.db.execute_sql(sql)
        self.db.close()

    def get_battle_video_status_list(self, trainer_id: str) -> list[dict[str, str]]:
        sql = f"""
        with target_trainer as (
            select
                id
            from
                trainer
            where
                identity = '{trainer_id}'
        )
        select
            video_id,
            registered_at,
            process_status
        from
            battlevideo
        where
            trainer_id in (select id from target_trainer)
        """
        self.db.connect()
        stats = self.db.execute_sql(sql).fetchall()
        self.db.close()
        summary = pd.DataFrame(
            stats,
            columns=[
                "videoId",
                "registeredAt",
                "status",
            ],
        )
        summary["registeredAt"] = summary["registeredAt"].dt.strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        _res = cast(
            list[Dict[str, str]],
            list(summary.to_dict(orient="index").values()),
        )
        return _res

    def get_seasons(self) -> list[dict[str, int | str]]:
        sql = """
        select
            season,
            start_datetime,
            end_datetime
        from
            season
        order by
            season desc
        """
        self.db.connect()
        stats = self.db.execute_sql(sql).fetchall()
        self.db.close()
        summary = pd.DataFrame(
            stats,
            columns=[
                "season",
                "start_datetime",
                "end_datetime",
            ],
        )
        summary["start_date"] = pd.to_datetime(summary["start_datetime"]).dt.strftime(
            "%Y/%m/%d"
        )
        summary["end_date"] = pd.to_datetime(summary["end_datetime"]).dt.strftime(
            "%Y/%m/%d"
        )
        summary["seasonStartEnd"] = (
            "シーズン"
            + summary["season"].apply(str)
            + " "
            + summary["start_date"]
            + " - "
            + summary["end_date"]
        )
        summary2 = summary[["season", "seasonStartEnd"]]
        _res = cast(
            list[Dict[str, int | str]],
            list(summary2.to_dict(orient="index").values()),
        )
        return _res

    def search_battles(self, trainer_id: str, season: int, my_pokemons: list[str], opponent_pokemons: list[str]) -> list[dict[str, str | int]]:
        sql = f"""
        with target_trainer as (
            select
                id
            from
                trainer
            where
                id = '{trainer_id}'
        ),
        target_trainer_battles as (
            select
                battle_id
            from
                battle
            where
                trainer_id in (select id from target_trainer)
        )
        select
            battle_id,
            created_at,
            win_or_lose,
            next_rank,
            your_team,
            opponent_team,
            your_pokemon_1,
            your_pokemon_2,
            your_pokemon_3,
            opponent_pokemon_1,
            opponent_pokemon_2,
            opponent_pokemon_3,
            memo
        from battlesummary
        where
            string_to_array(your_team, ',') @> array['{my_pokemons[0]}', '{my_pokemons[1]}', '{my_pokemons[2]}', '{my_pokemons[3]}', '{my_pokemons[4]}', '{my_pokemons[5]}']
            and string_to_array(opponent_team, ',') @> array['{opponent_pokemons[0]}', '{opponent_pokemons[1]}', '{opponent_pokemons[2]}', '{opponent_pokemons[3]}', '{opponent_pokemons[4]}', '{opponent_pokemons[5]}']
            and battle_id in (
                select
                    battle_id from target_trainer_battles)
        """
        self.db.connect()
        stats = self.db.execute_sql(sql).fetchall()
        self.db.close()

        summary = pd.DataFrame(
            stats,
            columns=[
                "battle_id",
                "created_at",
                "win_or_lose",
                "next_rank",
                "your_team",
                "opponent_team",
                "your_pokemon_1",
                "your_pokemon_2",
                "your_pokemon_3",
                "opponent_pokemon_1",
                "opponent_pokemon_2",
                "opponent_pokemon_3",
                "memo"
            ],
        )
        _res = cast(
            list[Dict[str, str | int]],
            list(summary.to_dict(orient="index").values()),
        )
        return _res
