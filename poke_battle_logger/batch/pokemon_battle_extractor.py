import logging
import os
from collections import Counter
from logging import getLogger
from typing import List, Tuple

import cv2
import resend
import yt_dlp
from rich.logging import RichHandler

from poke_battle_logger.batch.data_builder import DataBuilder
from poke_battle_logger.batch.extractor import Extractor
from poke_battle_logger.batch.frame_compressor import (
    frame_compress,
    message_frame_compress,
)
from poke_battle_logger.batch.frame_detector import FrameDetector
from poke_battle_logger.batch.pokemon_extractor import PokemonExtractor
from poke_battle_logger.database.database_handler import DatabaseHandler
from poke_battle_logger.firestore_handler import FirestoreHandler
from poke_battle_logger.gcs_handler import GCSHandler

resend.api_key = os.environ["RESEND_API_KEY"]
fail_unknown_pokemons_templates = open(
    "poke_battle_logger/email_templates/extract_fail_unknown_pokemons.html"
).read()


logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler()],
)
logger = getLogger(__name__)


class PokemonBattleExtractor:
    """
    API でポケモンの対戦動画から情報を抽出するクラス
    """

    def __init__(
        self, video_id: str, language: str, trainer_id_in_DB: int, email: str
    ) -> None:
        self.video_id = video_id
        self.language = language
        self.trainer_id_in_DB = trainer_id_in_DB
        self.email = email
        self.gcs_handler = GCSHandler()
        self.firestore_handler = FirestoreHandler()
        self.database_handler = DatabaseHandler()

    def _download_video(
        self,
    ) -> None:
        # GCS の poke_battle_logger_templates/user_battle_video/trainer_id_in_DB/{video_id}.mp4 があるか確認
        is_video_exists_in_GCS = self.gcs_handler.check_user_battle_video_exists(
            trainer_id_in_DB=self.trainer_id_in_DB, video_id=self.video_id
        )
        if is_video_exists_in_GCS:
            # GCS から video/{video_id}.mp4 にダウンロードする
            self.gcs_handler.download_video_from_gcs(
                trainer_id_in_DB=self.trainer_id_in_DB,
                video_id=self.video_id,
                local_path=f"video/{self.video_id}.mp4",
            )
            return
        # あれば、それを video/{video_id}.mp4 にダウンロードする
        # なければ、youtube からダウンロードする

        # download youtube video use yt-dlp
        # setting: 1080p, 30fps, mp4, video only(音声なし)
        # output: video/{video_id}.mp4
        yt_dlp_opts = {
            "format": "bestvideo[height<=1080][fps<=30][ext=mp4]",
            "outtmpl": f"video/{self.video_id}.mp4",
            "quiet": True,
        }

        with yt_dlp.YoutubeDL(yt_dlp_opts) as ydl:
            ydl.download([f"https://www.youtube.com/watch?v={self.video_id}"])

        # upload video to GCS
        self.gcs_handler.upload_video_to_gcs(
            trainer_id_in_DB=self.trainer_id_in_DB,
            video_id=self.video_id,
            local_path=f"video/{self.video_id}.mp4",
        )

        self.database_handler.update_video_process_status(
            trainer_id_in_DB=self.trainer_id_in_DB,
            video_id=self.video_id,
            status="Video downloaded.",
        )

    def run(self) -> Tuple[int, int, int]:
        self.database_handler.update_video_process_status(
            trainer_id_in_DB=self.trainer_id_in_DB,
            video_id=self.video_id,
            status="Downloading Video...",
        )
        logger.info(f"Downloading Video... {self.video_id}")

        self._download_video()

        self.database_handler.update_video_process_status(
            trainer_id_in_DB=self.trainer_id_in_DB,
            video_id=self.video_id,
            status="Processing...",
        )
        self.firestore_handler.update_log_document(
            video_id=self.video_id, new_message="INFO: Read Video..."
        )

        frame_detector = FrameDetector(self.language)
        extractor = Extractor(self.language)
        pokemon_extractor = PokemonExtractor()

        first_ranking_frames = []
        select_done_frames = []
        standing_by_frames = []
        level_50_frames = []
        ranking_frames = []
        win_or_lost_frames = []
        message_window_frames = []

        self.firestore_handler.update_log_document(
            video_id=self.video_id, new_message="INFO: Detecting frames..."
        )
        logger.info(f"Detecting frames... {self.video_id}")

        video = cv2.VideoCapture(f"video/{self.video_id}.mp4")
        total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        for i in range(total_frames):
            ret, frame = video.read()
            if ret:
                # message window
                if frame_detector.is_message_window_frame(frame):
                    message_window_frames.append(i)
                    continue

                # level_50
                if frame_detector.is_level_50_frame(frame):
                    level_50_frames.append(i)
                    continue

                # first ranking
                if frame_detector.is_first_ranking_frame(frame):
                    first_ranking_frames.append(i)
                    continue

                # select done
                if frame_detector.is_select_done_frame(frame):
                    select_done_frames.append(i)
                    continue

                # standing_by
                if frame_detector.is_standing_by_frame(frame):
                    standing_by_frames.append(i)
                    continue

                # ranking
                if frame_detector.is_ranking_frame(frame):
                    ranking_frames.append(i)
                    continue

                # win_or_lost
                if frame_detector.is_win_or_lost_frame(frame):
                    win_or_lost_frames.append(i)
                    continue
            else:
                continue
        video.release()

        # compress
        self.firestore_handler.update_log_document(
            video_id=self.video_id, new_message="INFO: Compressing frame array..."
        )
        logger.info(f"Compressing frame array... {self.video_id}")

        compressed_first_ranking_frames = frame_compress(first_ranking_frames)
        compressed_select_done_frames = frame_compress(select_done_frames)
        compressed_standing_by_frames = frame_compress(
            standing_by_frames, ignore_short_frames=True
        )
        compressed_level_50_frames = frame_compress(level_50_frames)
        compressed_ranking_frames = frame_compress(ranking_frames)
        compressed_win_or_lost_frames = frame_compress(win_or_lost_frames)
        compressed_message_window_frames = message_frame_compress(
            message_window_frames, frame_threshold=3
        )

        video = cv2.VideoCapture(f"video/{self.video_id}.mp4")
        total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

        rank_numbers = {}
        pokemon_select_order = {}
        pre_battle_pokemons: dict[int, dict[str, list[str]]] = {}
        is_exist_unknown_pokemon_list1 = []
        battle_pokemons: list[dict[str, str | int]] = []
        is_exist_unknown_pokemon_list2 = []

        first_ranking_frame_number = compressed_first_ranking_frames[0][-5]
        ranking_frame_numbers = [v[-5] for v in compressed_ranking_frames]
        select_done_frames = [
            v[-5] if len(v) > 5 else v[-1] for v in compressed_select_done_frames
        ]
        level_50_frames = [v[-1] for v in compressed_level_50_frames]

        standing_by_frames = []
        for i in range(len(compressed_standing_by_frames)):
            _standing_by_frames = compressed_standing_by_frames[i]
            if len(_standing_by_frames) == 1:
                continue
            standing_by_frames.append(_standing_by_frames[-1])

        win_or_lost = {}
        pre_win_or_lost = {}
        win_or_lost_all_frames: list[int] = sum(compressed_win_or_lost_frames, [])
        messages = {}
        message_window_frames = [v[-1] for v in compressed_message_window_frames]
        video = cv2.VideoCapture(f"video/{self.video_id}.mp4")
        for i in range(total_frames):
            ret, frame = video.read()
            # 開始時のランクを検出(OCR)
            if i == first_ranking_frame_number:
                logger.info(f"Extracting first ranking... {self.video_id}")
                _first_ranking_frame = frame
                rank_numbers[
                    first_ranking_frame_number
                ] = extractor.extract_first_rank_number(_first_ranking_frame)

            # ランクを検出(OCR)
            if i in ranking_frame_numbers:
                _ranking_frame = frame
                rank_numbers[i] = extractor.extract_rank_number(_ranking_frame)

            # 選出順の抽出
            if i in select_done_frames:
                _select_done_frame = frame
                pokemon_select_order[i] = extractor.extract_pokemon_select_numbers(
                    _select_done_frame
                )

            # 6vs6のポケモンを抽出する
            if i in standing_by_frames:
                _standing_by_frame = frame
                (
                    your_pokemon_names,
                    opponent_pokemon_names,
                    _is_exist_unknown_pokemon,
                ) = pokemon_extractor.extract_pre_battle_pokemons(_standing_by_frame)
                pre_battle_pokemons[i] = {
                    "your_pokemon_names": your_pokemon_names,
                    "opponent_pokemon_names": opponent_pokemon_names,
                }
                is_exist_unknown_pokemon_list1.append(_is_exist_unknown_pokemon)

            # 対戦中のポケモンを抽出する
            if i in level_50_frames:
                _level_50_frame = frame
                (
                    your_pokemon_name,
                    opponent_pokemon_name,
                    _is_exist_unknown_pokemon,
                ) = extractor.extract_pokemon_name_in_battle(_level_50_frame)
                battle_pokemons.append(
                    {
                        "frame_number": i,
                        "your_pokemon_name": your_pokemon_name,
                        "opponent_pokemon_name": opponent_pokemon_name,
                    },
                )
                is_exist_unknown_pokemon_list2.append(_is_exist_unknown_pokemon)

            # 勝ち負けを検出
            if i in win_or_lost_all_frames:
                _win_or_lost_frame = frame
                win_or_lost_result = extractor.extract_win_or_lost(_win_or_lost_frame)
                pre_win_or_lost[i] = win_or_lost_result

            # メッセージの文字認識(OCR)
            if i in message_window_frames:
                _message_frame = frame
                _message = extractor.extract_message(_message_frame)
                if _message is not None:
                    messages[i] = _message

        video.release()

        # 勝敗検出
        # 間違いやすいので、周辺フレームを全て見て判断する。全て unknown の時は弾く
        for win_or_lost_frame_numbers in compressed_win_or_lost_frames:
            if len(win_or_lost_frame_numbers) > 3:
                _win_or_lost_results = []
                for _win_or_lost_frame_number in win_or_lost_frame_numbers:
                    _win_or_lost_result = pre_win_or_lost[_win_or_lost_frame_number]
                    _win_or_lost_results.append(_win_or_lost_result)

                _win_or_lost_results = [
                    v for v in _win_or_lost_results if v != "unknown"
                ]
                win_or_lost_frame_number = win_or_lost_frame_numbers[-1]
                if len(_win_or_lost_results) == 0:
                    win_or_lost[win_or_lost_frame_number] = "unknown"
                    continue
                win_or_lost_result = Counter(_win_or_lost_results).most_common()[0][0]
                win_or_lost_frame_number = win_or_lost_frame_numbers[-1]
                win_or_lost[win_or_lost_frame_number] = win_or_lost_result

        # 順位が変動しなかった場合、その値を rank_numbers から削除する
        logger.info(f"Removing unchanged ranking... {self.video_id}")
        rank_frames = list(rank_numbers.keys())
        for i in range(len(rank_numbers) - 1):
            _ranking_frame_number = rank_frames[i]
            _next_ranking_frame_number = rank_frames[i + 1]

            if (
                rank_numbers[_ranking_frame_number]
                == rank_numbers[_next_ranking_frame_number]
            ):
                del rank_numbers[_ranking_frame_number]

        # 対戦の始点と終点を定義する
        self.firestore_handler.update_log_document(
            video_id=self.video_id,
            new_message="INFO: Defining battle start and end frame numbers...",
        )
        logger.info(f"Defining battle start and end frame numbers... {self.video_id}")
        battle_start_end_frame_numbers: List[Tuple[int, int]] = []
        rank_frames = list(rank_numbers.keys())
        for i in range(len(compressed_standing_by_frames)):
            _standing_by_frames = compressed_standing_by_frames[i]
            _standing_by_frame_number = _standing_by_frames[-1]

            # チーム選択からの場合(最初の順位表示なし)
            if len(compressed_standing_by_frames) == len(rank_numbers):
                _ranking_frame = rank_frames[i]
            else:
                # バトルスタジアム入場(最初に表示された順位がある)からの場合
                _ranking_frame = rank_frames[i + 1]

            if _standing_by_frame_number < _ranking_frame:
                battle_start_end_frame_numbers.append(
                    (_standing_by_frame_number, _ranking_frame)
                )

        if any(is_exist_unknown_pokemon_list1) or any(is_exist_unknown_pokemon_list2):
            self.gcs_handler.upload_unknown_pokemon_templates_to_gcs(
                trainer_id=self.trainer_id_in_DB
            )
            self.gcs_handler.upload_unknown_pokemon_name_window_templates_to_gcs(
                trainer_id=self.trainer_id_in_DB
            )
            self.firestore_handler.update_log_document(
                video_id=self.video_id,
                new_message="ERROR: Unknown pokemon exists. Stop processing. Please annotate unknown pokemons.",
            )

            params = {
                "from": "PokeBattleLogger <notify@poke-battle-logger-api.com>",
                "to": self.email,
                "subject": "PokeBattleLogger: Failed to extract stats from video because unknown pokemon exists.",
                "html": fail_unknown_pokemons_templates.format(video_id=self.video_id),
            }
            resend.Emails.send(params)

            raise Exception("Unknown pokemon exists. Stop processing.")

        # build formatted data
        self.firestore_handler.update_log_document(
            video_id=self.video_id, new_message="INFO: Building formatted data..."
        )
        logger.info(f"Building formatted data... {self.video_id}")
        data_builder = DataBuilder(
            trainer_id=self.trainer_id_in_DB,
            video_id=self.video_id,
            battle_start_end_frame_numbers=battle_start_end_frame_numbers,
            battle_pokemons=battle_pokemons,
            pre_battle_pokemons=pre_battle_pokemons,
            pokemon_select_order=pokemon_select_order,
            rank_numbers=rank_numbers,
            messages=messages,
            win_or_lost=win_or_lost,
        )

        (
            battles,
            battle_logs,
            modified_pre_battle_pokemons,
            modified_in_battle_pokemons,
            modified_messages,
        ) = data_builder.build()

        # insert data to database
        self.firestore_handler.update_log_document(
            video_id=self.video_id, new_message="INFO: Inserting data to database..."
        )
        logger.info(f"Inserting data to database... {self.video_id}")

        self.database_handler.insert_battle_id(battles)
        self.database_handler.insert_battle_summary(battle_logs)
        self.database_handler.insert_battle_pokemon_team(modified_pre_battle_pokemons)
        self.database_handler.insert_in_battle_pokemon_log(modified_in_battle_pokemons)
        self.database_handler.insert_message_log(modified_messages)

        # build fainted log
        self.firestore_handler.update_log_document(
            video_id=self.video_id, new_message="INFO: Build And Insert Fainted Log..."
        )
        logger.info(f"Build And Insert Fainted Log... {self.video_id}")
        self.database_handler.build_and_insert_fainted_log(
            modified_in_battle_pokemons, modified_messages
        )

        self.firestore_handler.update_log_document(
            video_id=self.video_id, new_message="INFO: Finish Processing ALL!!!"
        )
        logger.info(f"Finish Processing ALL!!! {self.video_id}")

        self.database_handler.update_video_process_status(
            trainer_id_in_DB=self.trainer_id_in_DB,
            video_id=self.video_id,
            status="Processing Done.",
        )

        return (
            len(battle_logs),
            len(
                [
                    battle_log
                    for battle_log in battle_logs
                    if battle_log.win_or_lose == "win"
                ]
            ),
            len(
                [
                    battle_log
                    for battle_log in battle_logs
                    if battle_log.win_or_lose == "lose"
                ]
            ),
        )
