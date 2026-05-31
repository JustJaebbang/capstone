"""add collector columns to movies and reviews

Adds columns required by the real-data collector layer (toclaude2.md step 1):
- movies: release_date, poster_url, genre
- reviews: external_review_id, author, rating, written_at, text_hash
- reviews: UNIQUE(source, external_review_id) for primary dedup
- reviews: INDEX(source, movie_id, text_hash) for fallback dedup lookups

Existing columns (release_year, registered_at) are left in place to avoid
breaking the 17 call sites that reference them.

Revision ID: f1a2c3d4b5e6
Revises: c040805043eb
Create Date: 2026-05-11 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f1a2c3d4b5e6'
down_revision: Union[str, Sequence[str], None] = 'c040805043eb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # --- movies ---
    op.add_column('movies', sa.Column('release_date', sa.Date(), nullable=True))
    op.add_column('movies', sa.Column('poster_url', sa.String(length=1024), nullable=True))
    op.add_column('movies', sa.Column('genre', sa.String(length=255), nullable=True))

    # --- reviews ---
    op.add_column('reviews', sa.Column('external_review_id', sa.String(length=255), nullable=True))
    op.add_column('reviews', sa.Column('author', sa.String(length=100), nullable=True))
    op.add_column('reviews', sa.Column('rating', sa.Numeric(precision=3, scale=1), nullable=True))
    op.add_column('reviews', sa.Column('written_at', sa.DateTime(), nullable=True))
    op.add_column('reviews', sa.Column('text_hash', sa.String(length=64), nullable=True))

    op.create_unique_constraint(
        'uq_reviews_source_external',
        'reviews',
        ['source', 'external_review_id'],
    )
    op.create_index(
        'ix_reviews_source_movie_hash',
        'reviews',
        ['source', 'movie_id', 'text_hash'],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_reviews_source_movie_hash', table_name='reviews')
    op.drop_constraint('uq_reviews_source_external', 'reviews', type_='unique')

    op.drop_column('reviews', 'text_hash')
    op.drop_column('reviews', 'written_at')
    op.drop_column('reviews', 'rating')
    op.drop_column('reviews', 'author')
    op.drop_column('reviews', 'external_review_id')

    op.drop_column('movies', 'genre')
    op.drop_column('movies', 'poster_url')
    op.drop_column('movies', 'release_date')
