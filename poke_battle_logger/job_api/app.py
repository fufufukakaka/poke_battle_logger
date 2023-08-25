import logging
import os
from logging import getLogger
from typing import Tuple

import pydantic
import resend
from fastapi import BackgroundTasks, FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from rich.logging import RichHandler

from poke_battle_logger.batch.pokemon_battle_extractor import PokemonBattleExtractor
from poke_battle_logger.database.database_handler import DatabaseHandler
from poke_battle_logger.gcs_handler import GCSHandler

resend.api_key = os.environ["RESEND_API_KEY"]
success_mail_templates = open(
    "poke_battle_logger/email_templates/extract_success.html"
).read()
fail_mail_templates = open(
    "poke_battle_logger/email_templates/extract_fail.html"
).read()

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


def get_trainer_id_in_DB_and_email(trainer_id: str) -> Tuple[int, str]:
    database_handler: DatabaseHandler = DatabaseHandler()
    trainer_id_in_DB = database_handler.get_trainer_id_in_DB(trainer_id)
    email = database_handler.get_user_email(trainer_id)
    return trainer_id_in_DB, email


class ExtractStatsFromVideoRequest(pydantic.BaseModel):
    trainerId: str
    videoId: str
    language: str


@app.post("/api/v1/extract_stats_from_video")
async def extract_stats_from_video(  # type: ignore
    request: ExtractStatsFromVideoRequest, background_tasks: BackgroundTasks
) -> str:
    trainer_id_in_DB, email = get_trainer_id_in_DB_and_email(request.trainerId)
    background_tasks.add_task(
        extract_stats, request=request, trainer_id_in_DB=trainer_id_in_DB, email=email
    )
    return "Request accepted"


async def extract_stats(
    request: ExtractStatsFromVideoRequest, trainer_id_in_DB: int, email: str
) -> None:
    gcs_handler = GCSHandler()
    gcs_handler.download_pokemon_templates(trainer_id_in_DB)
    gcs_handler.download_pokemon_name_window_templates(trainer_id_in_DB)
    poke_battle_extractor = PokemonBattleExtractor(
        video_id=request.videoId,
        language=request.language,
        trainer_id_in_DB=trainer_id_in_DB,
        email=email,
    )

    try:
        number_of_log, number_of_win, number_of_lose = await poke_battle_extractor.run()
        params = {
            "from": "PokeBattleLogger <notify@poke-battle-logger-api.com>",
            "to": email,
            "subject": "PokeBattleLogger: You're now ready to see your pokemon battle log!",
            "html": success_mail_templates.format(
                video_id=request.videoId,
                number_of_logs=number_of_log,
                number_of_win=number_of_win,
                number_of_lose=number_of_lose,
            ),
        }
        resend.Emails.send(params)
    except Exception:
        poke_battle_extractor.database_handler.update_video_process_status(
            trainer_id_in_DB=trainer_id_in_DB,
            video_id=request.videoId,
            status="Process failed",
        )
        params = {
            "from": "PokeBattleLogger <notify@poke-battle-logger-api.com>",
            "to": email,
            "subject": "PokeBattleLogger: Failed to extract stats from video",
            "html": fail_mail_templates.format(video_id=request.videoId),
        }
        resend.Emails.send(params)
