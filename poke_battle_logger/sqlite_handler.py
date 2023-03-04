import datetime

from peewee import (
    DateTimeField,
    ForeignKeyField,
    IntegerField,
    Model,
    SqliteDatabase,
    TextField,
)

db = SqliteDatabase("my_database.db")


class BaseModel(Model):
    class Meta:
        database = db


class Battle(BaseModel):
    battle_id = TextField(unique=True)


class BattleSummary(BaseModel):
    battle_id = ForeignKeyField(Battle, backref="battleSummarys")
    created_at = DateTimeField(default=datetime.datetime.now)
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
