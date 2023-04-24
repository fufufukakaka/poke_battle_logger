import cv2

from poke_battle_logger.batch.pokemon_name_window_extractor import (
    PokemonNameWindowExtractor,
)

pokemon_name_window_extractor = PokemonNameWindowExtractor()


def test_pokemon_name_window_extract_jpn():
    jpn_pokemon_name_window = cv2.imread("tests/fixtures/name_window/ハッサム.png")
    # Act
    pokemon_name, _ = pokemon_name_window_extractor.extract_pokemon_name_in_battle(
        name_window=jpn_pokemon_name_window
    )
    # Assert
    assert pokemon_name.split("_")[0] == "ハッサム"


def test_pokemon_name_window_extract_eng():
    jpn_pokemon_name_window = cv2.imread("tests/fixtures/name_window/キノガッサ_英語.png")
    # Act
    pokemon_name, _ = pokemon_name_window_extractor.extract_pokemon_name_in_battle(
        name_window=jpn_pokemon_name_window
    )
    # Assert
    assert pokemon_name.split("_")[0] == "キノガッサ"


def test_pokemon_name_window_extract_kor():
    jpn_pokemon_name_window = cv2.imread("tests/fixtures/name_window/ハバタクカミ_韓国語.png")
    # Act
    pokemon_name, _ = pokemon_name_window_extractor.extract_pokemon_name_in_battle(
        name_window=jpn_pokemon_name_window
    )
    # Assert
    assert pokemon_name.split("_")[0] == "ハバタクカミ"


def test_pokemon_name_window_extract_chi():
    jpn_pokemon_name_window = cv2.imread("tests/fixtures/name_window/イダイナキバ_中国語.png")
    # Act
    pokemon_name, _ = pokemon_name_window_extractor.extract_pokemon_name_in_battle(
        name_window=jpn_pokemon_name_window
    )
    # Assert
    assert pokemon_name.split("_")[0] == "イダイナキバ"
