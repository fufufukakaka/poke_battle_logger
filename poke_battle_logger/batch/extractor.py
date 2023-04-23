import glob
import re
from typing import List

import cv2
import editdistance
import pytesseract

from config.config import (
    FIRST_RANKING_NUMBER_WINDOW,
    MESSAGE_WINDOW,
    OPPONENT_POKEMON_NAME_WINDOW,
    POKEMON_SELECT_NUMBER_WINDOW1,
    POKEMON_SELECT_NUMBER_WINDOW2,
    POKEMON_SELECT_NUMBER_WINDOW3,
    POKEMON_SELECT_NUMBER_WINDOW4,
    POKEMON_SELECT_NUMBER_WINDOW5,
    POKEMON_SELECT_NUMBER_WINDOW6,
    POKEMON_SELECT_WINDOW_THRESHOLD_VALUE,
    RANKING_NUMBER_WINDOW,
    TEMPLATE_MATCHING_THRESHOLD,
    WIN_LOST_WINDOW,
    WIN_OR_LOST_TEMPLATE_MATCHING_THRESHOLD,
    YOUR_POKEMON_NAME_WINDOW,
)
from poke_battle_logger.batch.pokemon_name_window_extractor import (
    EDIT_DISTANCE_THRESHOLD,
    PokemonNameWindowExtractor,
)

pytesseract.pytesseract.tesseract_cmd = r"/opt/brew/bin/tesseract"


class Extractor:
    """
    対戦中でのポケモン検出及びその他細々した検出を行う

    TODO: やっていることが増えすぎたので、いずれ複数の小さなクラスに分割する
    """

    def __init__(self, lang: str = "en") -> None:
        self.lang = lang
        self.pokemon_name_window_extractor = PokemonNameWindowExtractor()
        (
            self.win_window_template,
            self.lost_window_template,
        ) = self._setup_win_lost_window_templates()
        (
            self.first_template,
            self.second_template,
            self.third_template,
        ) = self._setup_pokemon_select_window_templates()
        self.message_window_templates = self._setup_message_window_templates()

    def _setup_pokemon_select_window_templates(self):
        if self.lang == "en":
            first_template = cv2.imread(
                "template_images/general_templates/first.png", 0
            )
            second_template = cv2.imread(
                "template_images/general_templates/second.png", 0
            )
            third_template = cv2.imread(
                "template_images/general_templates/third.png", 0
            )
            self.order_str = ["First", "Second", "Third"]
        elif self.lang == "ja":
            first_template = cv2.imread(
                "template_images/japanese_general_templates/first.png", 0
            )
            second_template = cv2.imread(
                "template_images/japanese_general_templates/second.png", 0
            )
            third_template = cv2.imread(
                "template_images/japanese_general_templates/third.png", 0
            )
            self.order_str = ["1番目", "2番目", "3番目"]
        else:
            raise ValueError("lang must be en or ja")

        return first_template, second_template, third_template

    def _setup_win_lost_window_templates(self):
        if self.lang == "en":
            win_window_template = cv2.imread(
                "template_images/general_templates/win.png", 0
            )
            lost_window_template = cv2.imread(
                "template_images/general_templates/lost.png", 0
            )
        elif self.lang == "ja":
            win_window_template = cv2.imread(
                "template_images/japanese_general_templates/win.png", 0
            )
            lost_window_template = cv2.imread(
                "template_images/japanese_general_templates/lost.png", 0
            )
        else:
            raise ValueError("lang must be en or ja")

        return win_window_template, lost_window_template

    def _setup_message_window_templates(self):
        message_window_template_paths = glob.glob(
            "template_images/message_templates/*.png"
        )
        message_window_templates = {}
        for path in message_window_template_paths:
            _image = cv2.imread(path, 0)
            threshold_value = 200
            max_value = 255
            _, thresh = cv2.threshold(
                _image, threshold_value, max_value, cv2.THRESH_BINARY
            )
            message_window_templates[path.split("/")[-1].split(".")[0]] = thresh
        return message_window_templates

    def _get_pokemon_name_window(self, frame):
        your_pokemon_name_window = frame[
            YOUR_POKEMON_NAME_WINDOW[0] : YOUR_POKEMON_NAME_WINDOW[1],
            YOUR_POKEMON_NAME_WINDOW[2] : YOUR_POKEMON_NAME_WINDOW[3],
        ]
        opponent_pokemon_name_window = frame[
            OPPONENT_POKEMON_NAME_WINDOW[0] : OPPONENT_POKEMON_NAME_WINDOW[1],
            OPPONENT_POKEMON_NAME_WINDOW[2] : OPPONENT_POKEMON_NAME_WINDOW[3],
        ]

        return your_pokemon_name_window, opponent_pokemon_name_window

    def _search_pokemon_select_window_by_template_matching(
        self,
        select1_window,
        select2_window,
        select3_window,
        select4_window,
        select5_window,
        select6_window,
    ) -> List[int]:
        """
        テンプレートマッチングで、ポケモンの選出順を検出する

        select{i}_window に対して、 first_template・second_template・third_template との
        テンプレートマッチングを行い、最もスコアが高いものを選出順として返す
        """

        pokemon_select_order_score = []

        for i, template in enumerate(
            [self.first_template, self.second_template, self.third_template]
        ):
            for k, window in enumerate(
                [
                    select1_window,
                    select2_window,
                    select3_window,
                    select4_window,
                    select5_window,
                    select6_window,
                ]
            ):
                threshold_value = POKEMON_SELECT_WINDOW_THRESHOLD_VALUE
                max_value = 255
                _, window2 = cv2.threshold(
                    window, threshold_value, max_value, cv2.THRESH_BINARY
                )
                if self.lang == "ja":
                    _recognized_order_str = pytesseract.image_to_string(
                        window2, lang="jpn", config="--psm 6"
                    )
                elif self.lang == "en":
                    _recognized_order_str = pytesseract.image_to_string(
                        window2, lang="eng", config="--psm 6"
                    )
                else:
                    raise ValueError("lang must be en or ja")
                _recognized_order_str = re.sub(r'[^\w]', '', _recognized_order_str)

                _order_str = self.order_str[i]
                ed_score = editdistance.eval(_recognized_order_str, _order_str) / (
                    max(len(_recognized_order_str), len(_order_str)) * 1.00
                )
                res = cv2.matchTemplate(window, template, cv2.TM_CCOEFF_NORMED)
                score = cv2.minMaxLoc(res)[1]
                if (
                    ed_score == 0 or (score > TEMPLATE_MATCHING_THRESHOLD and ed_score <= EDIT_DISTANCE_THRESHOLD)
                ):
                    pokemon_select_order_score.append([k, i, score])

        pokemon_select_order: List[int] = []
        for i in range(3):
            pokemon_select_order.append(
                max(
                    [score for score in pokemon_select_order_score if score[1] == i],
                    key=lambda x: x[2],
                )[0]
            )
        return pokemon_select_order

    def _search_win_or_lost_by_template_matching(self, frame) -> str:
        """
        テンプレートマッチングで勝敗を検出する
        """
        win_lost_image = cv2.cvtColor(
            frame[
                WIN_LOST_WINDOW[0] : WIN_LOST_WINDOW[1],
                WIN_LOST_WINDOW[2] : WIN_LOST_WINDOW[3],
            ],
            cv2.COLOR_BGR2GRAY,
        )
        win_res = cv2.matchTemplate(
            win_lost_image, self.win_window_template, cv2.TM_CCOEFF_NORMED
        )
        win_score = cv2.minMaxLoc(win_res)[1]

        lost_res = cv2.matchTemplate(
            win_lost_image, self.lost_window_template, cv2.TM_CCOEFF_NORMED
        )
        lost_score = cv2.minMaxLoc(lost_res)[1]

        if win_score >= WIN_OR_LOST_TEMPLATE_MATCHING_THRESHOLD:
            return "win"
        elif lost_score >= WIN_OR_LOST_TEMPLATE_MATCHING_THRESHOLD:
            return "lose"
        else:
            return "unknown"

    def extract_pokemon_select_numbers(self, frame):
        """
        ポケモンの選択順をパターンマッチングで抽出する
        順番を返す e.g. -> [5,6,4]
        """

        # search by template matching

        select1_window = cv2.cvtColor(
            frame[
                POKEMON_SELECT_NUMBER_WINDOW1[0] : POKEMON_SELECT_NUMBER_WINDOW1[1],
                POKEMON_SELECT_NUMBER_WINDOW1[2] : POKEMON_SELECT_NUMBER_WINDOW1[3],
            ],
            cv2.COLOR_BGR2GRAY,
        )
        select2_window = cv2.cvtColor(
            frame[
                POKEMON_SELECT_NUMBER_WINDOW2[0] : POKEMON_SELECT_NUMBER_WINDOW2[1],
                POKEMON_SELECT_NUMBER_WINDOW2[2] : POKEMON_SELECT_NUMBER_WINDOW2[3],
            ],
            cv2.COLOR_BGR2GRAY,
        )
        select3_window = cv2.cvtColor(
            frame[
                POKEMON_SELECT_NUMBER_WINDOW3[0] : POKEMON_SELECT_NUMBER_WINDOW3[1],
                POKEMON_SELECT_NUMBER_WINDOW3[2] : POKEMON_SELECT_NUMBER_WINDOW3[3],
            ],
            cv2.COLOR_BGR2GRAY,
        )
        select4_window = cv2.cvtColor(
            frame[
                POKEMON_SELECT_NUMBER_WINDOW4[0] : POKEMON_SELECT_NUMBER_WINDOW4[1],
                POKEMON_SELECT_NUMBER_WINDOW4[2] : POKEMON_SELECT_NUMBER_WINDOW4[3],
            ],
            cv2.COLOR_BGR2GRAY,
        )
        select5_window = cv2.cvtColor(
            frame[
                POKEMON_SELECT_NUMBER_WINDOW5[0] : POKEMON_SELECT_NUMBER_WINDOW5[1],
                POKEMON_SELECT_NUMBER_WINDOW5[2] : POKEMON_SELECT_NUMBER_WINDOW5[3],
            ],
            cv2.COLOR_BGR2GRAY,
        )
        select6_window = cv2.cvtColor(
            frame[
                POKEMON_SELECT_NUMBER_WINDOW6[0] : POKEMON_SELECT_NUMBER_WINDOW6[1],
                POKEMON_SELECT_NUMBER_WINDOW6[2] : POKEMON_SELECT_NUMBER_WINDOW6[3],
            ],
            cv2.COLOR_BGR2GRAY,
        )
        pokemon_select_number = self._search_pokemon_select_window_by_template_matching(
            select1_window,
            select2_window,
            select3_window,
            select4_window,
            select5_window,
            select6_window,
        )

        return pokemon_select_number

    def extract_pokemon_name_in_battle(self, frame):
        """
        対戦中のポケモン名をパターンマッチングで抽出する

        frames: 対戦中の名前が表示されているフレーム画像
        """
        is_exist_unknown_pokemon = False

        (
            your_pokemon_name_window,
            opponent_pokemon_name_window,
        ) = self._get_pokemon_name_window(frame)
        (
            your_pokemon_name,
            is_exist_unknown_pokemon1,
        ) = self.pokemon_name_window_extractor.extract_pokemon_name_in_battle(
            your_pokemon_name_window
        )
        (
            opponent_pokemon_name,
            is_exist_unknown_pokemon2,
        ) = self.pokemon_name_window_extractor.extract_pokemon_name_in_battle(
            opponent_pokemon_name_window
        )

        if is_exist_unknown_pokemon1 or is_exist_unknown_pokemon2:
            is_exist_unknown_pokemon = True

        return your_pokemon_name, opponent_pokemon_name, is_exist_unknown_pokemon

    def extract_win_or_lost(self, frame):
        """
        勝敗をパターンマッチングで抽出する
        """

        result = self._search_win_or_lost_by_template_matching(frame)
        return result

    def _detect_rank_number(self, image):
        """Detects text in the file."""
        if self.lang == "en":
            _lang = "eng"
        elif self.lang == "ja":
            _lang = "jpn"
        else:
            raise ValueError("lang must be en or ja")
        text = pytesseract.image_to_string(image, lang=_lang, config="--psm 6")

        # 数字部分だけを取り出す
        _rank_text = text.split("No. ")[-1]
        _rank = int(re.sub(r"\D", "", _rank_text))
        return _rank

    def _recognize_message(self, image):
        """Detects text in the file."""
        text = pytesseract.image_to_string(image, lang="eng+jpn", config="--psm 6")

        return text.replace("\n", "")

    def extract_first_rank_number(self, frame):
        """
        (開始時の)ランクをOCRで抽出する
        """

        rank_frame_window = frame[
            FIRST_RANKING_NUMBER_WINDOW[0] : FIRST_RANKING_NUMBER_WINDOW[1],
            FIRST_RANKING_NUMBER_WINDOW[2] : FIRST_RANKING_NUMBER_WINDOW[3],
        ]
        gray = cv2.cvtColor(rank_frame_window, cv2.COLOR_BGR2GRAY)
        threshold_value = 160
        max_value = 255
        _, thresh = cv2.threshold(gray, threshold_value, max_value, cv2.THRESH_BINARY)
        rank_number = self._detect_rank_number(thresh)
        return rank_number

    def extract_rank_number(self, frame):
        """
        ランクをOCRで抽出する
        """

        rank_frame_window = frame[
            RANKING_NUMBER_WINDOW[0] : RANKING_NUMBER_WINDOW[1],
            RANKING_NUMBER_WINDOW[2] : RANKING_NUMBER_WINDOW[3],
        ]
        gray = cv2.cvtColor(rank_frame_window, cv2.COLOR_BGR2GRAY)
        threshold_value = 160
        max_value = 255
        _, thresh = cv2.threshold(gray, threshold_value, max_value, cv2.THRESH_BINARY)
        rank_number = self._detect_rank_number(thresh)
        return rank_number

    def extract_message(self, frame):
        """
        メッセージをOCRで認識する
        """

        message_frame_window = frame[
            MESSAGE_WINDOW[0] : MESSAGE_WINDOW[1],
            MESSAGE_WINDOW[2] : MESSAGE_WINDOW[3],
        ]
        gray = cv2.cvtColor(message_frame_window, cv2.COLOR_BGR2GRAY)
        threshold_value = 200
        max_value = 255
        _, thresh = cv2.threshold(gray, threshold_value, max_value, cv2.THRESH_BINARY)
        white_pixels = cv2.countNonZero(thresh)
        # 誤って検出したメッセージウィンドウでないフレームを除外する
        if white_pixels > 10000:
            return None

        message = self._recognize_message(thresh)
        return message
