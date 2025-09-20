from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .battle import Battle


class BattlePokemonTeam(SQLModel, table=True):
    """Pokemon team composition model."""
    __tablename__ = "battlepokemonteam"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    battle_id: str = Field(foreign_key="battle.battle_id")
    team: str
    pokemon_name: str
    
    # Relationships
    battle: Optional["Battle"] = Relationship(back_populates="pokemon_teams")


class InBattlePokemonLog(SQLModel, table=True):
    """In-battle Pokemon activity log model."""
    __tablename__ = "inbattlepokemonlog"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    battle_id: str = Field(foreign_key="battle.battle_id")
    turn: int
    frame_number: int
    your_pokemon_name: str
    opponent_pokemon_name: str
    
    # Relationships
    battle: Optional["Battle"] = Relationship(back_populates="in_battle_logs")


class FaintedLog(SQLModel, table=True):
    """Fainted Pokemon log model."""
    __tablename__ = "faintedlog"

    id: Optional[int] = Field(default=None, primary_key=True)
    battle_id: str = Field(foreign_key="battle.battle_id")
    turn: int
    your_pokemon_name: str
    opponent_pokemon_name: str
    fainted_pokemon_side: str

    # Relationships
    battle: Optional["Battle"] = Relationship(back_populates="fainted_logs")