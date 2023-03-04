import random
from typing import List

from peewee import ForeignKeyField, IntegerField, Model, SqliteDatabase, TextField

db = SqliteDatabase("poke_battle_logger.db")


class BaseModel(Model):
    class Meta:
        database = db


class Battle(BaseModel):
    battle_id = TextField(unique=True)


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


class InBattlePokemonLog(BaseModel):
    battle_id = ForeignKeyField(Battle, backref="battlePokemonTeams")
    turn = IntegerField()
    your_pokemon_name = TextField()
    opponent_pokemon_name = TextField()


class BattlePokemonTeam(BaseModel):
    battle_id = ForeignKeyField(Battle, backref="inBattlePokemonLogs")
    team = TextField()
    pokemon_name = TextField()


class Season(BaseModel):
    id = IntegerField(unique=True)
    season = IntegerField()
    start_datetime = TextField()
    end_datetime = TextField()


class SQLiteHandler:
    def __init__(self):
        self.db = SqliteDatabase("poke_battle_logger.db")

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

    def insert_battle_id(self, battle_ids):
        with self.db:
            for battle_id in battle_ids:
                Battle.create(battle_id=battle_id)

    def insert_battle_summary(self, battle_summary):
        with self.db:
            for _battle_summary in battle_summary:
                BattleSummary.create(
                    battle_id=_battle_summary["battle_id"],
                    created_at=_battle_summary["created_at"],
                    win_or_lose=_battle_summary["win_or_lose"],
                    next_rank=_battle_summary["next_rank"],
                    your_team=_battle_summary["your_team"],
                    opponent_team=_battle_summary["opponent_team"],
                    your_pokemon_1=_battle_summary["your_pokemon_1"],
                    your_pokemon_2=_battle_summary["your_pokemon_2"],
                    your_pokemon_3=_battle_summary["your_pokemon_3"],
                    opponent_pokemon_1=_battle_summary["opponent_pokemon_1"],
                    opponent_pokemon_2=_battle_summary["opponent_pokemon_2"],
                    opponent_pokemon_3=_battle_summary["opponent_pokemon_3"],
                    video=_battle_summary["video"],
                )

    def insert_battle_pokemon_team(self, battle_pokemon_team):
        with self.db:
            for _battle_pokemon_team in battle_pokemon_team:
                BattlePokemonTeam.create(
                    battle_id=_battle_pokemon_team["battle_id"],
                    team=_battle_pokemon_team["team"],
                    pokemon_name=_battle_pokemon_team["pokemon_name"],
                )

    def insert_in_battle_pokemon_log(self, in_battle_pokemon_log):
        with self.db:
            for _in_battle_pokemon_log in in_battle_pokemon_log:
                InBattlePokemonLog.create(
                    battle_id=_in_battle_pokemon_log["battle_id"],
                    turn=_in_battle_pokemon_log["turn"],
                    your_pokemon_name=_in_battle_pokemon_log["your_pokemon_name"],
                    opponent_pokemon_name=_in_battle_pokemon_log[
                        "opponent_pokemon_name"
                    ],
                )

    def get_latest_season_win_rate(self) -> float:
        sql = """
        with latest_season_start_end as (
            select
                start_datetime,
                end_datetime
            from
                season
            order by season desc
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
        order by
            created_at
        """
        with self.db:
            win_rate = self.db.execute_sql(sql).fetchone()[0]
        return win_rate

    def get_latest_season_rank(self) -> int:
        sql = """
        with latest_season_start_end as (
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
        order by
            created_at desc
        limit 1
        """
        with self.db:
            latest_season_rank = self.db.execute_sql(sql).fetchone()[0]
        return latest_season_rank

    def get_latest_win_pokemon(self) -> str:
        sql = """
        select
            opponent_pokemon_1, opponent_pokemon_2, opponent_pokemon_3
        from
            battlesummary
        where
            win_or_lose = "win"
        order by
            created_at desc
        limit 1
        """
        with self.db:
            latest_win_pokemons = self.db.execute_sql(sql).fetchone()
            # ランダムに1匹選ぶ
            latest_win_pokemon = random.choice(latest_win_pokemons)
        return latest_win_pokemon

    def get_latest_lose_pokemon(self) -> str:
        sql = """
        select
            opponent_pokemon_1, opponent_pokemon_2, opponent_pokemon_3
        from
            battlesummary
        where
            win_or_lose = "lose"
        order by
            created_at desc
        limit 1
        """
        with self.db:
            latest_lose_pokemons = self.db.execute_sql(sql).fetchone()
            print(latest_lose_pokemons)
            # ランダムに1匹選ぶ
            latest_lose_pokemon = random.choice(latest_lose_pokemons)
        return latest_lose_pokemon

    def get_win_rate_transitions(self, season: int) -> List[float]:
        sql = f"""
        with season_start_end as (
            select
                start_datetime,
                end_datetime
            from
                season
            where
                season = {season}
        )
        select
            (
                select
                    COUNT(*)
                from
                    battlesummary t2
                where
                    t2.id <= t1.id
                    and t2.win_or_lose = 'win') * 1.0 / id as win_rate
            from
                battlesummary t1
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
            win_rate_transitions = self.db.execute_sql(sql).fetchall()
        return win_rate_transitions
