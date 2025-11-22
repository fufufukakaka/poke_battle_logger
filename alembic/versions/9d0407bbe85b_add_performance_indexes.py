"""add_performance_indexes

Revision ID: 9d0407bbe85b
Revises: 13df4e83a95c
Create Date: 2025-09-30 17:25:04.403314

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9d0407bbe85b"
down_revision: Union[str, Sequence[str], None] = "13df4e83a95c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add indexes for battle_log query performance

    # Index on battle.trainer_id for JOIN optimization
    op.create_index("ix_battle_trainer_id", "battle", ["trainer_id"])

    # Index on battlesummary.battle_id for JOIN optimization
    op.create_index("ix_battlesummary_battle_id", "battlesummary", ["battle_id"])

    # Index on battlesummary.created_at for ORDER BY and date range filtering
    op.create_index("ix_battlesummary_created_at", "battlesummary", ["created_at"])

    # Composite index for season-based queries (battle_id + created_at)
    op.create_index(
        "ix_battlesummary_battle_id_created_at",
        "battlesummary",
        ["battle_id", "created_at"],
    )

    # Index on faintedlog.battle_id for JOIN optimization
    op.create_index("ix_faintedlog_battle_id", "faintedlog", ["battle_id"])

    # Index on inbattlepokemonlog.battle_id for JOIN optimization
    op.create_index(
        "ix_inbattlepokemonlog_battle_id", "inbattlepokemonlog", ["battle_id"]
    )

    # Index on messagelog.battle_id for JOIN optimization
    op.create_index("ix_messagelog_battle_id", "messagelog", ["battle_id"])

    # Index on selectedmove.battle_id for JOIN optimization
    op.create_index("ix_selectedmove_battle_id", "selectedmove", ["battle_id"])


def downgrade() -> None:
    """Downgrade schema."""
    # Remove indexes in reverse order
    op.drop_index("ix_selectedmove_battle_id", "selectedmove")
    op.drop_index("ix_messagelog_battle_id", "messagelog")
    op.drop_index("ix_inbattlepokemonlog_battle_id", "inbattlepokemonlog")
    op.drop_index("ix_faintedlog_battle_id", "faintedlog")
    op.drop_index("ix_battlesummary_battle_id_created_at", "battlesummary")
    op.drop_index("ix_battlesummary_created_at", "battlesummary")
    op.drop_index("ix_battlesummary_battle_id", "battlesummary")
    op.drop_index("ix_battle_trainer_id", "battle")
