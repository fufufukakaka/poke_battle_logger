from typing import Tuple

import cv2
import numpy as np

from config.config import (
    FIRST_RANKING_WINDOW,
    JAPANESE_LEVEL_50_TEMPLATE_PATH,
    JAPANESE_LOST_TEMPLATE_PATH,
    JAPANESE_RANKING_TEMPLATE_PATH,
    JAPANESE_SELECT_DONE_TEMPLATE_PATH,
    JAPANESE_STANDING_BY_TEMPLATE_PATH,
    JAPANESE_WIN_TEMPLATE_PATH,
    LEVEL_50_TEMPLATE_PATH,
    LEVEL_50_WINDOW,
    LOST_TEMPLATE_PATH,
    POKEMON_MESSAGE_WINDOW,
    POKEMON_MESSAGE_WINDOW_MAX_WHITE_PIXELS,
    POKEMON_MESSAGE_WINDOW_MIN_WHITE_PIXELS,
    POKEMON_MESSAGE_WINDOW_THRESHOLD_VALUE,
    POKEMON_SELECT_DONE_WINDOW,
    RANKING_TEMPLATE_PATH,
    RANKING_WINDOW,
    SELECT_DONE_TEMPLATE_PATH,
    STANDING_BY_TEMPLATE_PATH,
    STANDING_BY_WINDOW,
    TEMPLATE_MATCHING_THRESHOLD,
    WIN_LOST_WINDOW,
    WIN_OR_LOST_TEMPLATE_MATCHING_THRESHOLD,
    WIN_TEMPLATE_PATH,
    MOVE_ANKER_POSITION,
    MOVE_ANKER_TEMPLATE,
    POKEMON_SELECTION_TEMPLATE_PATH,
    POKEMON_SELECTION_ICON,
)


class FrameDetector:
    def __init__(self, lang: str = "en") -> None:
        self.lang = lang
        (
            self.gray_standing_by_template,
            self.gray_level_50_template,
            self.gray_ranking_template,
            self.gray_win_template,
            self.gray_lost_template,
            self.gray_done_template,
            self.gray_move_anker_template,
        ) = self.setup_templates()

    def setup_templates(
        self,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        if self.lang == "en":
            gray_standing_by_template = cv2.imread(STANDING_BY_TEMPLATE_PATH, 0)
            gray_level_50_template = cv2.imread(LEVEL_50_TEMPLATE_PATH, 0)
            gray_ranking_template = cv2.imread(RANKING_TEMPLATE_PATH, 0)
            gray_win_template = cv2.imread(WIN_TEMPLATE_PATH, 0)
            gray_lost_template = cv2.imread(LOST_TEMPLATE_PATH, 0)
            gray_select_done_template = cv2.imread(SELECT_DONE_TEMPLATE_PATH, 0)
            gray_move_anker_template = cv2.imread(MOVE_ANKER_TEMPLATE, 0)
            gray_pokemon_selection_template = cv2.imread(POKEMON_SELECTION_TEMPLATE_PATH, 0)
        elif self.lang == "ja":
            gray_standing_by_template = cv2.imread(
                JAPANESE_STANDING_BY_TEMPLATE_PATH, 0
            )
            gray_level_50_template = cv2.imread(JAPANESE_LEVEL_50_TEMPLATE_PATH, 0)
            gray_ranking_template = cv2.imread(JAPANESE_RANKING_TEMPLATE_PATH, 0)
            gray_win_template = cv2.imread(JAPANESE_WIN_TEMPLATE_PATH, 0)
            gray_lost_template = cv2.imread(JAPANESE_LOST_TEMPLATE_PATH, 0)
            gray_select_done_template = cv2.imread(
                JAPANESE_SELECT_DONE_TEMPLATE_PATH, 0
            )
            gray_move_anker_template = cv2.imread(MOVE_ANKER_TEMPLATE, 0)  # TODO: 日本語のテンプレート
            gray_pokemon_selection_template = cv2.imread(
                POKEMON_SELECTION_TEMPLATE_PATH, 0
            )
        else:
            raise ValueError("Invalid language")

        return (
            gray_standing_by_template,
            gray_level_50_template,
            gray_ranking_template,
            gray_win_template,
            gray_lost_template,
            gray_select_done_template,
            gray_move_anker_template,
            gray_pokemon_selection_template,
        )

    def is_standing_by_frame(self, frame: np.ndarray) -> bool:
        gray_standing_by_area = cv2.cvtColor(
            frame[
                STANDING_BY_WINDOW[0] : STANDING_BY_WINDOW[1],
                STANDING_BY_WINDOW[2] : STANDING_BY_WINDOW[3],
            ],
            cv2.COLOR_RGB2GRAY,
        )
        result = cv2.matchTemplate(
            gray_standing_by_area, self.gray_standing_by_template, cv2.TM_CCOEFF_NORMED
        )
        _result = cv2.minMaxLoc(result)[1] >= TEMPLATE_MATCHING_THRESHOLD
        return bool(_result)

    def is_level_50_frame(self, frame: np.ndarray) -> bool:
        gray_level_50_area = cv2.cvtColor(
            frame[
                LEVEL_50_WINDOW[0] : LEVEL_50_WINDOW[1],
                LEVEL_50_WINDOW[2] : LEVEL_50_WINDOW[3],
            ],
            cv2.COLOR_RGB2GRAY,
        )
        result = cv2.matchTemplate(
            gray_level_50_area, self.gray_level_50_template, cv2.TM_CCOEFF_NORMED
        )
        _, thresh = cv2.threshold(gray_level_50_area, 200, 255, cv2.THRESH_BINARY)
        _res = (
            cv2.countNonZero(thresh) > 100
            and cv2.minMaxLoc(result)[1] >= TEMPLATE_MATCHING_THRESHOLD
        )
        return bool(_res)

    def is_first_ranking_frame(self, frame: np.ndarray) -> bool:
        gray_ranking_area = cv2.cvtColor(
            frame[
                FIRST_RANKING_WINDOW[0] : FIRST_RANKING_WINDOW[1],
                FIRST_RANKING_WINDOW[2] : FIRST_RANKING_WINDOW[3],
            ],
            cv2.COLOR_RGB2GRAY,
        )
        result = cv2.matchTemplate(
            gray_ranking_area, self.gray_ranking_template, cv2.TM_CCOEFF_NORMED
        )
        _result = cv2.minMaxLoc(result)[1] >= TEMPLATE_MATCHING_THRESHOLD
        return bool(_result)

    def is_ranking_frame(self, frame: np.ndarray) -> bool:
        gray_ranking_area = cv2.cvtColor(
            frame[
                RANKING_WINDOW[0] : RANKING_WINDOW[1],
                RANKING_WINDOW[2] : RANKING_WINDOW[3],
            ],
            cv2.COLOR_RGB2GRAY,
        )
        result = cv2.matchTemplate(
            gray_ranking_area, self.gray_ranking_template, cv2.TM_CCOEFF_NORMED
        )
        _result = cv2.minMaxLoc(result)[1] >= TEMPLATE_MATCHING_THRESHOLD
        return bool(_result)

    def is_win_or_lost_frame(self, frame: np.ndarray) -> bool:
        gray_win_lost_area = cv2.cvtColor(
            frame[
                WIN_LOST_WINDOW[0] : WIN_LOST_WINDOW[1],
                WIN_LOST_WINDOW[2] : WIN_LOST_WINDOW[3],
            ],
            cv2.COLOR_RGB2GRAY,
        )
        result_win = cv2.matchTemplate(
            gray_win_lost_area, self.gray_win_template, cv2.TM_CCOEFF_NORMED
        )
        result_lost = cv2.matchTemplate(
            gray_win_lost_area, self.gray_lost_template, cv2.TM_CCOEFF_NORMED
        )
        _result = (
            cv2.minMaxLoc(result_win)[1] >= WIN_OR_LOST_TEMPLATE_MATCHING_THRESHOLD
            or cv2.minMaxLoc(result_lost)[1] >= WIN_OR_LOST_TEMPLATE_MATCHING_THRESHOLD
        )
        return bool(_result)

    def is_select_done_frame(self, frame: np.ndarray) -> bool:
        gray_select_done_area = cv2.cvtColor(
            frame[
                POKEMON_SELECT_DONE_WINDOW[0] : POKEMON_SELECT_DONE_WINDOW[1],
                POKEMON_SELECT_DONE_WINDOW[2] : POKEMON_SELECT_DONE_WINDOW[3],
            ],
            cv2.COLOR_RGB2GRAY,
        )
        result = cv2.matchTemplate(
            gray_select_done_area, self.gray_done_template, cv2.TM_CCOEFF_NORMED
        )
        _result = cv2.minMaxLoc(result)[1] >= TEMPLATE_MATCHING_THRESHOLD
        return bool(_result)

    def is_message_window_frame(self, frame: np.ndarray) -> bool:
        gray = cv2.cvtColor(
            frame[
                POKEMON_MESSAGE_WINDOW[0] : POKEMON_MESSAGE_WINDOW[1],
                POKEMON_MESSAGE_WINDOW[2] : POKEMON_MESSAGE_WINDOW[3],
            ],
            cv2.COLOR_BGR2GRAY,
        )
        max_value = 255
        _, thresh = cv2.threshold(
            gray, POKEMON_MESSAGE_WINDOW_THRESHOLD_VALUE, max_value, cv2.THRESH_BINARY
        )
        white_pixels = cv2.countNonZero(thresh)
        is_message = (
            white_pixels > POKEMON_MESSAGE_WINDOW_MIN_WHITE_PIXELS
            and white_pixels < POKEMON_MESSAGE_WINDOW_MAX_WHITE_PIXELS
        )

        mser = cv2.MSER.create()
        regions, _ = mser.detectRegions(thresh)
        is_exist_text = len(regions) >= 2
        _result = is_message & is_exist_text
        return bool(_result)

    def is_move_frame(self, frame: np.ndarray) -> bool:
        gray_move_anker_area = cv2.cvtColor(
            frame[
                MOVE_ANKER_POSITION[0] : MOVE_ANKER_POSITION[1],
                MOVE_ANKER_POSITION[2] : MOVE_ANKER_POSITION[3],
            ],
            cv2.COLOR_BGR2GRAY,
        )
        result = cv2.matchTemplate(
            gray_move_anker_area, self.gray_move_anker_template, cv2.TM_CCOEFF_NORMED
        )
        _result = cv2.minMaxLoc(result)[1] >= TEMPLATE_MATCHING_THRESHOLD
        return bool(_result)

    def is_pokemon_selection_frame(self, frame: np.ndarray) -> bool:
        gray_pokemon_selection_area = cv2.cvtColor(
            frame[
                POKEMON_SELECTION_ICON[0] : POKEMON_SELECTION_ICON[1],
                POKEMON_SELECTION_ICON[2] : POKEMON_SELECTION_ICON[3],
            ],
            cv2.COLOR_BGR2GRAY,
        )
        result = cv2.matchTemplate(
            gray_pokemon_selection_area,
            self.gray_pokemon_selection_template,
            cv2.TM_CCOEFF_NORMED,
        )
        _result = cv2.minMaxLoc(result)[1] >= TEMPLATE_MATCHING_THRESHOLD
        return bool(_result)
