"""fix_selectedmove_battle_id_type

Revision ID: 13df4e83a95c
Revises: 802ebed3492d
Create Date: 2025-09-20 17:30:15.294508

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '13df4e83a95c'
down_revision: Union[str, Sequence[str], None] = '802ebed3492d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Fix battle_id type in related tables."""
    # Drop existing foreign key constraint if it exists
    with op.batch_alter_table('selectedmove') as batch_op:
        try:
            batch_op.drop_constraint('selectedmove_battle_id_fkey', type_='foreignkey')
        except:
            pass  # Constraint might not exist

        # Change column type from integer to string
        batch_op.alter_column(
            'battle_id',
            type_=sqlmodel.sql.sqltypes.AutoString(),
            existing_type=sa.Integer(),
            nullable=False
        )

        # Recreate foreign key constraint
        batch_op.create_foreign_key(
            'selectedmove_battle_id_fkey',
            'battle',
            ['battle_id'],
            ['battle_id']
        )

    # Fix the same issue in other tables that might have the same problem
    # MessageLog
    with op.batch_alter_table('messagelog') as batch_op:
        try:
            batch_op.drop_constraint('messagelog_battle_id_fkey', type_='foreignkey')
        except:
            pass  # Constraint might not exist

        batch_op.alter_column(
            'battle_id',
            type_=sqlmodel.sql.sqltypes.AutoString(),
            existing_type=sa.Integer(),
            nullable=False
        )

        batch_op.create_foreign_key(
            'messagelog_battle_id_fkey',
            'battle',
            ['battle_id'],
            ['battle_id']
        )

    # InBattlePokemonLog
    with op.batch_alter_table('inbattlepokemonlog') as batch_op:
        try:
            batch_op.drop_constraint('inbattlepokemonlog_battle_id_fkey', type_='foreignkey')
        except:
            pass  # Constraint might not exist

        batch_op.alter_column(
            'battle_id',
            type_=sqlmodel.sql.sqltypes.AutoString(),
            existing_type=sa.Integer(),
            nullable=False
        )

        batch_op.create_foreign_key(
            'inbattlepokemonlog_battle_id_fkey',
            'battle',
            ['battle_id'],
            ['battle_id']
        )

    # FaintedLog
    with op.batch_alter_table('faintedlog') as batch_op:
        try:
            batch_op.drop_constraint('faintedlog_battle_id_fkey', type_='foreignkey')
        except:
            pass  # Constraint might not exist

        batch_op.alter_column(
            'battle_id',
            type_=sqlmodel.sql.sqltypes.AutoString(),
            existing_type=sa.Integer(),
            nullable=False
        )

        batch_op.create_foreign_key(
            'faintedlog_battle_id_fkey',
            'battle',
            ['battle_id'],
            ['battle_id']
        )

    # BattlePokemonTeam
    with op.batch_alter_table('battlepokemonteam') as batch_op:
        try:
            batch_op.drop_constraint('battlepokemonteam_battle_id_fkey', type_='foreignkey')
        except:
            pass  # Constraint might not exist

        batch_op.alter_column(
            'battle_id',
            type_=sqlmodel.sql.sqltypes.AutoString(),
            existing_type=sa.Integer(),
            nullable=False
        )

        batch_op.create_foreign_key(
            'battlepokemonteam_battle_id_fkey',
            'battle',
            ['battle_id'],
            ['battle_id']
        )

    # BattleSummary
    with op.batch_alter_table('battlesummary') as batch_op:
        try:
            batch_op.drop_constraint('battlesummary_battle_id_fkey', type_='foreignkey')
        except:
            pass  # Constraint might not exist

        batch_op.alter_column(
            'battle_id',
            type_=sqlmodel.sql.sqltypes.AutoString(),
            existing_type=sa.Integer(),
            nullable=False
        )

        batch_op.create_foreign_key(
            'battlesummary_battle_id_fkey',
            'battle',
            ['battle_id'],
            ['battle_id']
        )


def downgrade() -> None:
    """Revert changes."""
    # Drop foreign key constraint
    with op.batch_alter_table('selectedmove') as batch_op:
        batch_op.drop_constraint('selectedmove_battle_id_fkey', type_='foreignkey')

        # Change column type back to integer
        batch_op.alter_column(
            'battle_id',
            type_=sa.Integer(),
            existing_type=sqlmodel.sql.sqltypes.AutoString(),
            nullable=False
        )

        # Recreate foreign key constraint with integer reference
        batch_op.create_foreign_key(
            'selectedmove_battle_id_fkey',
            'battle',
            ['battle_id'],
            ['id']
        )
