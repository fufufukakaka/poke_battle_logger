import glob

import cv2

from config.config import (OPPONENT_PRE_POKEMON_POSITION, POKEMON_POSITIONS,
                           TEMPLATE_MATCHING_THRESHOLD, WIN_LOST_WINDOW,
                           YOUR_PRE_POKEMON_POSITION)


class PokemonExtractor:
    """
    6vs6 の見せ合い画面でのポケモン検出と
    対戦中でのポケモン検出を行う
    """

    def __init__(self):
        self.pre_battle_pokemon_templates = self._setup_pre_battle_pokemon_templates()
        self.battle_pokemon_name_window_templates = (
            self._setup_battle_pokemon_name_window_templates()
        )
        (
            self.win_window_template,
            self.lost_window_template,
        ) = self._setup_win_lost_window_templates()

    def _setup_win_lost_window_templates(self):
        win_window_template = (
            cv2.imread("template_images/general_templates/win.png", 0),
        )

        lost_window_template = (
            cv2.imread("template_images/general_templates/lost.png", 0),
        )

        return win_window_template, lost_window_template

    def _setup_pre_battle_pokemon_templates(self):
        pre_battle_pokemon_template_paths = glob.glob(
            "template_images/labeled_pokemon_templates/*.png"
        )
        pre_battle_pokemon_templates = {}
        for path in pre_battle_pokemon_template_paths:
            _gray_image = cv2.imread(path, 0)
            pre_battle_pokemon_templates[
                path.split("/")[-1].split(".")[0].split("_")[0]
            ] = _gray_image
        return pre_battle_pokemon_templates

    def _setup_battle_pokemon_name_window_templates(self):
        battle_pokemon_name_window_template_paths = glob.glob(
            "template_images/labeled_pokemon_name_window_templates/*.png"
        )
        battle_pokemon_name_window_templates = {}
        for path in battle_pokemon_name_window_template_paths:
            _gray_image = cv2.imread(path, 0)
            battle_pokemon_name_window_templates[
                path.split("/")[-1].split(".")[0].split("_")[0]
            ] = _gray_image
        return battle_pokemon_name_window_templates

    def _search_by_template_matching(self, pokemon_image) -> str:
        """
        テンプレートマッチングでポケモンを検出する
        """
        score_results = {}
        gray_pokemon_image = cv2.cvtColor(pokemon_image, cv2.COLOR_RGB2GRAY)

        for pokemon_name, template in self.pre_battle_pokemon_templates.items():
            res = cv2.matchTemplate(gray_pokemon_image, template, cv2.TM_CCOEFF_NORMED)
            score = cv2.minMaxLoc(res)[1]
            if score >= TEMPLATE_MATCHING_THRESHOLD:
                score_results[pokemon_name] = score
        if len(score_results) == 0:
            return "unknown_pokemon"
        return max(score_results, key=score_results.get)

    def _search_name_window_by_template_matching(self, pokemon_image) -> str:
        """
        テンプレートマッチングでポケモン名ウィンドウを検出する
        """
        score_results = {}
        gray_pokemon_image = cv2.cvtColor(pokemon_image, cv2.COLOR_RGB2GRAY)
        for pokemon_name, template in self.battle_pokemon_name_window_templates.items():
            res = cv2.matchTemplate(gray_pokemon_image, template, cv2.TM_CCOEFF_NORMED)
            score = cv2.minMaxLoc(res)[1]
            if score >= TEMPLATE_MATCHING_THRESHOLD:
                score_results[pokemon_name] = score
        if len(score_results) == 0:
            return "unknown_pokemon"
        return max(score_results, key=score_results.get)

    def _search_win_or_lost_by_template_matching(self, frame) -> str:
        """
        テンプレートマッチングで勝敗を検出する
        """
        win_lost_image = cv2.cvtColor(
            frame[
                WIN_LOST_WINDOW[0] : WIN_LOST_WINDOW[1],
                WIN_LOST_WINDOW[2] : WIN_LOST_WINDOW[3],
            ],
            cv2.COLOR_RGB2GRAY,
        )
        win_res = cv2.matchTemplate(
            win_lost_image, self.win_window_template, cv2.TM_CCOEFF_NORMED
        )
        win_score = cv2.minMaxLoc(win_res)[1]

        lost_res = cv2.matchTemplate(
            win_lost_image, self.lost_window_template, cv2.TM_CCOEFF_NORMED
        )
        lost_score = cv2.minMaxLoc(lost_res)[1]

        if win_score >= TEMPLATE_MATCHING_THRESHOLD:
            return "win"
        elif lost_score >= TEMPLATE_MATCHING_THRESHOLD:
            return "lost"
        else:
            return "unknown"

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

    # ポケモンの名前を切り取る
    def _get_pokemon_name_window(self, frame):
        your_pokemon_name_window = frame[575:615, 50:250]
        opponent_pokemon_name_window = frame[80:120, 950:1150]
        return your_pokemon_name_window, opponent_pokemon_name_window

    def extract_pre_battle_pokemons(self, frame):
        """
        対戦前のポケモンをパターンマッチングで抽出する
        """

        your_pokemons, opponent_pokemons = self._get_pokemons(frame)

        # search by template matching
        your_pokemon_names = []
        for pokemon_image in your_pokemons:
            pokemon_name = self._search_by_template_matching(pokemon_image)
            your_pokemon_names.append(pokemon_name)

        opponent_pokemon_names = []
        for pokemon_image in opponent_pokemons:
            pokemon_name = self._search_by_template_matching(pokemon_image)
            opponent_pokemon_names.append(pokemon_name)

        return your_pokemon_names, opponent_pokemon_names

    def extract_pokemon_name_in_battle(self, frame):
        """
        対戦中のポケモン名をパターンマッチングで抽出する

        frames: 対戦中の名前が表示されているフレーム画像
        """

        (
            your_pokemon_name_window,
            opponent_pokemon_name_window,
        ) = self._get_pokemon_name_window(frame)
        your_pokemon_name = self._search_name_window_by_template_matching(
            your_pokemon_name_window
        )
        opponent_pokemon_name = self._search_name_window_by_template_matching(
            opponent_pokemon_name_window
        )
        return your_pokemon_name, opponent_pokemon_name

    def extract_win_or_lost(self, frame):
        """
        勝敗をパターンマッチングで抽出する
        """

        win_or_lost_window = frame[
            WIN_LOST_WINDOW[0] : WIN_LOST_WINDOW[1],
            WIN_LOST_WINDOW[2] : WIN_LOST_WINDOW[3],
        ]
        result = self._search_win_or_lost_by_template_matching(win_or_lost_window)
        return result
