import asyncio
import json
import logging
import unicodedata
from logging import getLogger
from typing import Dict, List, Union

import cv2
import numpy as np
import pandas as pd
import yt_dlp
from fastapi import (
    FastAPI,
    File,
    HTTPException,
    Request,
    UploadFile,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from rich.logging import RichHandler

from poke_battle_logger.batch.pokemon_extractor import PokemonExtractor
from poke_battle_logger.cloud_batch_handler import CloudBatchHandler
from poke_battle_logger.database.database_handler import DatabaseHandler
from poke_battle_logger.firestore_handler import FirestoreHandler
from poke_battle_logger.gcs_handler import GCSHandler
from poke_battle_logger.stream.live_battle_analyzer import LiveBattleAnalyzer
from poke_battle_logger.types import ImageLabel, NameWindowImageLabel

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler()],
)
logger = getLogger(__name__)

app = FastAPI()
origins = [
    "http://127.0.0.1:3000",
    "http://localhost:3000",
    "https://poke-battle-logger.vercel.app",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


pokemon_name_df = pd.read_csv("data/pokemon_names.csv")
pokemon_japanese_to_no_dict: Dict[str, int] = dict(
    zip(pokemon_name_df["Japanese"], pokemon_name_df["No."])
)
pokemon_japanese_to_english_dict: Dict[str, str] = dict(
    zip(pokemon_name_df["Japanese"], pokemon_name_df["English"])
)
pokemon_extractor = PokemonExtractor()


def get_trainer_id_in_DB(trainer_id: str) -> int:
    database_handler: DatabaseHandler = DatabaseHandler()
    trainer_id_in_DB = database_handler.get_trainer_id_in_DB(trainer_id)
    return trainer_id_in_DB


@app.exception_handler(RequestValidationError)
async def handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    print(exc)
    return JSONResponse(content={}, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


@app.get("/hello")
async def hello_revision() -> str:
    return "hello poke_battle_logger API"


@app.get("/api/v1/get_trainer_id_in_DB")
async def get_trainer_id_in_DB_api(trainer_id: str) -> int:
    return get_trainer_id_in_DB(trainer_id)


@app.get("/api/v1/pokemon_name_to_no")
async def get_pokemon_name_to_no(pokemon_name: str) -> int:
    return pokemon_japanese_to_no_dict[pokemon_name]


@app.get("/api/v1/recent_battle_summary")
async def get_recent_battle_summary(
    trainer_id: str,
) -> Dict[str, Union[float, int, str, List[Dict[str, Union[str, int]]]]]:
    database_handler: DatabaseHandler = DatabaseHandler()
    is_exist = database_handler.check_trainer_id_exists(trainer_id)
    if not is_exist:
        return {
            "win_rate": 0.0,
            "latest_rank": 0,
            "latest_win_pokemon": [],
            "latest_lose_pokemon": [],
            "recent_battle_history": [],
        }

    win_rate = database_handler.get_latest_season_win_rate(trainer_id)
    latest_rank = database_handler.get_latest_season_rank(trainer_id)
    latest_win_pokemon = database_handler.get_latest_win_pokemon(trainer_id)
    latest_lose_pokemon = database_handler.get_latest_lose_pokemon(trainer_id)
    recent_battle_history = database_handler.get_recent_battle_history(trainer_id)
    battle_counts = database_handler.get_battle_counts(trainer_id)

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
) -> Dict[
    str,
    Union[
        List[float],
        List[int],
        List[Dict[str, Union[str, int, float]]],
        List[Dict[str, Union[str, int]]],
    ],
]:
    database_handler: DatabaseHandler = DatabaseHandler()
    if season == 0:
        win_rate_transition = database_handler.get_win_rate_transitions_all(trainer_id)
        next_rank_transition = database_handler.get_next_rank_transitions_all(
            trainer_id
        )
        your_pokemon_stats_summary = (
            database_handler.get_your_pokemon_stats_summary_all(trainer_id)
        )
        opponent_pokemon_stats_summary = (
            database_handler.get_opponent_pokemon_stats_summary_all(trainer_id)
        )
        your_pokemon_defeat_summary = database_handler.get_your_pokemon_defeat_summary(
            trainer_id
        )
        opponent_pokemon_defeat_summary = (
            database_handler.get_opponent_pokemon_defeat_summary(trainer_id)
        )
    elif season > 0:
        win_rate_transition = database_handler.get_win_rate_transitions_season(
            season, trainer_id
        )
        next_rank_transition = database_handler.get_next_rank_transitions_season(
            season, trainer_id
        )
        your_pokemon_stats_summary = (
            database_handler.get_your_pokemon_stats_summary_season(season, trainer_id)
        )
        opponent_pokemon_stats_summary = (
            database_handler.get_opponent_pokemon_stats_summary_season(
                season, trainer_id
            )
        )
        your_pokemon_defeat_summary = (
            database_handler.get_your_pokemon_defeat_summary_in_season(
                season, trainer_id
            )
        )
        opponent_pokemon_defeat_summary = (
            database_handler.get_opponent_pokemon_defeat_summary_in_season(
                season, trainer_id
            )
        )
    else:
        raise ValueError("season must be 0 or positive")
    return {
        "winRate": win_rate_transition,
        "nextRank": next_rank_transition,
        "yourPokemonStatsSummary": your_pokemon_stats_summary,
        "opponentPokemonStatsSummary": opponent_pokemon_stats_summary,
        "yourPokemonKnockOutSummary": your_pokemon_defeat_summary,
        "opponentPokemonKnockOutSummary": opponent_pokemon_defeat_summary,
    }


@app.get("/api/v1/battle_log")
async def get_battle_log(
    trainer_id: str,
    season: int,
    page: int,
    size: int,
) -> List[Dict[str, Union[str, int]]]:
    database_handler: DatabaseHandler = DatabaseHandler()
    if season == 0:
        battle_log = database_handler.get_battle_log_all(trainer_id, page, size)
    elif season > 0:
        battle_log = database_handler.get_battle_log_season(
            trainer_id, season, page, size
        )
    else:
        raise ValueError("season must be 0 or positive")
    return battle_log


@app.get("/api/v1/battle_log_count")
async def get_battle_log_count(
    trainer_id: str,
    season: int,
) -> int:
    database_handler: DatabaseHandler = DatabaseHandler()
    if season == 0:
        battle_log_count = database_handler.get_battle_log_all_count(trainer_id)
    elif season > 0:
        battle_log_count = database_handler.get_battle_log_season_count(
            trainer_id, season
        )
    else:
        raise ValueError("season must be 0 or positive")
    return battle_log_count


@app.get("/api/v1/in_battle_log")
async def get_in_battle_log(battle_id: str) -> list[dict[str, str | int]]:
    database_handler: DatabaseHandler = DatabaseHandler()
    return database_handler.get_in_battle_log(battle_id)


@app.get("/api/v1/in_battle_message_log")
async def get_in_battle_message_log(battle_id: str) -> list[dict[str, str | int]]:
    database_handler: DatabaseHandler = DatabaseHandler()
    in_battle_message_log = database_handler.get_in_battle_message_log(battle_id)
    return in_battle_message_log


class BattleLogEntry(BaseModel):
    turn: int
    frame_number: int
    message: str
    your_pokemon_name: Union[str, None]
    opponent_pokemon_name: Union[str, None]


class BattleMessageFullLogResponse(BaseModel):
    battle_id: str
    win_or_lose: str
    next_rank: int
    your_team: str
    opponent_team: str
    your_pokemon_1: str
    your_pokemon_2: str
    your_pokemon_3: str
    opponent_pokemon_1: str
    opponent_pokemon_2: str
    opponent_pokemon_3: str
    battle_log: List[BattleLogEntry]


@app.get(
    "/api/v1/in_battle_message_full_log", response_model=BattleMessageFullLogResponse
)
async def get_in_battle_message_full_log(
    battle_id: str,
) -> BattleMessageFullLogResponse:
    database_handler: DatabaseHandler = DatabaseHandler()
    in_battle_message_full_log = database_handler.get_in_battle_message_full_log(
        battle_id
    )
    battle_summary = database_handler.get_battle_summary(battle_id)

    # Convert battle log entries to Pydantic models
    battle_log_entries = [
        BattleLogEntry(**entry) for entry in in_battle_message_full_log
    ]

    # Create response model
    return BattleMessageFullLogResponse(
        battle_id=str(battle_summary["battle_id"]),
        win_or_lose=str(battle_summary["win_or_lose"]),
        next_rank=int(battle_summary["next_rank"]),
        your_team=str(battle_summary["your_team"]),
        opponent_team=str(battle_summary["opponent_team"]),
        your_pokemon_1=str(battle_summary["your_pokemon_1"]),
        your_pokemon_2=str(battle_summary["your_pokemon_2"]),
        your_pokemon_3=str(battle_summary["your_pokemon_3"]),
        opponent_pokemon_1=str(battle_summary["opponent_pokemon_1"]),
        opponent_pokemon_2=str(battle_summary["opponent_pokemon_2"]),
        opponent_pokemon_3=str(battle_summary["opponent_pokemon_3"]),
        battle_log=battle_log_entries,
    )


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
    trainer_email: str


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
    database_handler: DatabaseHandler = DatabaseHandler()
    if database_handler.check_trainer_id_exists(user.trainer_id):
        logger.info("trainer_id already exists")
        return "trainer_id already exists"
    else:
        logger.info("trainer_id does not exist")
        database_handler.save_new_trainer(user.trainer_id, user.trainer_email)
        return f"save new user: {user.trainer_id}"


class MemoModel(BaseModel):
    battle_id: str
    memo: str


@app.post("/api/v1/update_memo")
async def update_memo(request: MemoModel) -> str:
    database_handler: DatabaseHandler = DatabaseHandler()
    database_handler.update_memo(request.battle_id, request.memo)
    return "update memo"


@app.get("/api/v1/check_video_format")
async def check_video_format(
    videoId: str,
) -> Dict[str, bool]:
    """
    Youtube の動画 ID を受け取って、以下の項目をチェックする
    - 動画が存在するか
    - 1080p の動画か
    - 30fps の動画か
    """
    # 動画が存在するか
    URL = f"https://www.youtube.com/watch?v={videoId}"
    try:
        with yt_dlp.YoutubeDL({}) as ydl:
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


class SetLabelRequest(BaseModel):
    trainer_id: int
    image_labels: List[ImageLabel]


@app.post("/api/v1/set_label_to_unknown_pokemon_images")
async def set_label_to_unknown_pokemon_images(
    request: SetLabelRequest,
    # trainer_id: int,
    # image_labels: List[ImageLabel],
) -> Dict[str, str]:
    """
    trainer_id は DB 上での ID に変換済のものが入力される
    """
    gcs_handler = GCSHandler()
    try:
        gcs_handler.set_label_unknown_pokemon_images(
            request.trainer_id, request.image_labels
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"message": "Unknown pokemon image labels are set successfully"}


class SetNameWindowLabelRequest(BaseModel):
    trainer_id: int
    image_labels: List[NameWindowImageLabel]


@app.post("/api/v1/set_label_to_unknown_pokemon_name_window_images")
async def set_label_to_unknown_pokemon_name_window_images(
    request: SetNameWindowLabelRequest,
) -> Dict[str, str]:
    """
    trainer_id は DB 上での ID に変換済のものが入力される
    """
    gcs_handler = GCSHandler()
    try:
        gcs_handler.set_label_unknown_pokemon_name_window_images(
            request.trainer_id, request.image_labels
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"message": "Unknown pokemon name window image labels are set successfully"}


@app.get("/api/v1/fainted_pokemon_log")
async def get_fainted_pokemon_log(battle_id: str) -> List[Dict[str, Union[str, int]]]:
    database_handler: DatabaseHandler = DatabaseHandler()
    return database_handler.get_fainted_pokemon_log(battle_id)


@app.get("/api/v1/get_battle_video_status_list")
async def get_battle_video_status_list(
    trainer_id: str,
) -> list[dict[str, str]]:
    database_handler: DatabaseHandler = DatabaseHandler()
    return database_handler.get_battle_video_status_list(trainer_id)


@app.get("/api/v1/get_battle_video_detail_status_log")
async def get_battle_video_detail_status_log(
    video_id: str,
) -> list[str]:
    firestore_handler: FirestoreHandler = FirestoreHandler()
    return firestore_handler.get_battle_video_detail_status_log(video_id)


@app.get("/api/v1/extract_stats_from_video")
async def get_stats_from_video_via_cloud_batch(
    videoId: str, language: str, trainerId: str, finalResult: int | None = None
) -> str:
    """
    finalResult が指定されている場合、動画の最後に順位が表示されていないことを想定する(最終日など)
    """
    cloud_batch_handler = CloudBatchHandler()
    cloud_batch_handler.run_extract_stats_from_video_batch(
        video_id=videoId,
        trainer_id=trainerId,
        language=language,
        finalResult=finalResult,
    )
    return "Start extracting stats from video via cloud batch"


@app.get("/api/v1/get_seasons")
async def get_seasons() -> list[dict[str, int | str]]:
    database_handler: DatabaseHandler = DatabaseHandler()
    return database_handler.get_seasons()


@app.post("/api/v1/extract_pokemon_name_from_image")
async def extract_pokemon_name_from_image(
    file: UploadFile = File(...),
) -> Dict[str, List[str]]:
    # ファイルの内容を読み取り
    content = await file.read()
    # bytes から opencv を通じて numpy array に変換
    nparr = np.frombuffer(content, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    (
        _,
        opponent_pokemon_names,
        _,
    ) = pokemon_extractor.extract_pre_battle_pokemons(img, is_both_team=False)

    return {"opponent_pokemon_names": opponent_pokemon_names}


@app.get("/api/v1/search_battles")
async def search_battles(
    trainer_id: str,
    season: int,
    my_pokemons: str,
    opponent_pokemons: str,
) -> List[Dict[str, Union[str, int]]]:
    my_pokemons_list = my_pokemons.split(",")
    opponent_pokemons_list = opponent_pokemons.split(",")

    database_handler: DatabaseHandler = DatabaseHandler()
    res = database_handler.search_battles(
        trainer_id, season, my_pokemons_list, opponent_pokemons_list
    )
    return res


# Live Stream Analysis endpoints
live_analyzers: Dict[str, LiveBattleAnalyzer] = {}


class LiveAnalysisStartRequest(BaseModel):
    trainer_id: str
    capture_source: str = "obs"
    language: str = "en"
    capture_config: Dict[str, Union[str, int]] = {}


class LiveAnalysisStatusResponse(BaseModel):
    is_running: bool
    stats: Dict[str, Union[str, int, float]]
    available_sources: List[str]


@app.post("/api/v1/live_analysis/start")
async def start_live_analysis(request: LiveAnalysisStartRequest) -> Dict[str, str]:
    if request.trainer_id in live_analyzers:
        existing_analyzer = live_analyzers[request.trainer_id]
        if existing_analyzer.is_running:
            return {
                "status": "error",
                "message": "Live analysis already running for this trainer",
            }
        else:
            del live_analyzers[request.trainer_id]

    try:
        analyzer = LiveBattleAnalyzer(
            trainer_id=request.trainer_id,
            language=request.language,
            capture_source=request.capture_source,
            capture_config=request.capture_config,
            db_handler=DatabaseHandler(),
        )

        live_analyzers[request.trainer_id] = analyzer

        # Start analysis in background
        import asyncio

        asyncio.create_task(analyzer.start_analysis())

        return {"status": "success", "message": "Live analysis started"}

    except Exception as e:
        logger.error(f"Error starting live analysis: {e}")
        return {"status": "error", "message": str(e)}


@app.post("/api/v1/live_analysis/stop")
async def stop_live_analysis(trainer_id: str) -> Dict[str, str]:
    if trainer_id not in live_analyzers:
        return {
            "status": "error",
            "message": "No live analysis running for this trainer",
        }

    try:
        analyzer = live_analyzers[trainer_id]
        await analyzer.stop_analysis()
        del live_analyzers[trainer_id]

        return {"status": "success", "message": "Live analysis stopped"}

    except Exception as e:
        logger.error(f"Error stopping live analysis: {e}")
        return {"status": "error", "message": str(e)}


@app.get("/api/v1/live_analysis/status")
async def get_live_analysis_status(trainer_id: str) -> LiveAnalysisStatusResponse:
    if trainer_id not in live_analyzers:
        # Return available sources even when not running
        dummy_analyzer = LiveBattleAnalyzer(trainer_id, "en", "obs")
        return LiveAnalysisStatusResponse(
            is_running=False,
            stats={},
            available_sources=dummy_analyzer.get_available_capture_sources(),
        )

    analyzer = live_analyzers[trainer_id]
    return LiveAnalysisStatusResponse(
        is_running=analyzer.is_running,
        stats=analyzer.get_stats(),
        available_sources=analyzer.get_available_capture_sources(),
    )


@app.get("/api/v1/live_analysis/sources")
async def get_available_capture_sources() -> Dict[str, List[str]]:
    dummy_analyzer = LiveBattleAnalyzer("dummy", "en", "obs")
    return {"available_sources": dummy_analyzer.get_available_capture_sources()}


@app.post("/api/v1/live_analysis/test_source")
async def test_capture_source(
    source_type: str, config: Dict[str, Union[str, int]] = {}
) -> Dict[str, Union[str, bool]]:
    try:
        dummy_analyzer = LiveBattleAnalyzer("dummy", "en", "obs")
        result = await dummy_analyzer.test_capture_source(source_type, config)

        return {"status": "success" if result else "failed", "available": result}

    except Exception as e:
        logger.error(f"Error testing capture source: {e}")
        return {"status": "error", "available": False, "message": str(e)}


# WebSocket connection management
class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, trainer_id: str):
        await websocket.accept()
        if trainer_id not in self.active_connections:
            self.active_connections[trainer_id] = []
        self.active_connections[trainer_id].append(websocket)
        logger.info(f"WebSocket connected for trainer {trainer_id}")

    def disconnect(self, websocket: WebSocket, trainer_id: str):
        if trainer_id in self.active_connections:
            if websocket in self.active_connections[trainer_id]:
                self.active_connections[trainer_id].remove(websocket)
            if not self.active_connections[trainer_id]:
                del self.active_connections[trainer_id]
        logger.info(f"WebSocket disconnected for trainer {trainer_id}")

    async def send_to_trainer(self, trainer_id: str, message: dict):
        if trainer_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[trainer_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except:
                    disconnected.append(connection)

            # Remove disconnected connections
            for conn in disconnected:
                self.disconnect(conn, trainer_id)


websocket_manager = WebSocketManager()


@app.websocket("/ws/live_analysis/{trainer_id}")
async def websocket_endpoint(websocket: WebSocket, trainer_id: str):
    await websocket_manager.connect(websocket, trainer_id)

    # Add event handler to the analyzer if it exists
    if trainer_id in live_analyzers:
        analyzer = live_analyzers[trainer_id]

        async def websocket_event_handler(event):
            await websocket_manager.send_to_trainer(
                trainer_id,
                {
                    "type": "battle_event",
                    "event_type": event.event_type,
                    "data": event.data,
                    "timestamp": event.timestamp.isoformat(),
                    "confidence": event.confidence,
                },
            )

        analyzer.add_event_callback(websocket_event_handler)

    try:
        # Send initial status
        if trainer_id in live_analyzers:
            analyzer = live_analyzers[trainer_id]
            await websocket.send_text(
                json.dumps(
                    {
                        "type": "status",
                        "is_running": analyzer.is_running,
                        "stats": analyzer.get_stats(),
                    }
                )
            )

        # Keep connection alive and handle incoming messages
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)

                if message.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
                elif message.get("type") == "get_status":
                    if trainer_id in live_analyzers:
                        analyzer = live_analyzers[trainer_id]
                        await websocket.send_text(
                            json.dumps(
                                {
                                    "type": "status",
                                    "is_running": analyzer.is_running,
                                    "stats": analyzer.get_stats(),
                                }
                            )
                        )

            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                break

    except WebSocketDisconnect:
        pass
    finally:
        websocket_manager.disconnect(websocket, trainer_id)
