import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union, cast

from pytube import YouTube
from pytube.exceptions import RegexMatchError
from pytube.helpers import regex_search

from poke_battle_logger.types import (
    Battle,
    BattleLog,
    InBattlePokemon,
    Message,
    PreBattlePokemon,
)


class DataBuilder:
    """
    データを整形するクラス
    """

    def __init__(
        self,
        trainer_id: int,
        video_id: str,
        battle_start_end_frame_numbers: List[Tuple[int, int]],
        battle_pokemons: List[Dict[str, Union[str, int]]],
        pre_battle_pokemons: Dict[int, Dict[str, List[str]]],
        pokemon_select_order: Dict[int, List[int]],
        rank_numbers: Dict[int, int],
        messages: Dict[int, str],
        win_or_lost: Dict[int, str],
    ) -> None:
        self.trainer_id = trainer_id
        self.video_id = video_id
        self.battle_start_end_frame_numbers = battle_start_end_frame_numbers
        self.battle_pokemons = battle_pokemons
        self.pre_battle_pokemons = pre_battle_pokemons
        self.pokemon_select_order = pokemon_select_order
        self.rank_numbers = rank_numbers
        self.messages = messages
        self.win_or_lost = win_or_lost

    def _publish_date(self, watch_html: str) -> Optional[datetime]:
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

    def _get_start_time(
        self, video_id: str, start_frame_number: int
    ) -> Tuple[Optional[str], Optional[int]]:
        yt = YouTube(f"http://youtube.com/watch?v={video_id}")
        second_from_frame_number = int(start_frame_number / 30)  # FPS=30

        # +9h は UTC to JST
        _publish_date = self._publish_date(yt.watch_html)
        if _publish_date is None:
            return None, None
        start_datetime = _publish_date + timedelta(
            seconds=second_from_frame_number, hours=9
        )
        return start_datetime.strftime("%Y-%m-%d %H:%M:%S"), second_from_frame_number

    def _get_battle_id(self, start_datetime: str) -> str:
        return str(uuid.uuid5(uuid.uuid1(), start_datetime))

    def _compress_battle_pokemons(self) -> None:
        compressed_battle_pokemons = []
        for start_frame, end_frame in self.battle_start_end_frame_numbers:
            _battle_pokemons = []
            for b_pokemons in self.battle_pokemons:
                _frame = cast(int, b_pokemons["frame_number"])
                if start_frame < _frame and end_frame > _frame:
                    _your_pokemon_name = cast(str, b_pokemons["your_pokemon_name"])
                    _opponent_pokemon_name = cast(
                        str, b_pokemons["opponent_pokemon_name"]
                    )
                    modified_b_pokemons = {
                        "frame_number": _frame,
                        "your_pokemon_name": _your_pokemon_name.split("_")[0],
                        "opponent_pokemon_name": _opponent_pokemon_name.split("_")[0],
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

    def _build_battle_pokemon_combinations(self) -> None:
        battle_pokemon_combinations = []
        for i, _battle_pokemons in enumerate(self.compressed_battle_pokemons):
            _pre_battle_opponent_pokemons = list(self.pre_battle_pokemons.values())[i][
                "opponent_pokemon_names"
            ]

            # team にいるロトムを見つける(ロトムは必ず1体しかいない)
            opponent_team_rotom_names = [
                v for v in _pre_battle_opponent_pokemons if "ロトム" in v
            ]
            opponent_team_rotom_name = "ロトム"
            if len(opponent_team_rotom_names) == 1:
                opponent_team_rotom_name = opponent_team_rotom_names[0].split("_")[0]
            # 自チームについても同様に処理する
            your_team_rotom_names = [
                v
                for v in list(self.pre_battle_pokemons.values())[i][
                    "your_pokemon_names"
                ]
                if "ロトム" in v
            ]
            your_team_rotom_name = "ロトム"
            if len(your_team_rotom_names) == 1:
                your_team_rotom_name = your_team_rotom_names[0].split("_")[0]

            # team にいるケンタロスを見つける(ケンタロスは必ず1体しかいない)
            opponent_team_tauros_names = [
                v for v in _pre_battle_opponent_pokemons if "ケンタロス" in v
            ]
            opponent_team_tauros_name = "ケンタロス"
            if len(opponent_team_tauros_names) == 1:
                opponent_team_tauros_name = opponent_team_tauros_names[0].split("_")[0]
            # 自チームについても同様に処理する
            your_team_tauros_names = [
                v
                for v in list(self.pre_battle_pokemons.values())[i][
                    "your_pokemon_names"
                ]
                if "ケンタロス" in v
            ]
            your_team_tauros_name = "ケンタロス"
            if len(your_team_tauros_names) == 1:
                your_team_tauros_name = your_team_tauros_names[0].split("_")[0]

            _pre_battle_your_pokemons = list(self.pre_battle_pokemons.values())[i][
                "your_pokemon_names"
            ]
            _pokemon_select_order = list(self.pokemon_select_order.values())[i]
            _battle_pokemon_your_combinations = []
            for _position in _pokemon_select_order:
                _battle_pokemon_your_combinations.append(
                    _pre_battle_your_pokemons[_position].split("_")[0]
                )

            _battle_pokemon_opponent_combinations: List[str] = []
            for _b_p in _battle_pokemons:
                _your = cast(str, _b_p["your_pokemon_name"])
                _opponent = cast(str, _b_p["opponent_pokemon_name"])

                # ロトムなら修正する
                if _opponent == "ロトム":
                    _opponent = opponent_team_rotom_name
                if _your == "ロトム":
                    _your = your_team_rotom_name

                # ケンタロスなら修正する
                if _opponent == "ケンタロス":
                    _opponent = opponent_team_tauros_name
                if _your == "ケンタロス":
                    _your = your_team_tauros_name

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

    def _build_modified_win_or_lose(self) -> None:
        def determine_unknown_outcomes(
            win_or_lost: Dict[int, str], modified_win_or_lose_frames: Dict[int, str]
        ) -> Dict[int, str]:
            if len(win_or_lost) == 0:
                return modified_win_or_lose_frames
            for modified_frame, outcome in modified_win_or_lose_frames.items():
                closest_frame = min(win_or_lost, key=lambda x: abs(x - modified_frame))
                win_or_lost[closest_frame] = outcome
            return win_or_lost

        def trim_win_or_lost(
            win_or_lost: Dict[int, str],
            battle_start_end_frame_numbers: List[Tuple[int, int]],
        ) -> Dict[int, str]:
            new_win_or_lost = {}
            for start, end in battle_start_end_frame_numbers:
                for frame, outcome in win_or_lost.items():
                    if start <= frame <= end:
                        new_win_or_lost[frame] = outcome
            return new_win_or_lost

        self.modified_win_or_lose_frames_from_rank = {}
        rank_frames = list(self.rank_numbers.keys())
        for i in range(1, len(self.rank_numbers.values())):
            previous_rank = list(self.rank_numbers.values())[i - 1]
            next_rank = list(self.rank_numbers.values())[i]
            if previous_rank > next_rank:
                self.modified_win_or_lose_frames_from_rank[rank_frames[i]] = "win"
            else:
                self.modified_win_or_lose_frames_from_rank[rank_frames[i]] = "lose"

        _filled_win_or_lost = determine_unknown_outcomes(
            self.win_or_lost, self.modified_win_or_lose_frames_from_rank
        )
        self.filled_win_or_lost = trim_win_or_lost(
            _filled_win_or_lost, self.battle_start_end_frame_numbers
        )

    def build(
        self,
    ) -> Tuple[
        List[Battle],
        List[BattleLog],
        List[PreBattlePokemon],
        List[InBattlePokemon],
        List[Message],
    ]:
        battles: List[Battle] = []
        battle_logs: List[BattleLog] = []
        modified_pre_battle_pokemons: List[PreBattlePokemon] = []
        modified_in_battle_pokemons: List[InBattlePokemon] = []
        modified_messages: List[Message] = []

        # setup
        self._compress_battle_pokemons()
        self._build_battle_pokemon_combinations()
        self._build_modified_win_or_lose()

        # filled_win_or_lost 上に unknown がある場合は abort する
        if "unknown" in self.filled_win_or_lost.values():
            raise Exception("unknown win or lost")

        for i in range(len(self.battle_start_end_frame_numbers)):
            start_frame = self.battle_start_end_frame_numbers[i][0]
            created_at, second_from_frame_number = self._get_start_time(
                self.video_id, start_frame
            )
            if created_at is None:
                continue
            battle_id = self._get_battle_id(created_at)

            battles.append(
                Battle(
                    battle_id=battle_id,
                    trainer_id=self.trainer_id,
                )
            )

            # messages
            message_log = self.compressed_messages[i]
            for _message_log in message_log:
                modified_messages.append(
                    Message(
                        battle_id=battle_id,
                        frame_number=cast(int, _message_log["frame_number"]),
                        message=cast(str, _message_log["message"]),
                    )
                )

            # overview
            if (
                len(self.rank_numbers.values())
                == len(self.battle_start_end_frame_numbers) + 1
            ):
                _next_rank = list(self.rank_numbers.values())[i + 1]
            else:
                _next_rank = list(self.rank_numbers.values())[i]

            # 長さが合うものを使う
            # 最初に rank が表示されない時
            if len(self.filled_win_or_lost) == len(self.rank_numbers):
                _win_or_lose = list(self.filled_win_or_lost.values())[i]
            # 最初に rank が表示された時
            elif (
                len(self.modified_win_or_lose_frames_from_rank)
                == len(self.rank_numbers) - 1
            ):
                _win_or_lose = list(
                    self.modified_win_or_lose_frames_from_rank.values()
                )[i]
            else:
                raise Exception("win or lost is not valid")

            _log = BattleLog(
                battle_id=battle_id,
                created_at=created_at,
                win_or_lose=_win_or_lose,
                next_rank=_next_rank,
                your_team=",".join(
                    [
                        v.split("_")[0]
                        for v in list(self.pre_battle_pokemons.values())[i][
                            "your_pokemon_names"
                        ]
                    ]
                ),
                opponent_team=",".join(
                    [
                        v.split("_")[0]
                        for v in list(self.pre_battle_pokemons.values())[i][
                            "opponent_pokemon_names"
                        ]
                    ]
                ),
                your_pokemon_1=self.battle_pokemon_combinations[i]["you"][0],
                your_pokemon_2=self.battle_pokemon_combinations[i]["you"][1],
                your_pokemon_3=self.battle_pokemon_combinations[i]["you"][2],
                opponent_pokemon_1=self.battle_pokemon_combinations[i]["opponent"][0],
                opponent_pokemon_2=self.battle_pokemon_combinations[i]["opponent"][1],
                opponent_pokemon_3=self.battle_pokemon_combinations[i]["opponent"][2],
                video=f"http://youtube.com/watch?v={self.video_id}&t={second_from_frame_number}",
            )
            battle_logs.append(_log)

            # pre_battle
            for pokemon in [
                v.split("_")[0]
                for v in list(self.pre_battle_pokemons.values())[i][
                    "your_pokemon_names"
                ]
            ]:
                modified_pre_battle_pokemons.append(
                    PreBattlePokemon(
                        battle_id=battle_id,
                        team="you",
                        pokemon_name=pokemon,
                    )
                )
            for pokemon in [
                v.split("_")[0]
                for v in list(self.pre_battle_pokemons.values())[i][
                    "opponent_pokemon_names"
                ]
            ]:
                modified_pre_battle_pokemons.append(
                    PreBattlePokemon(
                        battle_id=battle_id,
                        team="opponent",
                        pokemon_name=pokemon,
                    )
                )

            # in-battle
            in_battle_log = self.compressed_battle_pokemons[i]
            for idx, _in_battle_log in enumerate(in_battle_log):
                modified_in_battle_pokemons.append(
                    InBattlePokemon(
                        battle_id=battle_id,
                        turn=idx + 1,
                        frame_number=cast(int, _in_battle_log["frame_number"]),
                        your_pokemon_name=cast(
                            str, _in_battle_log["your_pokemon_name"]
                        ),
                        opponent_pokemon_name=cast(
                            str, _in_battle_log["opponent_pokemon_name"]
                        ),
                    )
                )

        return (
            battles,
            battle_logs,
            modified_pre_battle_pokemons,
            modified_in_battle_pokemons,
            modified_messages,
        )
