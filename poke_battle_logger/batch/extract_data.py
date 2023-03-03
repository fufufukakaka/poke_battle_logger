import cv2
from tqdm.auto import tqdm

from poke_battle_logger.batch.frame_compressor import frame_compress
from poke_battle_logger.batch.frame_detector import FrameDetector
from poke_battle_logger.batch.pokemon_extractor import PokemonExtractor


def main():
    movie_id = "O8GmphpBbco"
    video = cv2.VideoCapture(f'video/{movie_id}.mp4')

    frame_detector = FrameDetector()
    pokemon_extractor = PokemonExtractor()

    standing_by_frames = []
    level_50_frames = []
    ranking_frames = []
    win_or_lost_frames = []
    for i in tqdm(range(int(video.get(cv2.CAP_PROP_FRAME_COUNT)))):
        ret, frame = video.read()
        if ret:
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
        else:
            continue

    # compress
    compressed_standing_by_frames = frame_compress(standing_by_frames)
    compressed_level_50_frames = frame_compress(level_50_frames)
    compressed_ranking_frames = frame_compress(ranking_frames)
    compressed_win_or_lost_frames = frame_compress(win_or_lost_frames)

    # 対戦の始点と終点を定義する
    battle_start_end_frame_numbers = []
    for i in range(len(compressed_standing_by_frames)):
        _standing_by_frames = compressed_standing_by_frames[i]
        _standing_by_frame = _standing_by_frames[-10]

        _ranking_frames = compressed_ranking_frames[i]
        _ranking_frame = _ranking_frames[-10]

        if _standing_by_frame < _ranking_frame:
            battle_start_end_frame_numbers.append([_standing_by_frame, _ranking_frame])

    # 6vs6のポケモンを抽出する
    pre_battle_pokemons = []
    for i in range(len(compressed_standing_by_frames)):
        _standing_by_frames = compressed_standing_by_frames[i]
        _standing_by_frame_number = _standing_by_frames[-10]

        video.set(cv2.CAP_PROP_POS_FRAMES, _standing_by_frame_number - 1)
        _, _standing_by_frame = video.read()

        (
            your_pokemon_names,
            opponent_pokemon_names,
        ) = pokemon_extractor.extract_pre_battle_pokemons(_standing_by_frame)
        pre_battle_pokemons.append(
            {
                "your_pokemon_names": your_pokemon_names,
                "opponent_pokemon_names": opponent_pokemon_names,
            }
        )

    # 対戦中のポケモンを抽出する
    battle_pokemons = []
    for level_50_frame_numbers in compressed_level_50_frames:
        _in_battle_data = []
        for _level_50_frame_number in level_50_frame_numbers:
            video.set(cv2.CAP_PROP_POS_FRAMES, _level_50_frame_number - 1)
            _, _level_50_frame = video.read()

            (
                your_pokemon_name,
                opponent_pokemon_name,
            ) = pokemon_extractor.extract_pokemon_name_in_battle(_level_50_frame)
            _in_battle_data.append(
                {
                    "frame_number": _level_50_frame_number,
                    "your_pokemon_name": your_pokemon_name,
                    "opponent_pokemon_name": opponent_pokemon_name,
                }
            )
        battle_pokemons.append(_in_battle_data)

    # 勝ち負けを検出
    win_or_lost = []
    for win_or_lost_frame_numbers in compressed_win_or_lost_frames:
        _win_or_lost = []
        for _win_or_lost_frame_number in win_or_lost_frame_numbers:
            video.set(cv2.CAP_PROP_POS_FRAMES, _win_or_lost_frame_number - 1)
            _, _win_or_lost_frame = video.read()

            _win_or_lost.append(
                pokemon_extractor.extract_win_or_lost(_win_or_lost_frame)
            )
        win_or_lost.append(_win_or_lost)

    # ランクを検出(OCR)


if __name__ == "__main__":
    main()
