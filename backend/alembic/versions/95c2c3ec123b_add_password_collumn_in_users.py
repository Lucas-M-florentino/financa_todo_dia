"""Add password column in usuarios

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
    op.add_column('usuarios', sa.Column('password', sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('usuarios', 'password')
