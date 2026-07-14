"""Live coding module.

Revision ID: 0005_live_coding_module
Revises: 0004_learning_recommendations
Create Date: 2026-07-14 00:00:00.000000+00:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0005_live_coding"
down_revision: str | None = "0004_recommendations"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "code_submissions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("interview_id", sa.String(length=36), nullable=True),
        sa.Column("language", sa.String(length=32), server_default="python", nullable=False),
        sa.Column("prompt_title", sa.String(length=180), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=True),
        sa.Column("source_code", sa.Text(), nullable=False),
        sa.Column("stdin", sa.Text(), server_default="", nullable=False),
        sa.Column("expected_output", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), server_default="skipped", nullable=False),
        sa.Column("stdout", sa.Text(), server_default="", nullable=False),
        sa.Column("stderr", sa.Text(), server_default="", nullable=False),
        sa.Column("exit_code", sa.Integer(), nullable=True),
        sa.Column("execution_time_ms", sa.Integer(), nullable=True),
        sa.Column("memory_kb", sa.Integer(), nullable=True),
        sa.Column("time_complexity", sa.String(length=64), server_default="Unknown", nullable=False),
        sa.Column("space_complexity", sa.String(length=64), server_default="Unknown", nullable=False),
        sa.Column(
            "bugs",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column("optimized_code", sa.Text(), server_default="", nullable=False),
        sa.Column("improvement_explanation", sa.Text(), server_default="", nullable=False),
        sa.Column(
            "analysis",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "metadata_json",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column("submitted_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["interview_id"], ["interviews.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_code_submissions_user_id", "code_submissions", ["user_id"], unique=False)
    op.create_index("ix_code_submissions_interview_id", "code_submissions", ["interview_id"], unique=False)
    op.create_index("ix_code_submissions_language", "code_submissions", ["language"], unique=False)
    op.create_index("ix_code_submissions_status", "code_submissions", ["status"], unique=False)
    op.create_index("ix_code_submissions_submitted_at", "code_submissions", ["submitted_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_code_submissions_submitted_at", table_name="code_submissions")
    op.drop_index("ix_code_submissions_status", table_name="code_submissions")
    op.drop_index("ix_code_submissions_language", table_name="code_submissions")
    op.drop_index("ix_code_submissions_interview_id", table_name="code_submissions")
    op.drop_index("ix_code_submissions_user_id", table_name="code_submissions")
    op.drop_table("code_submissions")
