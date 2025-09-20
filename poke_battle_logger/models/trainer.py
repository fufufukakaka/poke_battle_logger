from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .battle import Battle


class Trainer(SQLModel, table=True):
    """Trainer model."""
    __tablename__ = "trainer"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    identity: str = Field(index=True)
    email: str
    
    # Relationships
    battles: List["Battle"] = Relationship(back_populates="trainer")