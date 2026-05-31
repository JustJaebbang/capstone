"""add collection_jobs table

Adds the collection_jobs table for tracking collector executions
(real-time POST /collection/reviews/run-now and future scheduled runs).

Revision ID: a8b7c6d5e4f3
Revises: f1a2c3d4b5e6
Create Date: 2026-05-24 22:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a8b7c6d5e4f3'
down_revision: Union[str, Sequence[str], None] = 'f1a2c3d4b5e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'collection_jobs',
        sa.Column('collection_job_id', sa.String(length=100), nullable=False),
        sa.Column('source', sa.String(length=50), nullable=False),
        sa.Column('mode', sa.String(length=20), nullable=False),
        sa.Column('target_movie_id', sa.String(length=50), nullable=False),
        sa.Column('source_external_id', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('finished_at', sa.DateTime(), nullable=True),
        sa.Column('total_fetched', sa.Integer(), nullable=False),
        sa.Column('total_inserted', sa.Integer(), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['target_movie_id'], ['movies.movie_id']),
        sa.PrimaryKeyConstraint('collection_job_id'),
    )
    op.create_index(
        'ix_collection_jobs_source', 'collection_jobs', ['source'], unique=False
    )
    op.create_index(
        'ix_collection_jobs_target_movie_id', 'collection_jobs', ['target_movie_id'], unique=False
    )
    op.create_index(
        'ix_collection_jobs_status', 'collection_jobs', ['status'], unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_collection_jobs_status', table_name='collection_jobs')
    op.drop_index('ix_collection_jobs_target_movie_id', table_name='collection_jobs')
    op.drop_index('ix_collection_jobs_source', table_name='collection_jobs')
    op.drop_table('collection_jobs')
