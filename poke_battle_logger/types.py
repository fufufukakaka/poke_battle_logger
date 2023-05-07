import dataclasses
from typing import List

from pydantic import BaseModel


@dataclasses.dataclass
class StatusByWebsocket:
    message: List[str]
    progress: int


@dataclasses.dataclass
class Battle:
    battle_id: str
    trainer_id: int


@dataclasses.dataclass
class Message:
    battle_id: str
    frame_number: int
    message: str


@dataclasses.dataclass
class BattleLog:
    battle_id: str
    created_at: str
    win_or_lose: str
    next_rank: int
    your_team: str
    opponent_team: str
    your_pokemon_1: str
    your_pokemon_2: str
    your_pokemon_3: str
    opponent_pokemon_1: str
    opponent_pokemon_2: str
    opponent_pokemon_3: str
    video: str


@dataclasses.dataclass
class PreBattlePokemon:
    battle_id: str
    team: str
    pokemon_name: str


@dataclasses.dataclass
class InBattlePokemon:
    battle_id: str
    turn: int
    frame_number: int
    your_pokemon_name: str
    opponent_pokemon_name: str


class ImageLabel(BaseModel):
    pokemon_image_file_on_gcs: str
    pokemon_label: str
