"""Add outbox events

Revision ID: de6b3a34fef6
Revises: f772e5b2afc9
Create Date: 2026-01-03 19:27:54.994618

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'de6b3a34fef6'
down_revision: Union[str, Sequence[str], None] = 'f772e5b2afc9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Ensure schema exists then create outbox_events only
    op.execute("CREATE SCHEMA IF NOT EXISTS users")
    op.create_table(
        'outbox_events',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('event_type', sa.String(), nullable=False),
        sa.Column('created_at', sa.Integer(), server_default=sa.text('EXTRACT(epoch FROM now())'), nullable=False),
        sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('updated_at', sa.Integer(), nullable=True),
        sa.Column('status', sa.Enum('pending', 'sent', 'failed', name='outboxstatus'), server_default='pending', nullable=False),
        sa.Column('retry_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('error', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        schema='users',
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # Drop only the outbox_events table
    op.drop_table('outbox_events', schema='users')
    # ### end Alembic commands ###
