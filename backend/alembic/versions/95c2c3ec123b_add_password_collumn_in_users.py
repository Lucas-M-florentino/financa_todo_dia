"""Add password column in users

Revision ID: 95c2c3ec123b
Revises: 4355b5d6f028
Create Date: 2025-08-20 18:32:28.171464
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '95c2c3ec123b'
down_revision: Union[str, Sequence[str], None] = '4355b5d6f028'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Adiciona coluna password em users
    op.add_column('users', sa.Column('password', sa.String(), nullable=True))

    # Ajusta FK de transactions para users (se antes apontava para usuarios)
    op.drop_constraint('transactions_usuario_id_fkey', 'transactions', type_='foreignkey')
    op.create_foreign_key(
        'transactions_user_id_fkey',
        'transactions',
        'users',
        ['usuario_id'],
        ['id'],
        ondelete="SET NULL"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('transactions_user_id_fkey', 'transactions', type_='foreignkey')
    op.drop_column('users', 'password')
