import logging
import click
import cv2
from rich.logging import RichHandler
from tqdm.auto import tqdm

from poke_battle_logger.batch.data_builder import DataBuilder
from poke_battle_logger.batch.frame_compressor import (
    frame_compress,
    message_frame_compress,
)
from poke_battle_logger.batch.frame_detector import FrameDetector
from poke_battle_logger.batch.pokemon_extractor import PokemonExtractor
from poke_battle_logger.sqlite_handler import SQLiteHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler()],
)
logger = logging.getLogger("rich")


@click.command()
@click.option("--video_id", "-v", type=str, required=True)
def main(video_id: str):
    video = cv2.VideoCapture(f"video/{video_id}.mp4")

    frame_detector = FrameDetector()
    pokemon_extractor = PokemonExtractor()
    sqlite_handler = SQLiteHandler()

    select_done_frames = []
    standing_by_frames = []
    level_50_frames = []
    ranking_frames = []
    win_or_lost_frames = []
    message_window_frames = []

    is_exist_unknown_pokemon = False

    logger.info("Detecting frames...")
    for i in tqdm(range(int(video.get(cv2.CAP_PROP_FRAME_COUNT)))):
        ret, frame = video.read()
        if ret:
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

    # compress
    logger.info("Compressing frame array...")
    compressed_select_done_frames = frame_compress(select_done_frames)
    compressed_standing_by_frames = frame_compress(standing_by_frames)
    compressed_level_50_frames = frame_compress(level_50_frames)
    compressed_ranking_frames = frame_compress(ranking_frames)
    compressed_win_or_lost_frames = frame_compress(win_or_lost_frames)
    compressed_message_window_frames = message_frame_compress(
        message_window_frames, frame_threshold=3
    )

    # ??????????????????(OCR)
    logger.info("Extracting ranking...")
    rank_numbers = {}
    for ranking_frame_numbers in compressed_ranking_frames:
        ranking_frame_number = ranking_frame_numbers[-1]
        video.set(cv2.CAP_PROP_POS_FRAMES, ranking_frame_number - 1)
        _, _ranking_frame = video.read()
        rank_numbers[ranking_frame_number] = pokemon_extractor.extract_rank_number(
            _ranking_frame
        )

    # ??????????????????????????????????????????????????? rank_numbers ??????????????????
    logger.info("Removing unchanged ranking from rank_numbers...")
    rank_frames = list(rank_numbers.keys())
    for i in range(len(rank_numbers) - 1):
        _ranking_frame_number = rank_frames[i]
        _next_ranking_frame_number = rank_frames[i + 1]

        if (
            rank_numbers[_ranking_frame_number]
            == rank_numbers[_next_ranking_frame_number]
        ):
            del rank_numbers[_ranking_frame_number]

    # ???????????????????????????????????????
    logger.info("Defining battle start and end frame numbers...")
    battle_start_end_frame_numbers = []
    rank_frames = list(rank_numbers.keys())
    for i in range(len(compressed_standing_by_frames)):
        _standing_by_frames = compressed_standing_by_frames[i]
        _standing_by_frame = _standing_by_frames[-10]

        # ??????????????????????????????(???????????????????????????)
        if len(compressed_standing_by_frames) == len(rank_numbers):
            _ranking_frame = rank_frames[i]
        else:
            # ??????????????????????????????(???????????????????????????????????????)???????????????
            _ranking_frame = rank_frames[i + 1]

        if _standing_by_frame < _ranking_frame:
            battle_start_end_frame_numbers.append([_standing_by_frame, _ranking_frame])

    # ???????????????????????????????????????
    logger.info("Extracting pokemon select order...")
    pokemon_select_order = {}
    for i in range(len(compressed_select_done_frames)):
        _select_done_frames = compressed_select_done_frames[i]
        _select_done_frame_number = _select_done_frames[-1]

        video.set(cv2.CAP_PROP_POS_FRAMES, _select_done_frame_number - 1)
        _, _select_done_frame = video.read()

        _pokemon_select_order = pokemon_extractor.extract_pokemon_select_numbers(
            _select_done_frame
        )
        pokemon_select_order[_select_done_frame_number] = _pokemon_select_order

    # 6vs6??????????????????????????????
    logger.info("Extracting pre-battle pokemons...")
    pre_battle_pokemons = {}
    for i in range(len(compressed_standing_by_frames)):
        _standing_by_frames = compressed_standing_by_frames[i]
        _standing_by_frame_number = _standing_by_frames[-10]

        video.set(cv2.CAP_PROP_POS_FRAMES, _standing_by_frame_number - 1)
        _, _standing_by_frame = video.read()

        (
            your_pokemon_names,
            opponent_pokemon_names,
            is_exist_unknown_pokemon,
        ) = pokemon_extractor.extract_pre_battle_pokemons(_standing_by_frame)
        pre_battle_pokemons[_standing_by_frame_number] = {
            "your_pokemon_names": your_pokemon_names,
            "opponent_pokemon_names": opponent_pokemon_names,
        }

    # ???????????????????????????????????????
    logger.info("Extracting in-battle pokemons...")
    battle_pokemons = []
    for level_50_frame_numbers in compressed_level_50_frames:
        _level_50_frame_number = level_50_frame_numbers[-10]
        video.set(cv2.CAP_PROP_POS_FRAMES, _level_50_frame_number - 1)
        _, _level_50_frame = video.read()

        (
            your_pokemon_name,
            opponent_pokemon_name,
            is_exist_unknown_pokemon,
        ) = pokemon_extractor.extract_pokemon_name_in_battle(_level_50_frame)
        battle_pokemons.append(
            {
                "frame_number": _level_50_frame_number,
                "your_pokemon_name": your_pokemon_name,
                "opponent_pokemon_name": opponent_pokemon_name,
            }
        )

    # unknown ???????????????????????????????????????????????????
    if is_exist_unknown_pokemon:
        logger.warning(
            "Unknown pokemon exists. Stop processing. Please annotate unknown pokemons."
        )
        return

    # ?????????????????????
    logger.info("Extracting win or lost...")
    win_or_lost = {}
    for win_or_lost_frame_numbers in compressed_win_or_lost_frames:
        win_or_lost_frame_number = win_or_lost_frame_numbers[-1]
        video.set(cv2.CAP_PROP_POS_FRAMES, win_or_lost_frame_number - 1)
        _, _win_or_lost_frame = video.read()
        win_or_lost[win_or_lost_frame_number] = pokemon_extractor.extract_win_or_lost(
            _win_or_lost_frame
        )

    # ??????????????????????????????(OCR)
    logger.info("Extracting message...")
    messages = {}
    for message_frame_numbers in compressed_message_window_frames:
        message_frame_number = message_frame_numbers[-1]
        video.set(cv2.CAP_PROP_POS_FRAMES, message_frame_number - 1)
        _, _message_frame = video.read()
        _message = pokemon_extractor.extract_message(_message_frame)
        if _message is not None:
            messages[message_frame_number] = _message

    # build formatted data
    logger.info("Build Formatted Data...")
    data_builder = DataBuilder(
        video_id=video_id,
        battle_start_end_frame_numbers=battle_start_end_frame_numbers,
        battle_pokemons=battle_pokemons,
        pre_battle_pokemons=pre_battle_pokemons,
        pokemon_select_order=pokemon_select_order,
        rank_numbers=rank_numbers,
        messages=messages,
        win_or_lost=win_or_lost,
    )

    (
        battle_ids,
        battle_logs,
        modified_pre_battle_pokemons,
        modified_in_battle_pokemons,
        modified_messages,
    ) = data_builder.build()

    # insert data to database
    logger.info("Insert Data to Database...")
    sqlite_handler.create_tables()
    sqlite_handler.insert_battle_id(battle_ids)
    sqlite_handler.insert_battle_summary(battle_logs)
    sqlite_handler.insert_battle_pokemon_team(modified_pre_battle_pokemons)
    sqlite_handler.insert_in_battle_pokemon_log(modified_in_battle_pokemons)
    sqlite_handler.insert_message_log(modified_messages)

    logger.info("Finish Processing!!!")


if __name__ == "__main__":
    main()
