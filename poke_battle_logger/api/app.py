import logging
from logging import getLogger
from typing import Dict, List, Union

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


@app.get("/hello")
async def hello_revision() -> str:
    return "hello poke_battle_logger API"


@app.get("/api/v1/recent_battle_summary")
async def get_recent_battle_summary() -> Dict[str, Union[float, int, str]]:
    win_rate = sqlite_handler.get_latest_season_win_rate()
    latest_rank = sqlite_handler.get_latest_season_rank()
    latest_win_pokemon = sqlite_handler.get_latest_win_pokemon()
    latest_lose_pokemon = sqlite_handler.get_latest_lose_pokemon()
    return {
        "win_rate": win_rate,
        "latest_rank": latest_rank,
        "latest_win_pokemon": latest_win_pokemon,
        "latest_lose_pokemon": latest_lose_pokemon,
    }
