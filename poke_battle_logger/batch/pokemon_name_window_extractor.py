import collections
import glob
import re
import time
import unicodedata
from typing import List, Optional, Tuple

import cv2
import editdistance
import numpy as np
import pandas as pd
import pytesseract

from config.config import (
    POKEMON_NAME_WINDOW_THRESHOLD_VALUE,
    POKEMON_TEMPLATE_MATCHING_THRESHOLD,
)

EDIT_DISTANCE_THRESHOLD = 0.5


class PokemonNameWindowExtractor:
    """
    対戦中のウィンドウからポケモンの名前を抽出するクラス
    """

    def __init__(self) -> None:
        self.tesseract_candidate_langs = [
            "chi_sim",
            "chi_tra",
            "eng",
            "fra",
            "ita",
            "jpn",
            "kor",
            "spa",
            "deu",
        ]
        self._setup_multi_lang_list()
        self.battle_pokemon_name_window_templates = (
            self._setup_battle_pokemon_name_window_templates()
        )
        self.non_CJK_patterns = re.compile(
            "[^"
            "\U00003040-\U0000309F"  # Hiragana
            "\U000030A0-\U000030FF"  # Katakana
            "\U0000FF65-\U0000FF9F"  # Half width Katakana
            "\U0000FF10-\U0000FF19"  # Full width digits
            "\U0000FF21-\U0000FF3A"  # Full width Upper case Alphabets
            "\U0000FF41-\U0000FF5A"  # Full width Lower case Alphabets
            "\U00000030-\U00000039"  # Half width digits
            "\U00000041-\U0000005A"  # Half width Upper case Alphabets
            "\U00000061-\U0000007A"  # Half width Lower case Alphabets
            "\U00003190-\U0000319F"  # Kanbun
            "\U00004E00-\U00009FFF"  # CJK unified ideographs. kanjis
            "]+",
            flags=re.UNICODE,
        )

    def _setup_multi_lang_list(self) -> None:
        multi_lang_names = pd.read_csv("data/pokemon_name_multi_language.csv")
        self.ja_list = multi_lang_names["ja"].values.tolist()
        self.en_list = multi_lang_names["en"].values.tolist()
        self.fr_list = multi_lang_names["fr"].values.tolist()
        self.de_list = multi_lang_names["de"].values.tolist()
        self.es_list = multi_lang_names["es"].values.tolist()
        self.it_list = multi_lang_names["it"].values.tolist()
        self.ko_list = multi_lang_names["ko"].values.tolist()
        self.zh_HK_list = multi_lang_names["zh_HK"].values.tolist()
        self.zh_list = multi_lang_names["zh"].values.tolist()

    def _setup_battle_pokemon_name_window_templates(self):
        battle_pokemon_name_window_template_paths = glob.glob(
            "template_images/labeled_pokemon_name_window_templates/*.png"
        )
        battle_pokemon_name_window_templates = {}
        for path in battle_pokemon_name_window_template_paths:
            _gray_image = cv2.imread(path, 0)
            battle_pokemon_name_window_templates[
                path.split("/")[-1].split(".")[0]
            ] = _gray_image
        return battle_pokemon_name_window_templates

    def _search_name_window_by_template_matching(
        self, gray_name_window: np.ndarray, pokemon_name_window_image: np.ndarray
    ) -> Tuple[str, bool]:
        """
        テンプレートマッチングでポケモン名ウィンドウを検出する
        """
        score_results = {}
        for pokemon_name, template in self.battle_pokemon_name_window_templates.items():
            res = cv2.matchTemplate(gray_name_window, template, cv2.TM_CCOEFF_NORMED)
            score = cv2.minMaxLoc(res)[1]
            if score >= POKEMON_TEMPLATE_MATCHING_THRESHOLD:
                score_results[pokemon_name] = score
        if len(score_results) == 0:
            # save image for annotation(name is timestamp)
            cv2.imwrite(
                "template_images/unknown_pokemon_name_window_templates/"
                + str(time.time())
                + ".png",
                pokemon_name_window_image,
            )
            return "unknown_pokemon", True
        return max(score_results, key=score_results.get), False

    def _search_name_by_edit_distance(
        self, name_list: List[str], target: str
    ) -> Optional[str]:
        target = target.replace("\n", "").replace(" ", "")
        scores = {}
        for idx, _name in enumerate(name_list):
            _score = editdistance.eval(target, _name) / (
                max(len(_name), len(target)) * 1.00
            )
            if _score < EDIT_DISTANCE_THRESHOLD:
                scores[self.ja_list[idx]] = _score
        if len(scores) == 0:
            return None
        min_score_name = min(scores, key=scores.get)
        return min_score_name

    def _normalize_japanese_ocr_name(self, text: str) -> str:
        """
        OCRで読み取った日本語の名前から特殊文字を削除する
        """
        return self.non_CJK_patterns.sub(r"", text)

    def extract_pokemon_name_in_battle(
        self, name_window: np.ndarray
    ) -> Tuple[str, bool]:
        threshold_value = POKEMON_NAME_WINDOW_THRESHOLD_VALUE
        max_value = 255
        gray_name_window = cv2.cvtColor(name_window, cv2.COLOR_RGB2GRAY)
        _, name_window2 = cv2.threshold(
            gray_name_window, threshold_value, max_value, cv2.THRESH_BINARY
        )
        results = []
        _name_results = []
        for _lang in self.tesseract_candidate_langs:
            _name = pytesseract.image_to_string(
                name_window2, lang=_lang, config="--psm 6"
            )
            if _lang == "chi_sim":
                _name_results.append(_name)
                results.append(self._search_name_by_edit_distance(self.zh_list, _name))
            elif _lang == "chi_tra":
                _name_results.append(_name)
                results.append(
                    self._search_name_by_edit_distance(self.zh_HK_list, _name)
                )
            elif _lang == "eng":
                _name_results.append(_name)
                results.append(self._search_name_by_edit_distance(self.en_list, _name))
            elif _lang == "fra":
                _name_results.append(_name)
                results.append(self._search_name_by_edit_distance(self.fr_list, _name))
            elif _lang == "jpn":
                _name_results.append(self._normalize_japanese_ocr_name(_name))
                results.append(
                    self._search_name_by_edit_distance(
                        self.ja_list, self._normalize_japanese_ocr_name(_name)
                    )
                )
            elif _lang == "kor":
                _name_results.append(_name)
                results.append(self._search_name_by_edit_distance(self.ko_list, _name))
            elif _lang == "spa":
                _name_results.append(_name)
                results.append(self._search_name_by_edit_distance(self.es_list, _name))
            elif _lang == "deu":
                _name_results.append(_name)
                results.append(self._search_name_by_edit_distance(self.de_list, _name))
            else:
                continue
        results_exclude_None = [v for v in results if v is not None]
        if len(results_exclude_None) > 0:
            _counter = collections.Counter([v for v in results if v is not None])
            _most_common_name = _counter.most_common()
            _is_unknown = False
            return _most_common_name[0][0], _is_unknown
        else:
            # search by template matching
            _name, _is_unknown = self._search_name_window_by_template_matching(
                gray_name_window, name_window
            )
            return _name, _is_unknown
