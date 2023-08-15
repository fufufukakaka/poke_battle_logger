import logging
import os
from logging import getLogger
from typing import Tuple

import click
import resend
from rich.logging import RichHandler

from poke_battle_logger.database.database_handler import DatabaseHandler
from poke_battle_logger.gcs_handler import GCSHandler
from poke_battle_logger.job_api.pokemon_battle_extractor import PokemonBattleExtractor

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


def get_trainer_id_in_DB_and_email(trainer_id: str) -> Tuple[int, str]:
    database_handler: DatabaseHandler = DatabaseHandler()
    trainer_id_in_DB = database_handler.get_trainer_id_in_DB(trainer_id)
    email = database_handler.get_user_email(trainer_id)
    return trainer_id_in_DB, email


@click.command()
@click.option("--trainer_id", required=True)
@click.option("--video_id", required=True)
@click.option("--language", required=True)
async def run_extractor(trainer_id: str, video_id: str, language: str):
    trainer_id_in_DB, email = get_trainer_id_in_DB_and_email(trainer_id)

    gcs_handler = GCSHandler()
    gcs_handler.download_pokemon_templates(trainer_id_in_DB)
    gcs_handler.download_pokemon_name_window_templates(trainer_id_in_DB)
    poke_battle_extractor = PokemonBattleExtractor(
        video_id=video_id,
        language=language,
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
                video_id=video_id,
                number_of_logs=number_of_log,
                number_of_win=number_of_win,
                number_of_lose=number_of_lose,
            ),
        }
        resend.Emails.send(params)
    except Exception:
        poke_battle_extractor.database_handler.update_video_process_status(
            trainer_id_in_DB=trainer_id_in_DB,
            video_id=video_id,
            status="Process failed",
        )
        params = {
            "from": "PokeBattleLogger <notify@poke-battle-logger-api.com>",
            "to": email,
            "subject": "PokeBattleLogger: Failed to extract stats from video",
            "html": fail_mail_templates.format(video_id=video_id),
        }
        resend.Emails.send(params)


if __name__ == "__main__":
    run_extractor()  # type: ignore
