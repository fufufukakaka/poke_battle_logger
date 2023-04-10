import glob
import os
import time
from dataclasses import dataclass
from typing import List, Tuple, cast
from PIL import Image
import cv2
import numpy as np
from dotenv import load_dotenv
from transformers import pipeline

from config.config import (OPPONENT_PRE_POKEMON_POSITION, POKEMON_POSITIONS,
                           POKEMON_TEMPLATE_MATCHING_THRESHOLD,
                           YOUR_PRE_POKEMON_POSITION)
from poke_battle_logger.batch.pokemon_name_window_extractor import \
    PokemonNameWindowExtractor

load_dotenv()

MODEL_NAME = "fufufukakaka/autotrain-pokemon-image-classification-3-47925116995"



@dataclass
class PokemonClassifierResult:
    label: str
    score: float


class PokemonExtractor:
    """
    6vs6 の見せ合い画面でのポケモン検出
    """

    def __init__(self) -> None:
        self.pre_battle_pokemon_templates = self._setup_pre_battle_pokemon_templates()
        self.pokemon_name_window_extractor = PokemonNameWindowExtractor()
        self.classifier_pipe = pipeline(task="image-classification", model=MODEL_NAME, use_auth_token=os.getenv('HF_ACCESS_TOKEN'))

    def _setup_pre_battle_pokemon_templates(self):
        pre_battle_pokemon_template_paths = glob.glob(
            "template_images/labeled_pokemon_templates/*.png"
        )
        pre_battle_pokemon_templates = {}
        for path in pre_battle_pokemon_template_paths:
            _gray_image = cv2.imread(path, 0)
            pre_battle_pokemon_templates[
                path.split("/")[-1].split(".")[0]
            ] = _gray_image
        return pre_battle_pokemon_templates

    def _search_pokemon_by_template_matching(self, pokemon_image) -> Tuple[str, bool]:
        """
        テンプレートマッチングでポケモンを検出する
        ベクトル検索でポケモンを検出する
        """
        score_results = {}
        gray_pokemon_image = cv2.cvtColor(pokemon_image, cv2.COLOR_BGR2GRAY)

        for pokemon_name, template in self.pre_battle_pokemon_templates.items():
            res = cv2.matchTemplate(gray_pokemon_image, template, cv2.TM_CCOEFF_NORMED)
            score = cv2.minMaxLoc(res)[1]
            if score >= POKEMON_TEMPLATE_MATCHING_THRESHOLD:
                score_results[pokemon_name] = score
        if len(score_results) == 0:
            # save image for annotation(name is timestamp)
            cv2.imwrite(
                "template_images/unknown_pokemon_templates/"
                + str(time.time())
                + ".png",
                pokemon_image,
            )
            return "unknown_pokemon", True
        return max(score_results, key=score_results.get), False

    def _search_pokemon_by_transformers(
        self, pokemon_image: np.ndarray
    ) -> Tuple[str, bool]:
        """
        autotrain model でポケモンを特定する
        """

        pokemon_image2 = cv2.cvtColor(pokemon_image, cv2.COLOR_BGR2RGB)
        pokemon_image3 = Image.fromarray(pokemon_image2)
        results = cast(List[PokemonClassifierResult], self.classifier_pipe(pokemon_image3))

        if results[0]["score"] > 0.5:
            return results[0]["label"], False
        else:
            # テンプレートマッチングで検出する
            cv2.imwrite(
                "template_images/unknown_pokemon_templates/"
                + str(time.time())
                + ".png",
                pokemon_image,
            )
            return self._search_pokemon_by_template_matching(pokemon_image)

    def _get_pokemons(self, frame):
        """
        6vs6 の見せあい
        """

        opponent_pokemon_1 = frame[
            POKEMON_POSITIONS[0][0] : POKEMON_POSITIONS[0][1],
            OPPONENT_PRE_POKEMON_POSITION[0] : OPPONENT_PRE_POKEMON_POSITION[1],
        ]
        opponent_pokemon_2 = frame[
            POKEMON_POSITIONS[1][0] : POKEMON_POSITIONS[1][1],
            OPPONENT_PRE_POKEMON_POSITION[0] : OPPONENT_PRE_POKEMON_POSITION[1],
        ]
        opponent_pokemon_3 = frame[
            POKEMON_POSITIONS[2][0] : POKEMON_POSITIONS[2][1],
            OPPONENT_PRE_POKEMON_POSITION[0] : OPPONENT_PRE_POKEMON_POSITION[1],
        ]
        opponent_pokemon_4 = frame[
            POKEMON_POSITIONS[3][0] : POKEMON_POSITIONS[3][1],
            OPPONENT_PRE_POKEMON_POSITION[0] : OPPONENT_PRE_POKEMON_POSITION[1],
        ]
        opponent_pokemon_5 = frame[
            POKEMON_POSITIONS[4][0] : POKEMON_POSITIONS[4][1],
            OPPONENT_PRE_POKEMON_POSITION[0] : OPPONENT_PRE_POKEMON_POSITION[1],
        ]
        opponent_pokemon_6 = frame[
            POKEMON_POSITIONS[5][0] : POKEMON_POSITIONS[5][1],
            OPPONENT_PRE_POKEMON_POSITION[0] : OPPONENT_PRE_POKEMON_POSITION[1],
        ]
        opponent_pokemons = [
            opponent_pokemon_1,
            opponent_pokemon_2,
            opponent_pokemon_3,
            opponent_pokemon_4,
            opponent_pokemon_5,
            opponent_pokemon_6,
        ]

        your_pokemon_1 = frame[
            POKEMON_POSITIONS[0][0] : POKEMON_POSITIONS[0][1],
            YOUR_PRE_POKEMON_POSITION[0] : YOUR_PRE_POKEMON_POSITION[1],
        ]
        your_pokemon_2 = frame[
            POKEMON_POSITIONS[1][0] : POKEMON_POSITIONS[1][1],
            YOUR_PRE_POKEMON_POSITION[0] : YOUR_PRE_POKEMON_POSITION[1],
        ]
        your_pokemon_3 = frame[
            POKEMON_POSITIONS[2][0] : POKEMON_POSITIONS[2][1],
            YOUR_PRE_POKEMON_POSITION[0] : YOUR_PRE_POKEMON_POSITION[1],
        ]
        your_pokemon_4 = frame[
            POKEMON_POSITIONS[3][0] : POKEMON_POSITIONS[3][1],
            YOUR_PRE_POKEMON_POSITION[0] : YOUR_PRE_POKEMON_POSITION[1],
        ]
        your_pokemon_5 = frame[
            POKEMON_POSITIONS[4][0] : POKEMON_POSITIONS[4][1],
            YOUR_PRE_POKEMON_POSITION[0] : YOUR_PRE_POKEMON_POSITION[1],
        ]
        your_pokemon_6 = frame[
            POKEMON_POSITIONS[5][0] : POKEMON_POSITIONS[5][1],
            YOUR_PRE_POKEMON_POSITION[0] : YOUR_PRE_POKEMON_POSITION[1],
        ]
        your_pokemons = [
            your_pokemon_1,
            your_pokemon_2,
            your_pokemon_3,
            your_pokemon_4,
            your_pokemon_5,
            your_pokemon_6,
        ]

        return your_pokemons, opponent_pokemons

    def extract_pre_battle_pokemons(self, frame):
        """
        対戦前のポケモンを抽出する
        """
        is_exist_unknown_pokemon = False
        your_pokemons, opponent_pokemons = self._get_pokemons(frame)

        is_exist_unknown_pokemon_list = []
        # search by template matching
        your_pokemon_names = []
        for pokemon_image in your_pokemons:
            (
                pokemon_name,
                _is_exist_unknown_pokemon,
            ) = self._search_pokemon_by_transformers(pokemon_image)
            is_exist_unknown_pokemon_list.append(_is_exist_unknown_pokemon)
            your_pokemon_names.append(pokemon_name)

        opponent_pokemon_names = []
        for pokemon_image in opponent_pokemons:
            (
                pokemon_name,
                _is_exist_unknown_pokemon,
            ) = self._search_pokemon_by_transformers(pokemon_image)
            is_exist_unknown_pokemon_list.append(_is_exist_unknown_pokemon)
            opponent_pokemon_names.append(pokemon_name)

        # True を一つでも含んでいたら
        if is_exist_unknown_pokemon_list.count(True) > 0:
            is_exist_unknown_pokemon = True

        return your_pokemon_names, opponent_pokemon_names, is_exist_unknown_pokemon
