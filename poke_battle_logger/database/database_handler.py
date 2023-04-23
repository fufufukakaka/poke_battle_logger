import os
import random
import unicodedata
from typing import Dict, List, Union

import pandas as pd
from peewee import (
    ForeignKeyField,
    IntegerField,
    Model,
    PostgresqlDatabase,
    SqliteDatabase,
    TextField,
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


class BaseModel(Model):
    class Meta:
        database = build_db_connection()


class Battle(BaseModel):
    battle_id = TextField(unique=True)
    trainer_id = IntegerField()


class BattleSummary(BaseModel):
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


class InBattlePokemonLog(BaseModel):
    battle_id = ForeignKeyField(Battle, backref="battlePokemonTeams")
    turn = IntegerField()
    frame_number = IntegerField()
    your_pokemon_name = TextField()
    opponent_pokemon_name = TextField()


class MessageLog(BaseModel):
    battle_id = ForeignKeyField(Battle, backref="battleMessages")
    frame_number = IntegerField()
    message = TextField()


class BattlePokemonTeam(BaseModel):
    battle_id = ForeignKeyField(Battle, backref="inBattlePokemonLogs")
    team = TextField()
    pokemon_name = TextField()


class Season(BaseModel):
    season = IntegerField()
    start_datetime = TextField()
    end_datetime = TextField()


class Trainer(BaseModel):
    identity = TextField()


class SQLiteHandler:
    def __init__(self):
        self.db = build_db_connection()

    def create_tables(self):
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

    def insert_battle_id(self, battles):
        with self.db:
            for _battle in battles:
                Battle.create(
                    battle_id=_battle["battle_id"], trainer_id=_battle["trainer_id"]
                )

    def insert_battle_summary(self, battle_summary):
        with self.db:
            for _battle_summary in battle_summary:
                BattleSummary.create(
                    battle_id=_battle_summary["battle_id"],
                    created_at=_battle_summary["created_at"],
                    win_or_lose=_battle_summary["win_or_lose"],
                    next_rank=_battle_summary["next_rank"],
                    your_team=unicodedata.normalize(
                        "NFC", _battle_summary["your_team"]
                    ),
                    opponent_team=unicodedata.normalize(
                        "NFC", _battle_summary["opponent_team"]
                    ),
                    your_pokemon_1=unicodedata.normalize(
                        "NFC", _battle_summary["your_pokemon_1"]
                    ),
                    your_pokemon_2=unicodedata.normalize(
                        "NFC", _battle_summary["your_pokemon_2"]
                    ),
                    your_pokemon_3=unicodedata.normalize(
                        "NFC", _battle_summary["your_pokemon_3"]
                    ),
                    opponent_pokemon_1=unicodedata.normalize(
                        "NFC", _battle_summary["opponent_pokemon_1"]
                    ),
                    opponent_pokemon_2=unicodedata.normalize(
                        "NFC", _battle_summary["opponent_pokemon_2"]
                    ),
                    opponent_pokemon_3=unicodedata.normalize(
                        "NFC", _battle_summary["opponent_pokemon_3"]
                    ),
                    video=_battle_summary["video"],
                    memo="",
                )

    def insert_battle_pokemon_team(self, battle_pokemon_team):
        with self.db:
            for _battle_pokemon_team in battle_pokemon_team:
                BattlePokemonTeam.create(
                    battle_id=_battle_pokemon_team["battle_id"],
                    team=_battle_pokemon_team["team"],
                    pokemon_name=unicodedata.normalize(
                        "NFC", _battle_pokemon_team["pokemon_name"]
                    ),
                )

    def insert_in_battle_pokemon_log(self, in_battle_pokemon_log):
        with self.db:
            for _in_battle_pokemon_log in in_battle_pokemon_log:
                InBattlePokemonLog.create(
                    battle_id=_in_battle_pokemon_log["battle_id"],
                    turn=_in_battle_pokemon_log["turn"],
                    frame_number=_in_battle_pokemon_log["frame_number"],
                    your_pokemon_name=unicodedata.normalize(
                        "NFC", _in_battle_pokemon_log["your_pokemon_name"]
                    ),
                    opponent_pokemon_name=unicodedata.normalize(
                        "NFC", _in_battle_pokemon_log["opponent_pokemon_name"]
                    ),
                )

    def insert_message_log(self, message_log):
        with self.db:
            for _message_log in message_log:
                MessageLog.create(
                    battle_id=_message_log["battle_id"],
                    frame_number=_message_log["frame_number"],
                    message=_message_log["message"],
                )

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
        )
        select
            CAST(sum(
                    case when win_or_lose = "win" then
                        1
                    else
                        0
                    end) as float) / count(1) as win_rate
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
            created_at
        """
        with self.db:
            win_rate = self.db.execute_sql(sql).fetchone()[0]
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
        with self.db:
            latest_season_rank = self.db.execute_sql(sql).fetchone()[0]
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
            win_or_lose = "win"
            and battle_id in (
                select
                    battle_id from target_trainer_battles)
        order by
            created_at desc
        limit 1
        """
        with self.db:
            latest_win_pokemons = self.db.execute_sql(sql).fetchone()
            # ランダムに1匹選ぶ
            latest_win_pokemon = random.choice(latest_win_pokemons)
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
            win_or_lose = "lose"
            and battle_id in (
                select
                    battle_id from target_trainer_battles)
        order by
            created_at desc
        limit 1
        """
        with self.db:
            latest_lose_pokemons = self.db.execute_sql(sql).fetchone()
            # Unseen を除いてランダムに1匹選ぶ
            latest_lose_pokemon = random.choice(
                [pokemon for pokemon in latest_lose_pokemons if pokemon != "Unseen"]
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
        with self.db:
            win_rate_transitions = self.db.execute_sql(sql).fetchall()
        win_rate_transitions = [
            win_rate_transition[0] for win_rate_transition in win_rate_transitions
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
        with self.db:
            win_rate_transitions = self.db.execute_sql(sql).fetchall()
        win_rate_transitions = [
            win_rate_transition[0] for win_rate_transition in win_rate_transitions
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
        with self.db:
            next_rank_transitions = self.db.execute_sql(sql).fetchall()
        next_rank_transitions = [
            next_rank_transition[0] for next_rank_transition in next_rank_transitions
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
        with self.db:
            next_rank_transitions = self.db.execute_sql(sql).fetchall()
        next_rank_transitions = [
            next_rank_transition[0] for next_rank_transition in next_rank_transitions
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
        with self.db:
            recent_battle_history = self.db.execute_sql(sql).fetchall()
            recent_battle_history_dict = [
                {
                    "battle_id": battle_id,
                    "created_at": created_at,
                    "win_or_lose": win_or_lose,
                    "next_rank": next_rank,
                    "your_pokemon_1": your_pokemon_1,
                    "opponent_pokemon_1": opponent_pokemon_1,
                }
                for battle_id, created_at, win_or_lose, next_rank, your_pokemon_1, opponent_pokemon_1 in recent_battle_history
            ]
        return recent_battle_history_dict

    def get_your_pokemon_stats_summary_all(
        self, trainer_id: str
    ) -> List[Dict[str, Union[str, int, float]]]:
        sql = (
            open("sql/your_pokemon_stats_summary.sql")
            .read()
            .format(trainer_id=trainer_id)
        )

        with self.db:
            stats = self.db.execute_sql(sql).fetchall()

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
            open("sql/your_pokemon_stats_summary_in_season.sql")
            .read()
            .format(trainer_id=trainer_id, season=season)
        )

        with self.db:
            stats = self.db.execute_sql(sql).fetchall()

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
            open("sql/opponent_pokemon_stats_summary.sql")
            .read()
            .format(trainer_id=trainer_id)
        )

        with self.db:
            stats = self.db.execute_sql(sql).fetchall()

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
            open("sql/opponent_pokemon_stats_summary_in_season.sql")
            .read()
            .format(trainer_id=trainer_id, season=season)
        )

        with self.db:
            stats = self.db.execute_sql(sql).fetchall()

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

    def get_battle_log_all(self, trainer_id: str):
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
        """
        with self.db:
            battle_logs = self.db.execute_sql(sql).fetchall()
            battle_logs_dict = [
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
        return battle_logs_dict

    def get_battle_log_season(self, trainer_id: str, season: int):
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
        """
        with self.db:
            battle_logs = self.db.execute_sql(sql).fetchall()
            battle_logs_dict = [
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
        return battle_logs_dict

    def check_trainer_id_exists(self, trainer_id: str) -> bool:
        sql = f"""
        select
            count(*)
        from
            trainer
        where
            identity = '{trainer_id}'
        """
        with self.db:
            count = self.db.execute_sql(sql).fetchone()[0]
        return count > 0

    def save_new_trainer(self, trainer_id: str) -> None:
        sql = f"""
        insert into
            trainer
        values
            ('{trainer_id}')
        """
        with self.db:
            self.db.execute_sql(sql)

    def get_battle_counts(self, trainer_id: str):
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
            strftime('%Y-%m-%d',created_at) as battle_date, count(1)
        from
            battlesummary
        where
            battle_id in (
                select
                    battle_id from target_trainer_battles)
        group by battle_date
        """
        with self.db:
            stats = self.db.execute_sql(sql).fetchall()
            summary = pd.DataFrame(
                stats,
                columns=[
                    "battle_date",
                    "battle_count",
                ],
            )
        return list(summary.to_dict(orient="index").values())

    def get_in_battle_log(self, battle_id: str):
        sql = f"""
        select
            turn,
            frame_number,
            your_pokemon_name,
            opponent_pokemon_name
        from
            inbattlepokemonlog
        where
            battle_id = "{battle_id}"
        """
        with self.db:
            stats = self.db.execute_sql(sql).fetchall()
            summary = pd.DataFrame(
                stats,
                columns=[
                    "turn",
                    "frame_number",
                    "your_pokemon_name",
                    "opponent_pokemon_name"
                ],
            )
        return list(summary.to_dict(orient="index").values())

    def update_memo(self, battle_id: str, memo: str):
        sql = f"""
        update
            battlesummary
        set
            memo = '{memo}'
        where
            battle_id = '{battle_id}'
        """
        with self.db:
            self.db.execute_sql(sql)

    def get_trainer_id_in_DB(self, trainer_id: str) -> int:
        sql = f"""
        select
            id
        from
            trainer
        where
            identity = '{trainer_id}'
        """
        with self.db:
            trainer_id_in_DB: int = self.db.execute_sql(sql).fetchone()[0]
        return trainer_id_in_DB
