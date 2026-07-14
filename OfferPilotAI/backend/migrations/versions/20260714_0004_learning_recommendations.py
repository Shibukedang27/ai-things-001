"""Learning recommendation roadmap fields.

Revision ID: 0004_learning_recommendations
Revises: 0003_answer_evaluations
Create Date: 2026-07-14 00:00:00.000000+00:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0004_recommendations"
down_revision: str | None = "0003_evaluations"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


JSONB_LIST_COLUMNS = [
    "weak_topics",
    "leetcode_problems",
    "hackerrank_problems",
    "books",
    "courses",
    "youtube_videos",
    "daily_practice_plan",
    "weekly_roadmap",
    "monthly_roadmap",
]


def upgrade() -> None:
    for column_name in JSONB_LIST_COLUMNS:
        op.add_column(
            "learning_roadmaps",
            sa.Column(
                column_name,
                postgresql.JSONB(astext_type=sa.Text()),
                server_default=sa.text("'[]'::jsonb"),
                nullable=False,
            ),
        )

    op.add_column(
        "learning_roadmaps",
        sa.Column(
            "source_summary",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("learning_roadmaps", "source_summary")
    for column_name in reversed(JSONB_LIST_COLUMNS):
        op.drop_column("learning_roadmaps", column_name)
