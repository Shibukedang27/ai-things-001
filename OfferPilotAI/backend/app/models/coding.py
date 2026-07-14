"""Live coding ORM models."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin
from app.domain.enums import CodeRunStatus, CodingLanguage
from app.utils.ids import create_id
from app.utils.time import utc_now


class CodeSubmission(TimestampMixin, Base):
    """Persisted live-coding submission and generated analysis."""

    __tablename__ = "code_submissions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=create_id)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    interview_id: Mapped[str | None] = mapped_column(
        ForeignKey("interviews.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    language: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default=CodingLanguage.PYTHON.value,
        server_default=CodingLanguage.PYTHON.value,
        index=True,
    )
    prompt_title: Mapped[str] = mapped_column(String(180), nullable=False)
    prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_code: Mapped[str] = mapped_column(Text, nullable=False)
    stdin: Mapped[str] = mapped_column(Text, nullable=False, default="", server_default="")
    expected_output: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default=CodeRunStatus.SKIPPED.value,
        server_default=CodeRunStatus.SKIPPED.value,
        index=True,
    )
    stdout: Mapped[str] = mapped_column(Text, nullable=False, default="", server_default="")
    stderr: Mapped[str] = mapped_column(Text, nullable=False, default="", server_default="")
    exit_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    execution_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    memory_kb: Mapped[int | None] = mapped_column(Integer, nullable=True)
    time_complexity: Mapped[str] = mapped_column(String(64), nullable=False, default="Unknown", server_default="Unknown")
    space_complexity: Mapped[str] = mapped_column(String(64), nullable=False, default="Unknown", server_default="Unknown")
    bugs: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False, default=list, server_default=text("'[]'::jsonb"))
    optimized_code: Mapped[str] = mapped_column(Text, nullable=False, default="", server_default="")
    improvement_explanation: Mapped[str] = mapped_column(Text, nullable=False, default="", server_default="")
    analysis: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb"))
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb"))
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        server_default=func.now(),
        nullable=False,
        index=True,
    )
