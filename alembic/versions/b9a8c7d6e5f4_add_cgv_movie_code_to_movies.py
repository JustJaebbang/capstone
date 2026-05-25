"""add cgv_movie_code to movies

Adds the `movies.cgv_movie_code` column so that KOBIS → CGV mapping can be
cached at ingest time (no per-request resolver). Resolved via the
Playwright-based CGVMovieResolver.

Revision ID: b9a8c7d6e5f4
Revises: a8b7c6d5e4f3
Create Date: 2026-05-25 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b9a8c7d6e5f4'
down_revision: Union[str, Sequence[str], None] = 'a8b7c6d5e4f3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('movies', sa.Column('cgv_movie_code', sa.String(length=50), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('movies', 'cgv_movie_code')
