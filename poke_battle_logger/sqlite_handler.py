import random
from typing import Dict, List, Union

import pandas as pd
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
            # ランダムに1匹選ぶ
            latest_lose_pokemon = random.choice(latest_lose_pokemons)
        return latest_lose_pokemon

    def get_win_rate_transitions_season(self, season: int) -> List[float]:
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
        win_rate_transitions = [
            win_rate_transition[0] for win_rate_transition in win_rate_transitions
        ]
        return win_rate_transitions

    def get_next_rank_transitions_season(self, season: int) -> List[int]:
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
            next_rank
        from
            battlesummary
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

    def get_recent_battle_history(self) -> List[Dict[str, Union[str, int]]]:
        sql = """
        select
            battle_id,
            created_at,
            win_or_lose,
            next_rank,
            your_pokemon_1,
            opponent_pokemon_1
        from
            battlesummary
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

    def get_your_pokemon_stats_summary_all(self) -> List[Dict[str, Union[str, int, float]]]:
        sql_in_team_count = """
        -- 採用回数
        select
            pokemon_name,
            count(1)
        from
            battlepokemonteam
        where
            team = 'you'
        group by pokemon_name
        """
        sql_in_battle_count = """
        -- 選出回数
        with first as (
            select
                your_pokemon_1 as pokemon_name,
                count(1) as counts
            from
                battlesummary
            group by
                your_pokemon_1
        ),
        second as (
            select
                your_pokemon_2 as pokemon_name,
                count(1) as counts
            from
                battlesummary
            group by
                your_pokemon_2
        ),
        third as (
            select
                your_pokemon_3 as pokemon_name,
                count(1) as counts
            from
                battlesummary
            group by
                your_pokemon_3
        ),
        unions as (
            select
                *
            from
                first
            union
            select
                *
            from
                second
            union
            select
                *
            from
                third
        )
        select
            pokemon_name,
            sum(counts)
        from
            unions
        group by pokemon_name
        """
        sql_in_battle_win_count = """
        -- 勝利したときの選出回数
        with first as (
            select
                your_pokemon_1 as pokemon_name,
                count(1) as counts
            from
                battlesummary
            where
                win_or_lose = 'win'
            group by
                your_pokemon_1
        ),
        second as (
            select
                your_pokemon_2 as pokemon_name,
                count(1) as counts
            from
                battlesummary
            where
                win_or_lose = 'win'
            group by
                your_pokemon_2
        ),
        third as (
            select
                your_pokemon_3 as pokemon_name,
                count(1) as counts
            from
                battlesummary
            where
                win_or_lose = 'win'
            group by
                your_pokemon_3
        ),
        unions as (
            select
                *
            from
                first
            union
            select
                *
            from
                second
            union
            select
                *
            from
                third
        )
        select
            pokemon_name,
            sum(counts)
        from
            unions
        group by pokemon_name
        """
        sql_head_battle_count = """
        -- 選出されたときの先発回数
        select
            your_pokemon_1 as pokemon_name,
            count(1) as counts
        from
            battlesummary
        group by
            your_pokemon_1
        """

        with self.db:
            in_team_count = self.db.execute_sql(sql_in_team_count).fetchall()
            in_battle_count = self.db.execute_sql(sql_in_battle_count).fetchall()
            in_battle_win_count = self.db.execute_sql(
                sql_in_battle_win_count
            ).fetchall()
            head_battle_count = self.db.execute_sql(sql_head_battle_count).fetchall()

            # merge as pandas
            df_in_team_count = pd.DataFrame(
                in_team_count, columns=["pokemon_name", "in_team_count"]
            )
            df_in_battle_count = pd.DataFrame(
                in_battle_count, columns=["pokemon_name", "in_battle_count"]
            )
            df_in_battle_win_count = pd.DataFrame(
                in_battle_win_count, columns=["pokemon_name", "in_battle_win_count"]
            )
            df_head_battle_count = pd.DataFrame(
                head_battle_count, columns=["pokemon_name", "head_battle_count"]
            )
            merge_df = pd.merge(
                df_in_team_count,
                df_in_battle_count,
                on="pokemon_name",
                how="outer",
            )
            merge_df = pd.merge(
                merge_df, df_in_battle_win_count, on="pokemon_name", how="outer"
            )
            merge_df = pd.merge(
                merge_df, df_head_battle_count, on="pokemon_name", how="outer"
            )
            merge_df = merge_df.fillna(0)

        # 割合にする
        merge_df["in_battle_rate"] = (
            merge_df["in_battle_count"] / merge_df["in_team_count"]
        )
        merge_df["head_battle_rate"] = (
            merge_df["head_battle_count"] / merge_df["in_team_count"]
        )
        merge_df["in_battle_win_rate"] = (
            merge_df["in_battle_win_count"] / merge_df["in_battle_count"]
        )
        return list(merge_df.to_dict(orient="index").values())

    def get_your_pokemon_stats_summary_season(self, season: int) -> List[Dict[str, Union[str, int, float]]]:
        sql_battle_num = f"""
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
            count(1)
        from
            battlesummary
        where
            created_at between(
                select
                    start_datetime from season_start_end)
            and(
                select
                    end_datetime from season_start_end)
        """
        sql_in_team_count = f"""
        with season_start_end as (
            select
                start_datetime,
                end_datetime
            from
                season
            where
                season = {season}
        ),
        target_battles as (
            select
                battle_id
            from
                battlesummary
            where
                created_at between(
                    select
                        start_datetime from season_start_end)
                and(
                    select
                        end_datetime from season_start_end)
        )
        select
            pokemon_name, count(1)
        from
            battlepokemonteam
        where
            team = 'you'
            and battle_id in(
                select
                    battle_id from target_battles)
        group by
            pokemon_name
        """
        sql_in_battle_count = f"""
        -- 選出回数
        with season_start_end as (
            select
                start_datetime,
                end_datetime
            from
                season
            where
                season = {season}
        ), first as (
            select
                your_pokemon_1 as pokemon_name,
                count(1) as counts
            from
                battlesummary
            where
                created_at between(
                    select
                        start_datetime from season_start_end)
                and(
                    select
                        end_datetime from season_start_end)
            group by
                your_pokemon_1
        ),
        second as (
            select
                your_pokemon_2 as pokemon_name,
                count(1) as counts
            from
                battlesummary
            where
                created_at between(
                    select
                        start_datetime from season_start_end)
                and(
                    select
                        end_datetime from season_start_end)
            group by
                your_pokemon_2
        ),
        third as (
            select
                your_pokemon_3 as pokemon_name,
                count(1) as counts
            from
                battlesummary
            where
                created_at between(
                    select
                        start_datetime from season_start_end)
                and(
                    select
                        end_datetime from season_start_end)
            group by
                your_pokemon_3
        ),
        unions as (
            select
                *
            from
                first
            union
            select
                *
            from
                second
            union
            select
                *
            from
                third
        )
        select
            pokemon_name,
            sum(counts)
        from
            unions
        group by pokemon_name
        """
        sql_in_battle_win_count = f"""
        -- 勝利したときの選出回数
        with season_start_end as (
            select
                start_datetime,
                end_datetime
            from
                season
            where
                season = {season}
        ), first as (
            select
                your_pokemon_1 as pokemon_name,
                count(1) as counts
            from
                battlesummary
            where
                win_or_lose = 'win'
                and created_at between(
                    select
                        start_datetime from season_start_end)
                and(
                    select
                        end_datetime from season_start_end)
            group by
                your_pokemon_1
        ),
        second as (
            select
                your_pokemon_2 as pokemon_name,
                count(1) as counts
            from
                battlesummary
            where
                win_or_lose = 'win'
                and created_at between(
                    select
                        start_datetime from season_start_end)
                and(
                    select
                        end_datetime from season_start_end)
            group by
                your_pokemon_2
        ),
        third as (
            select
                your_pokemon_3 as pokemon_name,
                count(1) as counts
            from
                battlesummary
            where
                win_or_lose = 'win'
                and created_at between(
                    select
                        start_datetime from season_start_end)
                and(
                    select
                        end_datetime from season_start_end)
            group by
                your_pokemon_3
        ),
        unions as (
            select
                *
            from
                first
            union
            select
                *
            from
                second
            union
            select
                *
            from
                third
        )
        select
            pokemon_name,
            sum(counts)
        from
            unions
        group by pokemon_name
        """
        sql_head_battle_count = f"""
        with season_start_end as (
            select
                start_datetime,
                end_datetime
            from
                season
            where
                season = {season}
        )
        -- 選出されたときの先発回数
        select
            your_pokemon_1 as pokemon_name,
            count(1) as counts
        from
            battlesummary
        where created_at between(
                    select
                        start_datetime from season_start_end)
                and(
                    select
                        end_datetime from season_start_end)
        group by
            your_pokemon_1
        """

        with self.db:
            battle_num = self.db.execute_sql(sql_battle_num).fetchone()[0]
            in_team_count = self.db.execute_sql(sql_in_team_count).fetchall()
            in_battle_count = self.db.execute_sql(sql_in_battle_count).fetchall()
            in_battle_win_count = self.db.execute_sql(
                sql_in_battle_win_count
            ).fetchall()
            head_battle_count = self.db.execute_sql(sql_head_battle_count).fetchall()

            # merge as pandas
            df_in_team_count = pd.DataFrame(
                in_team_count, columns=["pokemon_name", "in_team_count"]
            )
            df_in_battle_count = pd.DataFrame(
                in_battle_count, columns=["pokemon_name", "in_battle_count"]
            )
            df_in_battle_win_count = pd.DataFrame(
                in_battle_win_count, columns=["pokemon_name", "in_battle_win_count"]
            )
            df_head_battle_count = pd.DataFrame(
                head_battle_count, columns=["pokemon_name", "head_battle_count"]
            )
            merge_df = pd.merge(
                df_in_team_count,
                df_in_battle_count,
                on="pokemon_name",
                how="outer",
            )
            merge_df = pd.merge(
                merge_df, df_in_battle_win_count, on="pokemon_name", how="outer"
            )
            merge_df = pd.merge(
                merge_df, df_head_battle_count, on="pokemon_name", how="outer"
            )
            merge_df = merge_df.fillna(0)

        # 割合にする
        merge_df["in_team_rate"] = (
            merge_df["in_team_count"] / battle_num
        )
        merge_df["in_battle_rate"] = (
            merge_df["in_battle_count"] / merge_df["in_team_count"]
        )
        merge_df["head_battle_rate"] = (
            merge_df["head_battle_count"] / merge_df["in_team_count"]
        )
        merge_df["in_battle_win_rate"] = (
            merge_df["in_battle_win_count"] / merge_df["in_battle_count"]
        )
        return list(merge_df.to_dict(orient="index").values())
