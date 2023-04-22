import asyncio
import re
from collections import Counter
import threading

import cv2
import yt_dlp
from fastapi import WebSocket
from tqdm.auto import tqdm
import concurrent.futures
from poke_battle_logger.batch.data_builder import DataBuilder
from poke_battle_logger.batch.extractor import Extractor
from poke_battle_logger.batch.frame_compressor import (
    frame_compress,
    message_frame_compress,
)
from poke_battle_logger.batch.frame_detector import FrameDetector
from poke_battle_logger.batch.pokemon_extractor import PokemonExtractor
from poke_battle_logger.sqlite_handler import SQLiteHandler


class PokeBattleExtractor:
    """
    API でポケモンの対戦動画から情報を抽出するクラス
    """

    def __init__(self, video_id: str, language: str, trainer_id: int) -> None:
        self.video_id = video_id
        self.language = language
        self.trainer_id = trainer_id

    def _download_video(self, status_json, websocket_for_status, download_complete_event):
        def extract_percentage(percentage_str):
            ansi_escape = re.compile(r"\x1b[^m]*m")
            cleaned_str = ansi_escape.sub("", percentage_str)
            percentage = float(cleaned_str.rstrip("%"))
            return percentage

        def _progress_hook(status_json, status, websocket: WebSocket):
            if status["status"] == "downloading":
                if "INFO: Downloading video..." not in status_json["message"]:
                    status_json["message"].append("INFO: Downloading video...")
                status_json["progress"] = extract_percentage(status["_percent_str"])
                new_loop = asyncio.new_event_loop()
                new_loop.run_until_complete(websocket.send_json(status_json))
            elif status["status"] == "finished":
                status_json["message"].append("INFO: Download complete")
                status_json["progress"] = 100
                new_loop = asyncio.new_event_loop()
                new_loop.run_until_complete(websocket.send_json(status_json))

        # download youtube video use yt-dlp
        # setting: 1080p, 30fps, mp4, video only(音声なし)
        # output: video/{video_id}.mp4
        yt_dlp_opts = {
            "format": "bestvideo[height<=1080][fps<=30][ext=mp4]",
            "outtmpl": f"video/{self.video_id}.mp4",
            "progress_hooks": [lambda status: _progress_hook(status_json, status, websocket_for_status)],
            "quiet": True,
        }

        with yt_dlp.YoutubeDL(yt_dlp_opts) as ydl:
            ydl.download([f"https://www.youtube.com/watch?v={self.video_id}"])
        download_complete_event.set()

    async def run(self, websocket_for_status: WebSocket) -> None:
        status_json = {
            "progress": 0,
            "message": [],
        }

        download_complete_event = threading.Event()

        with concurrent.futures.ThreadPoolExecutor() as executor:
            await asyncio.get_event_loop().run_in_executor(executor, lambda: self._download_video(status_json, websocket_for_status, download_complete_event))
        download_complete_event.wait()

        status_json["message"].append("INFO: Read Video...")
        await websocket_for_status.send_json(status_json)
        video = cv2.VideoCapture(f"video/{self.video_id}.mp4")

        frame_detector = FrameDetector(self.language)
        extractor = Extractor(self.language)
        pokemon_extractor = PokemonExtractor()
        sqlite_handler = SQLiteHandler()

        first_ranking_frames = []
        select_done_frames = []
        standing_by_frames = []
        level_50_frames = []
        ranking_frames = []
        win_or_lost_frames = []
        message_window_frames = []

        status_json["message"].append("INFO: Detecting frames...")
        await websocket_for_status.send_json(status_json)

        total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        for i in range(total_frames):
            ret, frame = video.read()
            if ret:
                # first ranking
                if frame_detector.is_first_ranking_frame(frame):
                    first_ranking_frames.append(i)

                # select done
                if frame_detector.is_select_done_frame(frame):
                    select_done_frames.append(i)

                # standing_by
                if frame_detector.is_standing_by_frame(frame):
                    standing_by_frames.append(i)

                # level_50
                if frame_detector.is_level_50_frame(frame):
                    level_50_frames.append(i)

                # ranking
                if frame_detector.is_ranking_frame(frame):
                    ranking_frames.append(i)

                # win_or_lost
                if frame_detector.is_win_or_lost_frame(frame):
                    win_or_lost_frames.append(i)

                # message window
                if frame_detector.is_message_window_frame(frame):
                    message_window_frames.append(i)
            else:
                continue
            if i % 100 == 0:
                status_json["progress"] = int((i / total_frames) * 100)
                await websocket_for_status.send_json(status_json)

        # compress
        status_json["message"].append("INFO: Compressing frame array...")
        await websocket_for_status.send_json(status_json)

        compressed_first_ranking_frames = frame_compress(first_ranking_frames)
        compressed_select_done_frames = frame_compress(select_done_frames)
        compressed_standing_by_frames = frame_compress(standing_by_frames, ignore_short_frames=True)
        compressed_level_50_frames = frame_compress(level_50_frames)
        compressed_ranking_frames = frame_compress(ranking_frames)
        compressed_win_or_lost_frames = frame_compress(win_or_lost_frames)
        compressed_message_window_frames = message_frame_compress(
            message_window_frames, frame_threshold=3
        )

        # 開始時のランクを検出(OCR)
        status_json["message"].append("INFO: Extracting first ranking...")
        await websocket_for_status.send_json(status_json)
        rank_numbers = {}
        first_ranking_frame_number = compressed_first_ranking_frames[0][-5]
        video.set(cv2.CAP_PROP_POS_FRAMES, first_ranking_frame_number - 1)
        _, _first_ranking_frame = video.read()
        rank_numbers[first_ranking_frame_number] = extractor.extract_first_rank_number(
            _first_ranking_frame
        )

        # ランクを検出(OCR)
        status_json["message"].append("INFO: Extracting ranking...")
        await websocket_for_status.send_json(status_json)
        for ranking_frame_numbers in compressed_ranking_frames:
            ranking_frame_number = ranking_frame_numbers[-5]
            video.set(cv2.CAP_PROP_POS_FRAMES, ranking_frame_number - 1)
            _, _ranking_frame = video.read()
            rank_numbers[ranking_frame_number] = extractor.extract_rank_number(
                _ranking_frame
            )

        # 順位が変動しなかった場合、その値を rank_numbers から削除する
        status_json["message"].append("INFO: Removing unchanged ranking from rank_numbers...")
        await websocket_for_status.send_json(status_json)
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
        status_json["message"].append("INFO: Defining battle start and end frame numbers...")
        await websocket_for_status.send_json(status_json)
        battle_start_end_frame_numbers = []
        rank_frames = list(rank_numbers.keys())
        for i in range(len(compressed_standing_by_frames)):
            _standing_by_frames = compressed_standing_by_frames[i]
            _standing_by_frame = _standing_by_frames[-1]

            # チーム選択からの場合(最初の順位表示なし)
            if len(compressed_standing_by_frames) == len(rank_numbers):
                _ranking_frame = rank_frames[i]
            else:
                # バトルスタジアム入場(最初に表示された順位がある)からの場合
                _ranking_frame = rank_frames[i + 1]

            if _standing_by_frame < _ranking_frame:
                battle_start_end_frame_numbers.append([_standing_by_frame, _ranking_frame])

        # ポケモンの選出順を抽出する
        status_json["message"].append("INFO: Extracting pokemon select order...")
        await websocket_for_status.send_json(status_json)
        pokemon_select_order = {}
        for i in range(len(compressed_select_done_frames)):
            _select_done_frames = compressed_select_done_frames[i]
            _select_done_frame_number = _select_done_frames[-5]

            video.set(cv2.CAP_PROP_POS_FRAMES, _select_done_frame_number - 1)
            _, _select_done_frame = video.read()

            _pokemon_select_order = extractor.extract_pokemon_select_numbers(
                _select_done_frame
            )
            pokemon_select_order[_select_done_frame_number] = _pokemon_select_order

        # 6vs6のポケモンを抽出する
        status_json["message"].append("INFO: Extracting pre-battle pokemons...")
        await websocket_for_status.send_json(status_json)
        pre_battle_pokemons = {}
        is_exist_unknown_pokemon_list1 = []
        for i in range(len(compressed_standing_by_frames)):
            _standing_by_frames = compressed_standing_by_frames[i]
            if len(_standing_by_frames) == 1:
                continue
            _standing_by_frame_number = _standing_by_frames[-1]

            video.set(cv2.CAP_PROP_POS_FRAMES, _standing_by_frame_number - 1)
            _, _standing_by_frame = video.read()

            (
                your_pokemon_names,
                opponent_pokemon_names,
                _is_exist_unknown_pokemon,
            ) = pokemon_extractor.extract_pre_battle_pokemons(_standing_by_frame)
            pre_battle_pokemons[_standing_by_frame_number] = {
                "your_pokemon_names": your_pokemon_names,
                "opponent_pokemon_names": opponent_pokemon_names,
            }
            is_exist_unknown_pokemon_list1.append(_is_exist_unknown_pokemon)

        # 対戦中のポケモンを抽出する
        status_json["message"].append("INFO: Extracting in-battle pokemons...")
        await websocket_for_status.send_json(status_json)
        battle_pokemons = []
        is_exist_unknown_pokemon_list2 = []
        for level_50_frame_numbers in compressed_level_50_frames:
            _level_50_frame_number = level_50_frame_numbers[-1]
            video.set(cv2.CAP_PROP_POS_FRAMES, _level_50_frame_number - 1)
            _, _level_50_frame = video.read()

            (
                your_pokemon_name,
                opponent_pokemon_name,
                _is_exist_unknown_pokemon,
            ) = extractor.extract_pokemon_name_in_battle(_level_50_frame)

            battle_pokemons.append(
                {
                    "frame_number": _level_50_frame_number,
                    "your_pokemon_name": your_pokemon_name,
                    "opponent_pokemon_name": opponent_pokemon_name,
                }
            )
            is_exist_unknown_pokemon_list2.append(_is_exist_unknown_pokemon)

        if any(is_exist_unknown_pokemon_list1) or any(is_exist_unknown_pokemon_list2):
            status_json["message"].append("ERROR: Unknown pokemon exists. Stop processing. Please annotate unknown pokemons.")
            await websocket_for_status.send_json(status_json)
            return

        # 勝ち負けを検出
        # 間違いやすいので、周辺最大10フレームを見て判断する。全て unknown の時は弾く
        status_json["message"].append("INFO: Extracting win or lost...")
        await websocket_for_status.send_json(status_json)
        win_or_lost = {}
        for win_or_lost_frame_numbers in compressed_win_or_lost_frames:
            if len(win_or_lost_frame_numbers) > 3:
                _win_or_lost_results = []
                for idx in range(max(10, len(win_or_lost_frame_numbers))):
                    _win_or_lost_frame_number = win_or_lost_frame_numbers[-1] - idx
                    video.set(cv2.CAP_PROP_POS_FRAMES, _win_or_lost_frame_number - 1)
                    _, _win_or_lost_frame = video.read()
                    _win_or_lost_result = extractor.extract_win_or_lost(_win_or_lost_frame)
                    _win_or_lost_results.append(_win_or_lost_result)

                _win_or_lost_results = [v for v in _win_or_lost_results if v != "unknown"]
                win_or_lost_frame_number = win_or_lost_frame_numbers[-1]
                if len(_win_or_lost_results) == 0:
                    win_or_lost[win_or_lost_frame_number] = "unknown"
                    continue
                win_or_lost_result = Counter(_win_or_lost_results).most_common()[0][0]
                win_or_lost_frame_number = win_or_lost_frame_numbers[-1]
                win_or_lost[win_or_lost_frame_number] = win_or_lost_result

        # メッセージの文字認識(OCR)
        status_json["message"].append("INFO: Extracting message...")
        await websocket_for_status.send_json(status_json)
        messages = {}
        for message_frame_numbers in compressed_message_window_frames:
            message_frame_number = message_frame_numbers[-1]
            video.set(cv2.CAP_PROP_POS_FRAMES, message_frame_number - 1)
            _, _message_frame = video.read()
            _message = extractor.extract_message(_message_frame)
            if _message is not None:
                messages[message_frame_number] = _message

        # build formatted data
        status_json["message"].append("INFO: Build Formatted Data...")
        await websocket_for_status.send_json(status_json)
        data_builder = DataBuilder(
            trainer_id=self.trainer_id,
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
        status_json["message"].append("INFO: Insert Data to Database...")
        await websocket_for_status.send_json(status_json)
        sqlite_handler.create_tables()
        sqlite_handler.insert_battle_id(battles)
        sqlite_handler.insert_battle_summary(battle_logs)
        sqlite_handler.insert_battle_pokemon_team(modified_pre_battle_pokemons)
        sqlite_handler.insert_in_battle_pokemon_log(modified_in_battle_pokemons)
        sqlite_handler.insert_message_log(modified_messages)

        status_json["message"].append("INFO: Finish Processing!!!")
        await websocket_for_status.send_json(status_json)

        return
