import os
from contextlib import contextmanager
from typing import Generator

from sqlmodel import Session, SQLModel, create_engine


def get_engine():
    """Get database engine based on environment."""
    env = os.environ.get("ENV", "local")
    
    if env == "local":
        database_url = "sqlite:///poke_battle_logger.db"
        engine = create_engine(
            database_url,
            echo=False,
            connect_args={"check_same_thread": False}
        )
    elif env == "production":
        database_url = (
            f"postgresql://"
            f"{os.environ.get('POSTGRES_USER', 'postgres')}:"
            f"{os.environ.get('POSTGRES_PASSWORD', 'postgres')}@"
            f"{os.environ.get('POSTGRES_HOST', 'localhost')}:"
            f"{os.environ.get('POSTGRES_PORT', 5432)}/"
            f"{os.environ.get('POSTGRES_DB', 'postgres')}"
        )
        engine = create_engine(
            database_url,
            echo=False,
            pool_pre_ping=True
        )
    else:
        raise ValueError("ENV must be local or production")
    
    return engine


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """Get database session."""
    engine = get_engine()
    with Session(engine) as session:
        yield session


def create_tables():
    """Create all database tables."""
    engine = get_engine()
    SQLModel.metadata.create_all(engine)