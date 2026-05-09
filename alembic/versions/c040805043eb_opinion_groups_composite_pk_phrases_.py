"""opinion_groups composite pk + phrases json + review_cluster_map composite fk

Revision ID: c040805043eb
Revises: 3ab1cfeae038
Create Date: 2026-05-10 05:27:26.469679

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c040805043eb'
down_revision: Union[str, Sequence[str], None] = '3ab1cfeae038'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint('review_cluster_map_cluster_id_fkey', 'review_cluster_map', type_='foreignkey')
    op.drop_constraint('opinion_groups_pkey', 'opinion_groups', type_='primary')

    op.add_column('opinion_groups', sa.Column('job_id', sa.String(length=100), nullable=False))
    op.add_column('opinion_groups', sa.Column('phrases', sa.JSON(), nullable=False))
    op.create_foreign_key('opinion_groups_job_id_fkey', 'opinion_groups', 'batch_jobs', ['job_id'], ['job_id'])
    op.create_primary_key('opinion_groups_pkey', 'opinion_groups', ['job_id', 'cluster_id'])

    op.add_column('review_cluster_map', sa.Column('job_id', sa.String(length=100), nullable=False))
    op.create_index(op.f('ix_review_cluster_map_job_id'), 'review_cluster_map', ['job_id'], unique=False)
    op.create_foreign_key('review_cluster_map_opinion_groups_fkey', 'review_cluster_map', 'opinion_groups', ['job_id', 'cluster_id'], ['job_id', 'cluster_id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('review_cluster_map_opinion_groups_fkey', 'review_cluster_map', type_='foreignkey')
    op.drop_index(op.f('ix_review_cluster_map_job_id'), table_name='review_cluster_map')
    op.drop_column('review_cluster_map', 'job_id')

    op.drop_constraint('opinion_groups_pkey', 'opinion_groups', type_='primary')
    op.drop_constraint('opinion_groups_job_id_fkey', 'opinion_groups', type_='foreignkey')
    op.drop_column('opinion_groups', 'phrases')
    op.drop_column('opinion_groups', 'job_id')
    op.create_primary_key('opinion_groups_pkey', 'opinion_groups', ['cluster_id'])

    op.create_foreign_key('review_cluster_map_cluster_id_fkey', 'review_cluster_map', 'opinion_groups', ['cluster_id'], ['cluster_id'])
