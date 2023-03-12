import uuid
from datetime import datetime, timedelta

from pytube import YouTube
from pytube.exceptions import RegexMatchError
from pytube.helpers import regex_search


class DataBuilder:
    """
    データを整形するクラス
    """

    def __init__(
        self,
        video_id,
        battle_start_end_frame_numbers,
        battle_pokemons,
        pre_battle_pokemons,
        pokemon_select_order,
        rank_numbers,
        messages,
        win_or_lost,
    ):
        self.video_id = video_id
        self.battle_start_end_frame_numbers = battle_start_end_frame_numbers
        self.battle_pokemons = battle_pokemons
        self.pre_battle_pokemons = pre_battle_pokemons
        self.pokemon_select_order = pokemon_select_order
        self.rank_numbers = rank_numbers
        self.messages = messages
        self.win_or_lost = win_or_lost

    def _publish_date(self, watch_html: str):
        """https://github.com/pytube/pytube/issues/1269

        Extract publish date
        :param str watch_html:
            The html contents of the watch page.
        :rtype: str
        :returns:
            Publish date of the video.
        """
        # Check if isLiveBroadcast to get Correct UTC Publish Date +00:00
        try:
            result = regex_search(
                r"(?<=itemprop=\"startDate\" content=\")\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}",
                watch_html,
                group=0,
            )
            return datetime.strptime(result, "%Y-%m-%dT%H:%M:%S")
        except RegexMatchError:
            try:
                result = regex_search(
                    r"(?<=itemprop=\"datePublished\" content=\")", watch_html, group=0
                )
                return datetime.strptime(result, "%Y-%m-%d")
            except RegexMatchError:
                return None

    def _get_start_time(self, video_id, start_frame_number):
        yt = YouTube(f"http://youtube.com/watch?v={video_id}")
        second_from_frame_number = int(0.03 * start_frame_number)

        # +9h は UTC to JST
        start_datetime = self._publish_date(yt.watch_html) + timedelta(
            seconds=second_from_frame_number, hours=9
        )
        return start_datetime.strftime("%Y-%m-%d %H:%M:%S")

    def _get_battle_id(self, start_datetime):
        return str(uuid.uuid5(uuid.uuid1(), start_datetime))

    def _compress_battle_pokemons(self):
        compressed_battle_pokemons = []
        for start_frame, end_frame in self.battle_start_end_frame_numbers:
            _battle_pokemons = []
            for b_pokemons in self.battle_pokemons:
                _frame = b_pokemons["frame_number"]
                if start_frame < _frame and end_frame > _frame:
                    modified_b_pokemons = {
                        "frame_number": _frame,
                        "your_pokemon_name": b_pokemons["your_pokemon_name"].split("_")[
                            0
                        ],
                        "opponent_pokemon_name": b_pokemons[
                            "opponent_pokemon_name"
                        ].split("_")[0],
                    }
                    _battle_pokemons.append(modified_b_pokemons)
            compressed_battle_pokemons.append(_battle_pokemons)
        self.compressed_battle_pokemons = compressed_battle_pokemons

        self.compressed_messages = []
        for start_frame, end_frame in self.battle_start_end_frame_numbers:
            _messages = []
            for frame, message in self.messages.items():
                if start_frame < frame and end_frame > frame:
                    message_dict = {
                        "frame_number": frame,
                        "message": message,
                    }
                    _messages.append(message_dict)
            self.compressed_messages.append(_messages)

    def _build_battle_pokemon_combinations(self):
        battle_pokemon_combinations = []
        for i, _battle_pokemons in enumerate(self.compressed_battle_pokemons):
            # team にいるロトムを見つける(ロトムは必ず1体しかいない)
            _pre_battle_opponent_pokemons = list(self.pre_battle_pokemons.values())[i][
                "opponent_pokemon_names"
            ]
            opponent_team_rotom_names = [
                v for v in _pre_battle_opponent_pokemons if "ロトム" in v
            ]
            opponent_team_rotom_name = "None"
            if len(opponent_team_rotom_names) == 1:
                opponent_team_rotom_name = opponent_team_rotom_names[0].split("_")[0]

            _pre_battle_your_pokemons = list(self.pre_battle_pokemons.values())[i][
                "your_pokemon_names"
            ]
            _pokemon_select_order = list(self.pokemon_select_order.values())[i]
            _battle_pokemon_your_combinations = []
            for _position in _pokemon_select_order:
                _battle_pokemon_your_combinations.append(
                    _pre_battle_your_pokemons[_position].split("_")[0]
                )

            _battle_pokemon_opponent_combinations = []
            for _b_p in _battle_pokemons:
                _opponent = _b_p["opponent_pokemon_name"]

                # ロトムなら修正する
                if _opponent == "ロトム":
                    _opponent = opponent_team_rotom_name

                if (
                    len(_battle_pokemon_opponent_combinations) < 3
                    and _opponent not in _battle_pokemon_opponent_combinations
                ):
                    _battle_pokemon_opponent_combinations.append(_opponent)

            if len(_battle_pokemon_opponent_combinations) < 3:
                # 3 になるように Unseen で埋める
                for _ in range(3 - len(_battle_pokemon_opponent_combinations)):
                    _battle_pokemon_opponent_combinations.append("Unseen")

            battle_pokemon_combinations.append(
                {
                    "you": _battle_pokemon_your_combinations,
                    "opponent": _battle_pokemon_opponent_combinations,
                }
            )
        self.battle_pokemon_combinations = battle_pokemon_combinations

    def _build_modified_win_or_lose(self):
        def determine_unknown_outcomes(win_or_lost, modified_win_or_lose_frames):
            for modified_frame, outcome in modified_win_or_lose_frames.items():
                closest_frame = min(win_or_lost, key=lambda x: abs(x - modified_frame))
                win_or_lost[closest_frame] = outcome
            return win_or_lost

        modified_win_or_lose_frames = {}
        rank_frames = list(self.rank_numbers.keys())
        for i in range(1, len(self.rank_numbers.values())):
            previous_rank = list(self.rank_numbers.values())[i - 1]
            next_rank = list(self.rank_numbers.values())[i]
            if previous_rank > next_rank:
                modified_win_or_lose_frames[rank_frames[i]] = "win"
            else:
                modified_win_or_lose_frames[rank_frames[i]] = "lose"
        self.filled_win_or_lost = determine_unknown_outcomes(
            self.win_or_lost, modified_win_or_lose_frames
        )

    def build(self):
        battle_ids = []
        battle_logs = []
        modified_pre_battle_pokemons = []
        modified_in_battle_pokemons = []
        modified_messages = []

        # setup
        self._compress_battle_pokemons()
        self._build_battle_pokemon_combinations()
        self._build_modified_win_or_lose()

        for i in range(len(self.battle_start_end_frame_numbers)):
            start_frame = self.battle_start_end_frame_numbers[i][0]
            created_at = self._get_start_time(self.video_id, start_frame)
            battle_id = self._get_battle_id(created_at)

            battle_ids.append(battle_id)

            # overview
            _log = {
                "battle_id": battle_id,
                "created_at": created_at,
                "win_or_lose": list(self.filled_win_or_lost.values())[i],
                "next_rank": list(self.rank_numbers.values())[i + 1],
                "your_team": ",".join(
                    [
                        v.split("_")[0]
                        for v in list(self.pre_battle_pokemons.values())[i][
                            "your_pokemon_names"
                        ]
                    ]
                ),
                "opponent_team": ",".join(
                    [
                        v.split("_")[0]
                        for v in list(self.pre_battle_pokemons.values())[i][
                            "opponent_pokemon_names"
                        ]
                    ]
                ),
                "your_pokemon_1": self.battle_pokemon_combinations[i]["you"][0],
                "your_pokemon_2": self.battle_pokemon_combinations[i]["you"][1],
                "your_pokemon_3": self.battle_pokemon_combinations[i]["you"][2],
                "opponent_pokemon_1": self.battle_pokemon_combinations[i]["opponent"][
                    0
                ],
                "opponent_pokemon_2": self.battle_pokemon_combinations[i]["opponent"][
                    1
                ],
                "opponent_pokemon_3": self.battle_pokemon_combinations[i]["opponent"][
                    2
                ],
                "video": f"http://youtube.com/watch?v={self.video_id}",
            }
            battle_logs.append(_log)

            # pre_battle
            for pokemon in [
                v.split("_")[0]
                for v in list(self.pre_battle_pokemons.values())[i][
                    "your_pokemon_names"
                ]
            ]:
                modified_pre_battle_pokemons.append(
                    {"battle_id": battle_id, "team": "you", "pokemon_name": pokemon}
                )
            for pokemon in [
                v.split("_")[0]
                for v in list(self.pre_battle_pokemons.values())[i][
                    "opponent_pokemon_names"
                ]
            ]:
                modified_pre_battle_pokemons.append(
                    {
                        "battle_id": battle_id,
                        "team": "opponent",
                        "pokemon_name": pokemon,
                    }
                )

            # in-battle
            in_battle_log = self.compressed_battle_pokemons[i]
            for i, _in_battle_log in enumerate(in_battle_log):
                modified_in_battle_pokemons.append(
                    {
                        "battle_id": battle_id,
                        "turn": i + 1,
                        "frame_number": _in_battle_log["frame_number"],
                        "your_pokemon_name": _in_battle_log["your_pokemon_name"],
                        "opponent_pokemon_name": _in_battle_log[
                            "opponent_pokemon_name"
                        ],
                    }
                )

            # messages
            message_log = self.compressed_messages[i]
            for _message_log in message_log:
                modified_messages.append(
                    {
                        "battle_id": battle_id,
                        "frame": _message_log["frame_number"],
                        "message": _message_log["message"],
                    }
                )

        return (
            battle_ids,
            battle_logs,
            modified_pre_battle_pokemons,
            modified_in_battle_pokemons,
            modified_messages,
        )
