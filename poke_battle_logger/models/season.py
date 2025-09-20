from typing import Optional
from sqlmodel import Field, SQLModel


class Season(SQLModel, table=True):
    """Season model."""
    __tablename__ = "season"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    season: int = Field(index=True)
    start_datetime: str
    end_datetime: str