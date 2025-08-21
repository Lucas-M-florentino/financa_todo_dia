"""fix referencia tabela usuario to users

Revision ID: 3b998bc9e703
Revises: 95c2c3ec123b
Create Date: 2025-08-21 14:11:03.891037

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3b998bc9e703'
down_revision: Union[str, Sequence[str], None] = '95c2c3ec123b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Remover índice e tabela antigos
    op.create_foreign_key(
        'transactions_user_id_fkey',   # Nome explícito da FK
        'transactions',                # Tabela origem
        'users',                       # Tabela destino
        ['usuario_id'],                # Coluna origem
        ['id'],                        # Coluna destino
        ondelete='SET NULL'
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Reverter FK para usuarios
    op.drop_constraint('transactions_user_id_fkey', 'transactions', type_='foreignkey')
