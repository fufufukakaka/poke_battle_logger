import cv2

from config.config import (
    LEVEL_50_TEMPLATE_PATH,
    LEVEL_50_WINDOW,
    LOST_TEMPLATE_PATH,
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
)


class FrameDetector:
    def __init__(self) -> None:
        (
            self.gray_standing_by_template,
            self.gray_level_50_template,
            self.gray_ranking_template,
            self.gray_win_template,
            self.gray_lost_template,
            self.gray_done_template,
        ) = self.setup_templates()

    def setup_templates(self):
        standing_by_template = cv2.imread(STANDING_BY_TEMPLATE_PATH)
        gray_standing_by_template = cv2.cvtColor(
            standing_by_template, cv2.COLOR_RGB2GRAY
        )

        level_50_template = cv2.imread(LEVEL_50_TEMPLATE_PATH)
        gray_level_50_template = cv2.cvtColor(level_50_template, cv2.COLOR_RGB2GRAY)

        ranking_template = cv2.imread(RANKING_TEMPLATE_PATH)
        gray_ranking_template = cv2.cvtColor(ranking_template, cv2.COLOR_RGB2GRAY)

        win_template = cv2.imread(WIN_TEMPLATE_PATH)
        gray_win_template = cv2.cvtColor(win_template, cv2.COLOR_RGB2GRAY)

        lost_template = cv2.imread(LOST_TEMPLATE_PATH)
        gray_lost_template = cv2.cvtColor(lost_template, cv2.COLOR_RGB2GRAY)

        select_done_template = cv2.imread(SELECT_DONE_TEMPLATE_PATH)
        gray_select_done_template = cv2.cvtColor(
            select_done_template, cv2.COLOR_RGB2GRAY
        )

        return (
            gray_standing_by_template,
            gray_level_50_template,
            gray_ranking_template,
            gray_win_template,
            gray_lost_template,
            gray_select_done_template,
        )

    def is_standing_by_frame(self, frame):
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
        return cv2.minMaxLoc(result)[1] >= TEMPLATE_MATCHING_THRESHOLD

    def is_level_50_frame(self, frame):
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
        return cv2.minMaxLoc(result)[1] >= TEMPLATE_MATCHING_THRESHOLD

    def is_ranking_frame(self, frame):
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
        return cv2.minMaxLoc(result)[1] >= TEMPLATE_MATCHING_THRESHOLD

    def is_win_or_lost_frame(self, frame) -> bool:
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
        return (
            cv2.minMaxLoc(result_win)[1] >= WIN_OR_LOST_TEMPLATE_MATCHING_THRESHOLD
            or cv2.minMaxLoc(result_lost)[1] >= WIN_OR_LOST_TEMPLATE_MATCHING_THRESHOLD
        )

    def is_select_done_frame(self, frame):
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
        return cv2.minMaxLoc(result)[1] >= TEMPLATE_MATCHING_THRESHOLD
