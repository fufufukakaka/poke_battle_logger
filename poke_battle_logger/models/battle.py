from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .game import MessageLog, SelectedMove
    from .pokemon import BattlePokemonTeam, FaintedLog, InBattlePokemonLog
    from .trainer import Trainer


class Battle(SQLModel, table=True):
    """Battle model."""

    __tablename__ = "battle"

    id: Optional[int] = Field(default=None, primary_key=True)
    battle_id: str = Field(unique=True, index=True)
    trainer_id: int = Field(foreign_key="trainer.id")

    # Relationships
    trainer: Optional["Trainer"] = Relationship(back_populates="battles")
    battle_summary: Optional["BattleSummary"] = Relationship(back_populates="battle")
    pokemon_teams: List["BattlePokemonTeam"] = Relationship(back_populates="battle")
    in_battle_logs: List["InBattlePokemonLog"] = Relationship(back_populates="battle")
    fainted_logs: List["FaintedLog"] = Relationship(back_populates="battle")
    message_logs: List["MessageLog"] = Relationship(back_populates="battle")
    selected_moves: List["SelectedMove"] = Relationship(back_populates="battle")


class BattleSummary(SQLModel, table=True):
    """Battle summary model."""

    __tablename__ = "battlesummary"

    id: Optional[int] = Field(default=None, primary_key=True)
    battle_id: str = Field(foreign_key="battle.battle_id")
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
    memo: str = ""

    # Relationships
    battle: Optional["Battle"] = Relationship(back_populates="battle_summary")


class BattleVideo(SQLModel, table=True):
    """Battle video processing status model."""

    __tablename__ = "battlevideo"

    id: Optional[int] = Field(default=None, primary_key=True)
    trainer_id: int = Field(foreign_key="trainer.id")
    video_id: str
    process_status: str
