import logging
from logging import getLogger

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from rich.logging import RichHandler

from poke_battle_logger.database.database_handler import DatabaseHandler
from poke_battle_logger.gcs_handler import GCSHandler
from poke_battle_logger.job_api.pokemon_battle_extractor import PokemonBattleExtractor

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


@app.exception_handler(RequestValidationError)
async def handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    print(exc)
    return JSONResponse(content={}, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


@app.get("/hello")
async def hello_revision() -> str:
    return "hello poke_battle_logger Job API"


def get_trainer_id_in_DB(trainer_id: str) -> int:
    database_handler: DatabaseHandler = DatabaseHandler()
    trainer_id_in_DB = database_handler.get_trainer_id_in_DB(trainer_id)
    return trainer_id_in_DB


@app.post("/api/v1/extract_stats_from_video")
async def extract_stats_from_video(  # type: ignore
    videoId: str, language: str, trainerId: str
):
    gcs_handler = GCSHandler()
    trainer_id_in_DB = get_trainer_id_in_DB(trainerId)
    gcs_handler.download_pokemon_templates(trainer_id_in_DB)
    gcs_handler.download_pokemon_name_window_templates(trainer_id_in_DB)
    poke_battle_extractor = PokemonBattleExtractor(
        video_id=videoId,
        language=language,
        trainer_id_in_DB=trainer_id_in_DB,
    )

    poke_battle_extractor.run()
