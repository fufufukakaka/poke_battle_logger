import logging
import unicodedata
from logging import getLogger
from typing import Dict, List, Union
from pydantic import BaseModel
import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from rich.logging import RichHandler

from poke_battle_logger.sqlite_handler import SQLiteHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler()],
)
logger = getLogger(__name__)

app = FastAPI()
origins = [
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


sqlite_handler = SQLiteHandler()
pokemon_name_df = pd.read_csv("data/pokemon_names.csv")
pokemon_japanese_to_no_dict = dict(
    zip(pokemon_name_df["Japanese"], pokemon_name_df["No."])
)
pokemon_japanese_to_english_dict = dict(
    zip(pokemon_name_df["Japanese"], pokemon_name_df["English"])
)


@app.get("/hello")
async def hello_revision() -> str:
    return "hello poke_battle_logger API"


@app.get("/api/v1/pokemon_name_to_no")
async def get_pokemon_name_to_no(pokemon_name: str) -> int:
    return pokemon_japanese_to_no_dict[pokemon_name]


@app.get("/api/v1/recent_battle_summary")
async def get_recent_battle_summary(trainer_id: str) -> Dict[
    str, Union[float, int, str, List[Dict[str, Union[str, int]]]]
]:
    win_rate = sqlite_handler.get_latest_season_win_rate(trainer_id)
    latest_rank = sqlite_handler.get_latest_season_rank(trainer_id)
    latest_win_pokemon = sqlite_handler.get_latest_win_pokemon(trainer_id)
    latest_lose_pokemon = sqlite_handler.get_latest_lose_pokemon(trainer_id)
    recent_battle_history = sqlite_handler.get_recent_battle_history(trainer_id)

    return {
        "win_rate": win_rate,
        "latest_rank": latest_rank,
        "latest_win_pokemon": latest_win_pokemon,
        "latest_lose_pokemon": latest_lose_pokemon,
        "recent_battle_history": recent_battle_history,
    }


@app.get("/api/v1/analytics")
async def get_analytics(
    trainer_id: str, season: int,
) -> Dict[str, Union[List[float], List[int], List[Dict[str, Union[str, int, float]]]]]:
    if season == 0:
        win_rate_transition = sqlite_handler.get_win_rate_transitions_all(trainer_id)
        next_rank_transition = sqlite_handler.get_next_rank_transitions_all(trainer_id)
        your_pokemon_stats_summary = sqlite_handler.get_your_pokemon_stats_summary_all(trainer_id)
        opponent_pokemon_stats_summary = (
            sqlite_handler.get_opponent_pokemon_stats_summary_all(trainer_id)
        )
    elif season > 0:
        win_rate_transition = sqlite_handler.get_win_rate_transitions_season(season, trainer_id)
        next_rank_transition = sqlite_handler.get_next_rank_transitions_season(season, trainer_id)
        your_pokemon_stats_summary = (
            sqlite_handler.get_your_pokemon_stats_summary_season(season, trainer_id)
        )
        opponent_pokemon_stats_summary = (
            sqlite_handler.get_opponent_pokemon_stats_summary_season(season, trainer_id)
        )
    else:
        raise ValueError("season must be 0 or positive")
    return {
        "winRate": win_rate_transition,
        "nextRank": next_rank_transition,
        "yourPokemonStatsSummary": your_pokemon_stats_summary,
        "opponentPokemonStatsSummary": opponent_pokemon_stats_summary,
    }


@app.get("/api/v1/battle_log")
async def get_battle_log(
    trainer_id: str, season: int,
) -> List[Dict[str, Union[str, int, float]]]:
    if season == 0:
        battle_log = sqlite_handler.get_battle_log_all(trainer_id)
    elif season > 0:
        battle_log = sqlite_handler.get_battle_log_season(trainer_id, season)
    else:
        raise ValueError("season must be 0 or positive")
    return battle_log


@app.get("/api/v1/pokemon_image_url")
async def get_pokemon_image_url(
    pokemon_name: str,
) -> str:
    pokemon_name = unicodedata.normalize("NFC", pokemon_name)
    # Unseen の場合は Unseen Image を返す
    if pokemon_name == "Unseen":
        return "https://upload.wikimedia.org/wikipedia/commons/5/53/Pok%C3%A9_Ball_icon.svg"
    # もしカタカナだったら英語に直す
    if pokemon_name in pokemon_japanese_to_english_dict:
        pokemon_name = pokemon_japanese_to_english_dict[pokemon_name]
    # lowerに変換・空白はハイフンに変換
    pokemon_name = pokemon_name.lower().replace(" ", "-")
    pokemon_image_url = (
        f"https://img.pokemondb.net/sprites/scarlet-violet/normal/{pokemon_name}.png"
    )
    return pokemon_image_url


class UserModel(BaseModel):
    trainer_id: str


@app.post("/api/v1/save_new_trainer")
async def save_new_trainer(
    user: UserModel,
) -> str:
    """

    trainer_id について、以下の処理を行う。
    - trainer_id が存在しない場合は新規登録
    - trainer_id が存在する場合は何もしない
    """
    # check if trainer_id exists
    if sqlite_handler.check_trainer_id_exists(user.trainer_id):
        logger.info("trainer_id already exists")
        return "trainer_id already exists"
    else:
        logger.info("trainer_id does not exist")
        sqlite_handler.save_new_trainer(user.trainer_id)
        return f"save new user: {user.trainer_id}"
