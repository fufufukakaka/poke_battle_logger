import asyncio
import logging
import unicodedata
from logging import getLogger
from typing import Dict, List, Union

import pandas as pd
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rich.logging import RichHandler
from tqdm.auto import tqdm
import yt_dlp
from poke_battle_logger.api.poke_battle_extractor import PokeBattleExtractor

from poke_battle_logger.database.database_handler import SQLiteHandler

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


def get_trainer_id_in_DB(trainer_id: str) -> int:
    trainer_id_in_DB = sqlite_handler.get_trainer_id_in_DB(trainer_id)
    return trainer_id_in_DB


@app.get("/hello")
async def hello_revision() -> str:
    return "hello poke_battle_logger API"


@app.get("/api/v1/pokemon_name_to_no")
async def get_pokemon_name_to_no(pokemon_name: str) -> int:
    return pokemon_japanese_to_no_dict[pokemon_name]


@app.get("/api/v1/recent_battle_summary")
async def get_recent_battle_summary(
    trainer_id: str,
) -> Dict[str, Union[float, int, str, List[Dict[str, Union[str, int]]]]]:
    is_exist = sqlite_handler.check_trainer_id_exists(trainer_id)
    if not is_exist:
        return {
            "win_rate": 0.0,
            "latest_rank": 0,
            "latest_win_pokemon": [],
            "latest_lose_pokemon": [],
            "recent_battle_history": [],
        }

    win_rate = sqlite_handler.get_latest_season_win_rate(trainer_id)
    latest_rank = sqlite_handler.get_latest_season_rank(trainer_id)
    latest_win_pokemon = sqlite_handler.get_latest_win_pokemon(trainer_id)
    latest_lose_pokemon = sqlite_handler.get_latest_lose_pokemon(trainer_id)
    recent_battle_history = sqlite_handler.get_recent_battle_history(trainer_id)
    battle_counts = sqlite_handler.get_battle_counts(trainer_id)

    return {
        "win_rate": win_rate,
        "latest_rank": latest_rank,
        "latest_win_pokemon": latest_win_pokemon,
        "latest_lose_pokemon": latest_lose_pokemon,
        "recent_battle_history": recent_battle_history,
        "battle_counts": battle_counts,
    }


@app.get("/api/v1/analytics")
async def get_analytics(
    trainer_id: str,
    season: int,
) -> Dict[str, Union[List[float], List[int], List[Dict[str, Union[str, int, float]]]]]:
    if season == 0:
        win_rate_transition = sqlite_handler.get_win_rate_transitions_all(trainer_id)
        next_rank_transition = sqlite_handler.get_next_rank_transitions_all(trainer_id)
        your_pokemon_stats_summary = sqlite_handler.get_your_pokemon_stats_summary_all(
            trainer_id
        )
        opponent_pokemon_stats_summary = (
            sqlite_handler.get_opponent_pokemon_stats_summary_all(trainer_id)
        )
    elif season > 0:
        win_rate_transition = sqlite_handler.get_win_rate_transitions_season(
            season, trainer_id
        )
        next_rank_transition = sqlite_handler.get_next_rank_transitions_season(
            season, trainer_id
        )
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
    trainer_id: str,
    season: int,
) -> List[Dict[str, Union[str, int, float]]]:
    if season == 0:
        battle_log = sqlite_handler.get_battle_log_all(trainer_id)
    elif season > 0:
        battle_log = sqlite_handler.get_battle_log_season(trainer_id, season)
    else:
        raise ValueError("season must be 0 or positive")
    return battle_log


@app.get("/api/v1/in_battle_log")
async def get_in_battle_log(battle_id: str):
    return sqlite_handler.get_in_battle_log(battle_id)


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


class MemoModel(BaseModel):
    battle_id: str
    memo: str


@app.post("/api/v1/update_memo")
async def update_memo(request: MemoModel) -> str:
    sqlite_handler.update_memo(request.battle_id, request.memo)
    return "update memo"


@app.get("/api/v1/check_video_format")
async def check_video_format(
    video_id: str,
) -> Dict[str, bool]:
    """
    Youtube の動画 ID を受け取って、以下の項目をチェックする
    - 動画が存在するか
    - 1080p の動画か
    - 30fps の動画か
    """
    # 動画が存在するか
    URL = f'https://www.youtube.com/watch?v={video_id}'
    try:
        ydl_opts = {}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(URL, download=False)
            sanitize_info = ydl.sanitize_info(info)
            if sanitize_info is None:
                return {
                    "isValid": False,
                    "is1080p": False,
                    "is30fps": False,
                }
            else:
                # 1080p の動画か
                is_1080p = False
                _resolution = sanitize_info["resolution"]
                if _resolution == "1920x1080":
                    is_1080p = True

                # 30fps の動画か
                is_30fps = False
                _fps = sanitize_info["fps"]
                if _fps == "30":
                    is_30fps = True
                return {
                    "isValid": True,
                    "is1080p": is_1080p,
                    "is30fps": is_30fps,
                }
    except BaseException:
        return {
            "isValid": False,
            "is1080p": False,
            "is30fps": False,
        }


async def send_progress(websocket: WebSocket, total: int):
    status = {
        "message": ["INFO: start"],
        "progress": total,
    }
    with tqdm(total=total) as progress_bar:
        for i in range(total):
            await asyncio.sleep(0.1)  # 重い処理の代わりに0.1秒待機
            progress_bar.update(1)
            status["progress"] = progress_bar.n
            await websocket.send_json(status)

    await asyncio.sleep(2)
    status["message"].append("INFO: job1")
    await websocket.send_json(status)

    await asyncio.sleep(2)
    status["message"].append("INFO: job2")
    await websocket.send_json(status)

    await asyncio.sleep(2)
    status["message"].append("INFO: end")
    await websocket.send_json(status)


@app.websocket("/api/v1/dummy_job")
async def websocket_endpoint(job_progress_websocket: WebSocket, videoId: str, language: str, trainerId: str):
    trainer_id_in_DB = get_trainer_id_in_DB(trainerId)
    await job_progress_websocket.accept()
    total = 100  # 進行状況の合計値
    await send_progress(job_progress_websocket, total)
    await job_progress_websocket.close()


@app.websocket("/api/v1/extract_stats_from_video")
async def extract_stats_from_video(job_progress_websocket: WebSocket, videoId: str, language: str, trainerId: str):
    trainer_id_in_DB = get_trainer_id_in_DB(trainerId)
    poke_battle_extractor = PokeBattleExtractor(
        video_id=videoId,
        language=language,
        trainer_id=trainer_id_in_DB,
    )

    await job_progress_websocket.accept()
    await poke_battle_extractor.run(job_progress_websocket)
    await job_progress_websocket.close()
