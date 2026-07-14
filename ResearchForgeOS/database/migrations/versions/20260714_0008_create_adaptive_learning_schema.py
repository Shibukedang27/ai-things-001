"""create adaptive learning schema

Revision ID: 20260714_0008
Revises: 20260714_0007
Create Date: 2026-07-14 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260714_0008"
down_revision: str | None = "20260714_0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "flashcards",
        sa.Column("owner_user_id", sa.String(length=36), nullable=True),
        sa.Column("document_id", sa.String(length=36), nullable=False),
        sa.Column("card_type", sa.String(length=80), nullable=False),
        sa.Column("difficulty", sa.String(length=40), nullable=False),
        sa.Column("front", sa.Text(), nullable=False),
        sa.Column("back", sa.Text(), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("tags", sa.JSON(), nullable=False),
        sa.Column("source_excerpt", sa.Text(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_flashcards")),
    )
    op.create_index(op.f("ix_flashcards_active"), "flashcards", ["active"])
    op.create_index(op.f("ix_flashcards_card_type"), "flashcards", ["card_type"])
    op.create_index(op.f("ix_flashcards_difficulty"), "flashcards", ["difficulty"])
    op.create_index(op.f("ix_flashcards_document_id"), "flashcards", ["document_id"])
    op.create_index(op.f("ix_flashcards_owner_user_id"), "flashcards", ["owner_user_id"])

    op.create_table(
        "quizzes",
        sa.Column("owner_user_id", sa.String(length=36), nullable=True),
        sa.Column("document_id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=220), nullable=False),
        sa.Column("quiz_type", sa.String(length=80), nullable=False),
        sa.Column("difficulty", sa.String(length=40), nullable=False),
        sa.Column("time_limit_seconds", sa.Integer(), nullable=False),
        sa.Column("adaptive", sa.Boolean(), nullable=False),
        sa.Column("status", sa.String(length=60), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_quizzes")),
    )
    op.create_index(op.f("ix_quizzes_difficulty"), "quizzes", ["difficulty"])
    op.create_index(op.f("ix_quizzes_document_id"), "quizzes", ["document_id"])
    op.create_index(op.f("ix_quizzes_owner_user_id"), "quizzes", ["owner_user_id"])
    op.create_index(op.f("ix_quizzes_quiz_type"), "quizzes", ["quiz_type"])
    op.create_index(op.f("ix_quizzes_status"), "quizzes", ["status"])
    op.create_index(op.f("ix_quizzes_title"), "quizzes", ["title"])

    op.create_table(
        "learning_sessions",
        sa.Column("owner_user_id", sa.String(length=36), nullable=True),
        sa.Column("document_id", sa.String(length=36), nullable=True),
        sa.Column("session_type", sa.String(length=80), nullable=False),
        sa.Column("title", sa.String(length=220), nullable=False),
        sa.Column("status", sa.String(length=60), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_seconds", sa.Integer(), nullable=False),
        sa.Column("items_studied", sa.Integer(), nullable=False),
        sa.Column("correct_count", sa.Integer(), nullable=False),
        sa.Column("total_count", sa.Integer(), nullable=False),
        sa.Column("mastery_delta", sa.Float(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_learning_sessions")),
    )
    op.create_index(op.f("ix_learning_sessions_document_id"), "learning_sessions", ["document_id"])
    op.create_index(op.f("ix_learning_sessions_owner_user_id"), "learning_sessions", ["owner_user_id"])
    op.create_index(op.f("ix_learning_sessions_session_type"), "learning_sessions", ["session_type"])
    op.create_index(op.f("ix_learning_sessions_started_at"), "learning_sessions", ["started_at"])
    op.create_index(op.f("ix_learning_sessions_status"), "learning_sessions", ["status"])
    op.create_index(op.f("ix_learning_sessions_title"), "learning_sessions", ["title"])

    op.create_table(
        "achievements",
        sa.Column("owner_user_id", sa.String(length=36), nullable=True),
        sa.Column("achievement_type", sa.String(length=80), nullable=False),
        sa.Column("title", sa.String(length=220), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("badge", sa.String(length=120), nullable=False),
        sa.Column("skill_level", sa.String(length=80), nullable=False),
        sa.Column("points", sa.Integer(), nullable=False),
        sa.Column("awarded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_achievements")),
        sa.UniqueConstraint("owner_user_id", "achievement_type", "title", name="uq_achievements_owner_type_title"),
    )
    op.create_index(op.f("ix_achievements_achievement_type"), "achievements", ["achievement_type"])
    op.create_index(op.f("ix_achievements_awarded_at"), "achievements", ["awarded_at"])
    op.create_index(op.f("ix_achievements_badge"), "achievements", ["badge"])
    op.create_index(op.f("ix_achievements_owner_user_id"), "achievements", ["owner_user_id"])
    op.create_index(op.f("ix_achievements_skill_level"), "achievements", ["skill_level"])
    op.create_index(op.f("ix_achievements_title"), "achievements", ["title"])

    op.create_table(
        "certificates",
        sa.Column("owner_user_id", sa.String(length=36), nullable=True),
        sa.Column("document_id", sa.String(length=36), nullable=True),
        sa.Column("title", sa.String(length=220), nullable=False),
        sa.Column("certificate_type", sa.String(length=80), nullable=False),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("mastery_percentage", sa.Float(), nullable=False),
        sa.Column("verification_code", sa.String(length=80), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_certificates")),
        sa.UniqueConstraint("verification_code", name=op.f("uq_certificates_verification_code")),
    )
    op.create_index(op.f("ix_certificates_certificate_type"), "certificates", ["certificate_type"])
    op.create_index(op.f("ix_certificates_document_id"), "certificates", ["document_id"])
    op.create_index(op.f("ix_certificates_issued_at"), "certificates", ["issued_at"])
    op.create_index(op.f("ix_certificates_owner_user_id"), "certificates", ["owner_user_id"])
    op.create_index(op.f("ix_certificates_title"), "certificates", ["title"])
    op.create_index(op.f("ix_certificates_verification_code"), "certificates", ["verification_code"])

    op.create_table(
        "progress",
        sa.Column("owner_user_id", sa.String(length=36), nullable=True),
        sa.Column("document_id", sa.String(length=36), nullable=True),
        sa.Column("knowledge_score", sa.Float(), nullable=False),
        sa.Column("retention_score", sa.Float(), nullable=False),
        sa.Column("weak_concepts", sa.JSON(), nullable=False),
        sa.Column("strong_concepts", sa.JSON(), nullable=False),
        sa.Column("learning_velocity", sa.Float(), nullable=False),
        sa.Column("quiz_accuracy", sa.Float(), nullable=False),
        sa.Column("memory_heatmap", sa.JSON(), nullable=False),
        sa.Column("study_time_minutes", sa.Integer(), nullable=False),
        sa.Column("completion_rate", sa.Float(), nullable=False),
        sa.Column("mastery_graph", sa.JSON(), nullable=False),
        sa.Column("mastered_items", sa.Integer(), nullable=False),
        sa.Column("total_items", sa.Integer(), nullable=False),
        sa.Column("streak_days", sa.Integer(), nullable=False),
        sa.Column("last_activity_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_progress")),
        sa.UniqueConstraint("owner_user_id", "document_id", name="uq_progress_owner_document"),
    )
    op.create_index(op.f("ix_progress_document_id"), "progress", ["document_id"])
    op.create_index(op.f("ix_progress_last_activity_at"), "progress", ["last_activity_at"])
    op.create_index(op.f("ix_progress_owner_user_id"), "progress", ["owner_user_id"])

    op.create_table(
        "coding_challenges",
        sa.Column("owner_user_id", sa.String(length=36), nullable=True),
        sa.Column("document_id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=220), nullable=False),
        sa.Column("difficulty", sa.String(length=40), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("starter_code", sa.Text(), nullable=False),
        sa.Column("hints", sa.JSON(), nullable=False),
        sa.Column("optimal_solution", sa.Text(), nullable=False),
        sa.Column("complexity_analysis", sa.Text(), nullable=False),
        sa.Column("alternative_solutions", sa.JSON(), nullable=False),
        sa.Column("edge_cases", sa.JSON(), nullable=False),
        sa.Column("unit_tests", sa.JSON(), nullable=False),
        sa.Column("tags", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=60), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_coding_challenges")),
    )
    op.create_index(op.f("ix_coding_challenges_difficulty"), "coding_challenges", ["difficulty"])
    op.create_index(op.f("ix_coding_challenges_document_id"), "coding_challenges", ["document_id"])
    op.create_index(op.f("ix_coding_challenges_owner_user_id"), "coding_challenges", ["owner_user_id"])
    op.create_index(op.f("ix_coding_challenges_status"), "coding_challenges", ["status"])
    op.create_index(op.f("ix_coding_challenges_title"), "coding_challenges", ["title"])

    op.create_table(
        "revision_plans",
        sa.Column("owner_user_id", sa.String(length=36), nullable=True),
        sa.Column("document_id", sa.String(length=36), nullable=False),
        sa.Column("plan_type", sa.String(length=80), nullable=False),
        sa.Column("title", sa.String(length=220), nullable=False),
        sa.Column("schedule", sa.JSON(), nullable=False),
        sa.Column("focus_concepts", sa.JSON(), nullable=False),
        sa.Column("estimated_minutes", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=60), nullable=False),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_revision_plans")),
    )
    op.create_index(op.f("ix_revision_plans_document_id"), "revision_plans", ["document_id"])
    op.create_index(op.f("ix_revision_plans_due_at"), "revision_plans", ["due_at"])
    op.create_index(op.f("ix_revision_plans_owner_user_id"), "revision_plans", ["owner_user_id"])
    op.create_index(op.f("ix_revision_plans_plan_type"), "revision_plans", ["plan_type"])
    op.create_index(op.f("ix_revision_plans_status"), "revision_plans", ["status"])
    op.create_index(op.f("ix_revision_plans_title"), "revision_plans", ["title"])

    op.create_table(
        "quiz_questions",
        sa.Column("quiz_id", sa.String(length=36), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("question_type", sa.String(length=80), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("choices", sa.JSON(), nullable=False),
        sa.Column("correct_answers", sa.JSON(), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("difficulty", sa.String(length=40), nullable=False),
        sa.Column("points", sa.Integer(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["quiz_id"], ["quizzes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_quiz_questions")),
    )
    op.create_index(op.f("ix_quiz_questions_difficulty"), "quiz_questions", ["difficulty"])
    op.create_index(op.f("ix_quiz_questions_question_type"), "quiz_questions", ["question_type"])
    op.create_index(op.f("ix_quiz_questions_quiz_id"), "quiz_questions", ["quiz_id"])

    op.create_table(
        "quiz_attempts",
        sa.Column("quiz_id", sa.String(length=36), nullable=False),
        sa.Column("owner_user_id", sa.String(length=36), nullable=True),
        sa.Column("status", sa.String(length=60), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("time_spent_seconds", sa.Integer(), nullable=False),
        sa.Column("answers", sa.JSON(), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("total_points", sa.Float(), nullable=False),
        sa.Column("accuracy", sa.Float(), nullable=False),
        sa.Column("passed", sa.Boolean(), nullable=False),
        sa.Column("feedback", sa.JSON(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["quiz_id"], ["quizzes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_quiz_attempts")),
    )
    op.create_index(op.f("ix_quiz_attempts_owner_user_id"), "quiz_attempts", ["owner_user_id"])
    op.create_index(op.f("ix_quiz_attempts_quiz_id"), "quiz_attempts", ["quiz_id"])
    op.create_index(op.f("ix_quiz_attempts_started_at"), "quiz_attempts", ["started_at"])
    op.create_index(op.f("ix_quiz_attempts_status"), "quiz_attempts", ["status"])

    op.create_table(
        "reviews",
        sa.Column("owner_user_id", sa.String(length=36), nullable=True),
        sa.Column("flashcard_id", sa.String(length=36), nullable=False),
        sa.Column("rating", sa.String(length=40), nullable=False),
        sa.Column("response_quality", sa.Float(), nullable=False),
        sa.Column("correct", sa.Boolean(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("scheduled_before", sa.DateTime(timezone=True), nullable=True),
        sa.Column("next_review_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("memory_strength", sa.Float(), nullable=False),
        sa.Column("retention_score", sa.Float(), nullable=False),
        sa.Column("duration_ms", sa.Integer(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["flashcard_id"], ["flashcards.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_reviews")),
    )
    op.create_index(op.f("ix_reviews_correct"), "reviews", ["correct"])
    op.create_index(op.f("ix_reviews_flashcard_id"), "reviews", ["flashcard_id"])
    op.create_index(op.f("ix_reviews_next_review_at"), "reviews", ["next_review_at"])
    op.create_index(op.f("ix_reviews_owner_user_id"), "reviews", ["owner_user_id"])
    op.create_index(op.f("ix_reviews_rating"), "reviews", ["rating"])
    op.create_index(op.f("ix_reviews_reviewed_at"), "reviews", ["reviewed_at"])

    op.create_table(
        "memory_tracking",
        sa.Column("owner_user_id", sa.String(length=36), nullable=True),
        sa.Column("document_id", sa.String(length=36), nullable=True),
        sa.Column("flashcard_id", sa.String(length=36), nullable=True),
        sa.Column("concept", sa.String(length=220), nullable=False),
        sa.Column("memory_strength", sa.Float(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("retention_score", sa.Float(), nullable=False),
        sa.Column("review_count", sa.Integer(), nullable=False),
        sa.Column("success_rate", sa.Float(), nullable=False),
        sa.Column("last_review_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("next_review_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("forgetting_curve", sa.JSON(), nullable=False),
        sa.Column("mastery_percentage", sa.Float(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["flashcard_id"], ["flashcards.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_memory_tracking")),
        sa.UniqueConstraint("owner_user_id", "flashcard_id", name="uq_memory_tracking_owner_flashcard"),
    )
    op.create_index(op.f("ix_memory_tracking_concept"), "memory_tracking", ["concept"])
    op.create_index(op.f("ix_memory_tracking_document_id"), "memory_tracking", ["document_id"])
    op.create_index(op.f("ix_memory_tracking_flashcard_id"), "memory_tracking", ["flashcard_id"])
    op.create_index(op.f("ix_memory_tracking_next_review_at"), "memory_tracking", ["next_review_at"])
    op.create_index(op.f("ix_memory_tracking_owner_user_id"), "memory_tracking", ["owner_user_id"])


def downgrade() -> None:
    for index_name in (
        "ix_memory_tracking_owner_user_id",
        "ix_memory_tracking_next_review_at",
        "ix_memory_tracking_flashcard_id",
        "ix_memory_tracking_document_id",
        "ix_memory_tracking_concept",
    ):
        op.drop_index(op.f(index_name), table_name="memory_tracking")
    op.drop_table("memory_tracking")

    for index_name in (
        "ix_reviews_reviewed_at",
        "ix_reviews_rating",
        "ix_reviews_owner_user_id",
        "ix_reviews_next_review_at",
        "ix_reviews_flashcard_id",
        "ix_reviews_correct",
    ):
        op.drop_index(op.f(index_name), table_name="reviews")
    op.drop_table("reviews")

    for index_name in (
        "ix_quiz_attempts_status",
        "ix_quiz_attempts_started_at",
        "ix_quiz_attempts_quiz_id",
        "ix_quiz_attempts_owner_user_id",
    ):
        op.drop_index(op.f(index_name), table_name="quiz_attempts")
    op.drop_table("quiz_attempts")

    for index_name in (
        "ix_quiz_questions_quiz_id",
        "ix_quiz_questions_question_type",
        "ix_quiz_questions_difficulty",
    ):
        op.drop_index(op.f(index_name), table_name="quiz_questions")
    op.drop_table("quiz_questions")

    for index_name in (
        "ix_revision_plans_title",
        "ix_revision_plans_status",
        "ix_revision_plans_plan_type",
        "ix_revision_plans_owner_user_id",
        "ix_revision_plans_due_at",
        "ix_revision_plans_document_id",
    ):
        op.drop_index(op.f(index_name), table_name="revision_plans")
    op.drop_table("revision_plans")

    for index_name in (
        "ix_coding_challenges_title",
        "ix_coding_challenges_status",
        "ix_coding_challenges_owner_user_id",
        "ix_coding_challenges_document_id",
        "ix_coding_challenges_difficulty",
    ):
        op.drop_index(op.f(index_name), table_name="coding_challenges")
    op.drop_table("coding_challenges")

    for index_name in ("ix_progress_owner_user_id", "ix_progress_last_activity_at", "ix_progress_document_id"):
        op.drop_index(op.f(index_name), table_name="progress")
    op.drop_table("progress")

    for index_name in (
        "ix_certificates_verification_code",
        "ix_certificates_title",
        "ix_certificates_owner_user_id",
        "ix_certificates_issued_at",
        "ix_certificates_document_id",
        "ix_certificates_certificate_type",
    ):
        op.drop_index(op.f(index_name), table_name="certificates")
    op.drop_table("certificates")

    for index_name in (
        "ix_achievements_title",
        "ix_achievements_skill_level",
        "ix_achievements_owner_user_id",
        "ix_achievements_badge",
        "ix_achievements_awarded_at",
        "ix_achievements_achievement_type",
    ):
        op.drop_index(op.f(index_name), table_name="achievements")
    op.drop_table("achievements")

    for index_name in (
        "ix_learning_sessions_title",
        "ix_learning_sessions_status",
        "ix_learning_sessions_started_at",
        "ix_learning_sessions_session_type",
        "ix_learning_sessions_owner_user_id",
        "ix_learning_sessions_document_id",
    ):
        op.drop_index(op.f(index_name), table_name="learning_sessions")
    op.drop_table("learning_sessions")

    for index_name in (
        "ix_quizzes_title",
        "ix_quizzes_status",
        "ix_quizzes_quiz_type",
        "ix_quizzes_owner_user_id",
        "ix_quizzes_document_id",
        "ix_quizzes_difficulty",
    ):
        op.drop_index(op.f(index_name), table_name="quizzes")
    op.drop_table("quizzes")

    for index_name in (
        "ix_flashcards_owner_user_id",
        "ix_flashcards_document_id",
        "ix_flashcards_difficulty",
        "ix_flashcards_card_type",
        "ix_flashcards_active",
    ):
        op.drop_index(op.f(index_name), table_name="flashcards")
    op.drop_table("flashcards")
