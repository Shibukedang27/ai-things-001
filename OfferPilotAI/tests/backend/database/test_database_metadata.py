"""Database metadata and Alembic migration integrity tests."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
from sqlalchemy.schema import CreateTable
from sqlalchemy.dialects import postgresql

from app.db.base import Base
import app.models  # noqa: F401

pytestmark = pytest.mark.database

PROJECT_ROOT = Path(__file__).resolve().parents[3]
MIGRATIONS_DIR = PROJECT_ROOT / "backend" / "migrations" / "versions"


def test_sqlalchemy_metadata_contains_product_tables():
    expected_tables = {
        "users",
        "interviews",
        "questions",
        "answers",
        "reports",
        "learning_roadmaps",
        "leaderboard",
        "sessions",
        "interview_history",
        "auth_credentials",
        "roles",
        "user_roles",
        "refresh_tokens",
        "password_reset_tokens",
        "answer_evaluations",
        "code_submissions",
        "resume_analyses",
    }

    assert expected_tables.issubset(Base.metadata.tables)


def test_required_foreign_keys_are_declared():
    actual_foreign_keys = {
        (table.name, foreign_key.parent.name, foreign_key.column.table.name)
        for table in Base.metadata.tables.values()
        for foreign_key in table.foreign_keys
    }
    expected_foreign_keys = {
        ("interviews", "user_id", "users"),
        ("questions", "interview_id", "interviews"),
        ("answers", "user_id", "users"),
        ("answers", "interview_id", "interviews"),
        ("answers", "question_id", "questions"),
        ("reports", "user_id", "users"),
        ("reports", "interview_id", "interviews"),
        ("learning_roadmaps", "user_id", "users"),
        ("learning_roadmaps", "report_id", "reports"),
        ("leaderboard", "user_id", "users"),
        ("sessions", "user_id", "users"),
        ("interview_history", "user_id", "users"),
        ("interview_history", "interview_id", "interviews"),
        ("auth_credentials", "user_id", "users"),
        ("user_roles", "user_id", "users"),
        ("user_roles", "role_id", "roles"),
        ("refresh_tokens", "user_id", "users"),
        ("refresh_tokens", "session_id", "sessions"),
        ("password_reset_tokens", "user_id", "users"),
        ("answer_evaluations", "user_id", "users"),
        ("answer_evaluations", "interview_id", "interviews"),
        ("answer_evaluations", "question_id", "questions"),
        ("answer_evaluations", "answer_id", "answers"),
        ("code_submissions", "user_id", "users"),
        ("code_submissions", "interview_id", "interviews"),
        ("resume_analyses", "user_id", "users"),
    }

    assert expected_foreign_keys.issubset(actual_foreign_keys)


def test_postgresql_ddl_compiles_for_all_models():
    dialect = postgresql.dialect()

    for table in Base.metadata.sorted_tables:
        ddl = str(CreateTable(table).compile(dialect=dialect))
        assert f"CREATE TABLE {table.name}" in ddl


def test_alembic_migrations_form_single_linear_chain():
    migrations = [_load_migration(path) for path in sorted(MIGRATIONS_DIR.glob("*.py"))]
    revision_map = {migration.revision: migration.down_revision for migration in migrations}

    assert list(revision_map) == [
        "0001_initial_schema",
        "0002_auth",
        "0003_evaluations",
        "0004_recommendations",
        "0005_live_coding",
        "0006_resume",
    ]
    assert len(revision_map) == len(set(revision_map))
    assert revision_map["0001_initial_schema"] is None
    assert revision_map["0002_auth"] == "0001_initial_schema"
    assert revision_map["0003_evaluations"] == "0002_auth"
    assert revision_map["0004_recommendations"] == "0003_evaluations"
    assert revision_map["0005_live_coding"] == "0004_recommendations"
    assert revision_map["0006_resume"] == "0005_live_coding"

    referenced_down_revisions = {revision for revision in revision_map.values() if revision}
    heads = set(revision_map) - referenced_down_revisions
    assert heads == {"0006_resume"}


def _load_migration(path: Path):
    spec = importlib.util.spec_from_file_location(f"migration_{path.stem}", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module
