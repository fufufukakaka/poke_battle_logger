import logging
from logging import getLogger
from typing import Dict, List, Union

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

origins = [""]

app = FastAPI()
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


@app.get("/hello")
async def hello_revision() -> str:
    return "hello poke_battle_logger API"


@app.get("/api/v1/pokemon_name_to_no")
async def get_pokemon_name_to_no(pokemon_name: str) -> int:
    return pokemon_japanese_to_no_dict[pokemon_name]


@app.get("/api/v1/recent_battle_summary")
async def get_recent_battle_summary() -> Dict[
    str, Union[float, int, str, List[Dict[str, Union[str, int]]]]
]:
    win_rate = sqlite_handler.get_latest_season_win_rate()
    latest_rank = sqlite_handler.get_latest_season_rank()
    latest_win_pokemon = sqlite_handler.get_latest_win_pokemon()
    latest_lose_pokemon = sqlite_handler.get_latest_lose_pokemon()
    recent_battle_history = sqlite_handler.get_recent_battle_history()

    # get image url
    latest_win_pokemon_image = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{pokemon_japanese_to_no_dict[latest_win_pokemon]}.png"
    latest_lose_pokemon_image = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{pokemon_japanese_to_no_dict[latest_lose_pokemon]}.png"

    return {
        "win_rate": win_rate,
        "latest_rank": latest_rank,
        "latest_win_pokemon": latest_win_pokemon,
        "latest_win_pokemon_image": latest_win_pokemon_image,
        "latest_lose_pokemon_image": latest_lose_pokemon_image,
        "latest_lose_pokemon": latest_lose_pokemon,
        "recent_battle_history": recent_battle_history,
    }


@app.get("/api/v1/win_rate_transition")
async def get_win_rate_transition(season: int) -> List[float]:
    """
    season 0 のときは全期間を返す
    """
    win_rate_transition = sqlite_handler.get_win_rate_transitions_season(season)
    return win_rate_transition


@app.get("/api/v1/next_rank_transition")
async def get_next_rank_transition(season: int) -> List[int]:
    """
    season 0 のときは全期間を返す
    """
    next_rank_transition = sqlite_handler.get_next_rank_transitions_season(season)
    return next_rank_transition


@app.get("/api/v1/your_pokemon_stats_summary")
async def get_your_pokemon_stats_summary(
    season: int,
) -> List[Dict[str, Union[str, int, float]]]:
    """
    season 0 のときは全期間を返す
    """
    if season == 0:
        your_pokemon_stats_summary = sqlite_handler.get_your_pokemon_stats_summary_all()
    elif season > 0:
        your_pokemon_stats_summary = (
            sqlite_handler.get_your_pokemon_stats_summary_season(season)
        )
    else:
        raise ValueError("season must be 0 or positive")
    return your_pokemon_stats_summary
