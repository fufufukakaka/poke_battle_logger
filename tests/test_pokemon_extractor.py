import cv2
from poke_battle_logger.batch.pokemon_extractor import PokemonExtractor

pokemon_extractor = PokemonExtractor()


def test_pokemon_extractor_kairyu():
    pokemon_image = cv2.imread("tests/fixtures/pokemons/カイリュー.png")
    (
        pokemon_name,
        _,
    ) = pokemon_extractor._search_pokemon_by_transformers(pokemon_image)
    assert pokemon_name == "カイリュー"


def test_pokemon_extractor_raudoboon():
    pokemon_image = cv2.imread("tests/fixtures/pokemons/ラウドボーン.png")
    (
        pokemon_name,
        _,
    ) = pokemon_extractor._search_pokemon_by_transformers(pokemon_image)
    assert pokemon_name == "ラウドボーン"


def test_pokemon_extractor_sunanokegawa():
    pokemon_image = cv2.imread("tests/fixtures/pokemons/スナノケガワ.png")
    (
        pokemon_name,
        _,
    ) = pokemon_extractor._search_pokemon_by_transformers(pokemon_image)
    assert pokemon_name == "スナノケガワ"


def test_pokemon_extractor_dohidoide():
    pokemon_image = cv2.imread("tests/fixtures/pokemons/ドヒドイデ.png")
    (
        pokemon_name,
        _,
    ) = pokemon_extractor._search_pokemon_by_transformers(pokemon_image)
    assert pokemon_name == "ドヒドイデ"


def test_pokemon_extractor_mimizuzu():
    pokemon_image = cv2.imread("tests/fixtures/pokemons/ミミズズ.png")
    (
        pokemon_name,
        _,
    ) = pokemon_extractor._search_pokemon_by_transformers(pokemon_image)
    assert pokemon_name == "ミミズズ"


def test_pokemon_extractor_morobareru():
    pokemon_image = cv2.imread("tests/fixtures/pokemons/モロバレル.png")
    (
        pokemon_name,
        _,
    ) = pokemon_extractor._search_pokemon_by_transformers(pokemon_image)
    assert pokemon_name == "モロバレル"
