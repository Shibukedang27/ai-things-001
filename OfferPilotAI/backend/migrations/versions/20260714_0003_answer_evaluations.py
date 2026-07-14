"""Answer evaluation schema.

Revision ID: 0003_answer_evaluations
Revises: 0002_authentication_authorization
Create Date: 2026-07-14 00:00:00.000000+00:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0003_evaluations"
down_revision: str | None = "0002_auth"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "answer_evaluations",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("interview_id", sa.String(length=36), nullable=False),
        sa.Column("question_id", sa.String(length=36), nullable=False),
        sa.Column("answer_id", sa.String(length=36), nullable=False),
        sa.Column("technical_accuracy", sa.Numeric(5, 2), nullable=False),
        sa.Column("communication", sa.Numeric(5, 2), nullable=False),
        sa.Column("completeness", sa.Numeric(5, 2), nullable=False),
        sa.Column("confidence_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("problem_solving", sa.Numeric(5, 2), nullable=False),
        sa.Column("explanation_quality", sa.Numeric(5, 2), nullable=False),
        sa.Column("overall_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("correct_answer", sa.Text(), nullable=False),
        sa.Column("better_answer", sa.Text(), nullable=False),
        sa.Column("industry_standard_answer", sa.Text(), nullable=False),
        sa.Column("improvement_suggestions", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=False),
        sa.Column("related_topics", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=False),
        sa.Column("difficulty_analysis", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("evaluator_version", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["answer_id"], ["answers.id"], name=op.f("fk_answer_evaluations_answer_id_answers"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["interview_id"], ["interviews.id"], name=op.f("fk_answer_evaluations_interview_id_interviews"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["question_id"], ["questions.id"], name=op.f("fk_answer_evaluations_question_id_questions"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_answer_evaluations_user_id_users"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_answer_evaluations")),
        sa.UniqueConstraint("answer_id", name="uq_answer_evaluations_answer_id"),
    )
    op.create_index(op.f("ix_answer_evaluations_answer_id"), "answer_evaluations", ["answer_id"], unique=False)
    op.create_index(op.f("ix_answer_evaluations_interview_id"), "answer_evaluations", ["interview_id"], unique=False)
    op.create_index(op.f("ix_answer_evaluations_question_id"), "answer_evaluations", ["question_id"], unique=False)
    op.create_index(op.f("ix_answer_evaluations_user_id"), "answer_evaluations", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_answer_evaluations_user_id"), table_name="answer_evaluations")
    op.drop_index(op.f("ix_answer_evaluations_question_id"), table_name="answer_evaluations")
    op.drop_index(op.f("ix_answer_evaluations_interview_id"), table_name="answer_evaluations")
    op.drop_index(op.f("ix_answer_evaluations_answer_id"), table_name="answer_evaluations")
    op.drop_table("answer_evaluations")
