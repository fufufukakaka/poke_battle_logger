from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .battle import Battle


class MessageLog(SQLModel, table=True):
    """In-battle message log model."""

    __tablename__ = "messagelog"

    id: Optional[int] = Field(default=None, primary_key=True)
    battle_id: str = Field(foreign_key="battle.battle_id")
    frame_number: int
    message: str

    # Relationships
    battle: Optional["Battle"] = Relationship(back_populates="message_logs")


class SelectedMove(SQLModel, table=True):
    """Selected move log model."""

    __tablename__ = "selectedmove"

    id: Optional[int] = Field(default=None, primary_key=True)
    battle_id: str = Field(foreign_key="battle.battle_id")
    frame_number: int
    your_pokemon_name: str
    opponent_pokemon_name: str
    move: str

    # Relationships
    battle: Optional["Battle"] = Relationship(back_populates="selected_moves")
