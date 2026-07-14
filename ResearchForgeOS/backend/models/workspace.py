from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base
from backend.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from backend.models.user import User


class Collection(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "collections"

    owner_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    parent_collection_id: Mapped[str | None] = mapped_column(
        ForeignKey("collections.id", ondelete="SET NULL"),
        index=True,
    )
    project_id: Mapped[str | None] = mapped_column(ForeignKey("projects.id", ondelete="SET NULL"), index=True)
    name: Mapped[str] = mapped_column(String(160), index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    collection_type: Mapped[str] = mapped_column(String(80), index=True, nullable=False, default="research")
    color: Mapped[str] = mapped_column(String(24), nullable=False, default="#2563eb")
    icon: Mapped[str] = mapped_column(String(80), nullable=False, default="folder")
    tags: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    metadata_json: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)

    owner: Mapped[User | None] = relationship("User")


class Project(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "projects"

    owner_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    title: Mapped[str] = mapped_column(String(180), index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(60), index=True, nullable=False, default="active")
    research_domain: Mapped[str | None] = mapped_column(String(140), index=True)
    goals: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    milestones: Mapped[list[dict[str, object]]] = mapped_column(JSON, default=list, nullable=False)
    resources: Mapped[list[dict[str, object]]] = mapped_column(JSON, default=list, nullable=False)
    progress_percent: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    target_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    metadata_json: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)

    owner: Mapped[User | None] = relationship("User")
    notes: Mapped[list[Note]] = relationship("Note", back_populates="project", lazy="selectin")
    tasks: Mapped[list[WorkspaceTask]] = relationship("WorkspaceTask", back_populates="project", lazy="selectin")


class Note(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "notes"
    __table_args__ = (
        UniqueConstraint("owner_user_id", "content_hash", name="uq_notes_owner_content_hash"),
    )

    owner_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    project_id: Mapped[str | None] = mapped_column(ForeignKey("projects.id", ondelete="SET NULL"), index=True)
    collection_id: Mapped[str | None] = mapped_column(ForeignKey("collections.id", ondelete="SET NULL"), index=True)
    title: Mapped[str] = mapped_column(String(180), index=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(220), index=True, nullable=False)
    note_type: Mapped[str] = mapped_column(String(80), index=True, nullable=False, default="smart_note")
    content: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    author: Mapped[str | None] = mapped_column(String(160), index=True)
    status: Mapped[str] = mapped_column(String(60), index=True, nullable=False, default="active")
    tags: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    keywords: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    concepts: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    action_items: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    related_note_ids: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    related_document_ids: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    related_graph_node_ids: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    duplicate_note_ids: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    duplicate_key: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(JSON, default=list, nullable=False)
    is_pinned: Mapped[bool] = mapped_column(Boolean, index=True, nullable=False, default=False)
    pinned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    note_date: Mapped[date | None] = mapped_column(Date, index=True, nullable=True)
    metadata_json: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)

    owner: Mapped[User | None] = relationship("User")
    project: Mapped[Project | None] = relationship("Project", back_populates="notes")
    collection: Mapped[Collection | None] = relationship("Collection")


class Bookmark(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "bookmarks"

    owner_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    collection_id: Mapped[str | None] = mapped_column(ForeignKey("collections.id", ondelete="SET NULL"), index=True)
    project_id: Mapped[str | None] = mapped_column(ForeignKey("projects.id", ondelete="SET NULL"), index=True)
    target_type: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    target_id: Mapped[str | None] = mapped_column(String(80), index=True)
    title: Mapped[str] = mapped_column(String(220), index=True, nullable=False)
    url: Mapped[str | None] = mapped_column(Text, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    source_title: Mapped[str | None] = mapped_column(String(220), nullable=True)
    category: Mapped[str] = mapped_column(String(120), index=True, nullable=False, default="Knowledge")
    tags: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    metadata_json: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)

    owner: Mapped[User | None] = relationship("User")
    collection: Mapped[Collection | None] = relationship("Collection")
    project: Mapped[Project | None] = relationship("Project")


class WorkspaceTask(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "workspace_tasks"

    owner_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    project_id: Mapped[str | None] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    session_id: Mapped[str | None] = mapped_column(ForeignKey("research_sessions.id", ondelete="SET NULL"), index=True)
    parent_task_id: Mapped[str | None] = mapped_column(
        ForeignKey("workspace_tasks.id", ondelete="SET NULL"),
        index=True,
    )
    title: Mapped[str] = mapped_column(String(180), index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    task_type: Mapped[str] = mapped_column(String(80), index=True, nullable=False, default="research")
    status: Mapped[str] = mapped_column(String(60), index=True, nullable=False, default="pending")
    priority: Mapped[str] = mapped_column(String(40), index=True, nullable=False, default="medium")
    checklist: Mapped[list[dict[str, object]]] = mapped_column(JSON, default=list, nullable=False)
    tags: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    related_note_ids: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    related_document_ids: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    metadata_json: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)

    owner: Mapped[User | None] = relationship("User")
    project: Mapped[Project | None] = relationship("Project", back_populates="tasks")
    session: Mapped[ResearchSession | None] = relationship("ResearchSession", back_populates="tasks")


class ResearchSession(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "research_sessions"

    owner_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    project_id: Mapped[str | None] = mapped_column(ForeignKey("projects.id", ondelete="SET NULL"), index=True)
    title: Mapped[str] = mapped_column(String(180), index=True, nullable=False)
    objective: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(60), index=True, nullable=False, default="active")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    active_concepts: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    recent_document_ids: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    recent_note_ids: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    search_history: Mapped[list[dict[str, object]]] = mapped_column(JSON, default=list, nullable=False)
    ai_conversation_refs: Mapped[list[dict[str, object]]] = mapped_column(JSON, default=list, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False, default="")
    memory_snapshot: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)
    metadata_json: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)

    owner: Mapped[User | None] = relationship("User")
    project: Mapped[Project | None] = relationship("Project")
    tasks: Mapped[list[WorkspaceTask]] = relationship("WorkspaceTask", back_populates="session", lazy="selectin")


class CanvasObject(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "canvas_objects"

    owner_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    project_id: Mapped[str | None] = mapped_column(ForeignKey("projects.id", ondelete="SET NULL"), index=True)
    session_id: Mapped[str | None] = mapped_column(ForeignKey("research_sessions.id", ondelete="SET NULL"), index=True)
    canvas_id: Mapped[str] = mapped_column(String(80), index=True, nullable=False, default="default")
    object_type: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), index=True, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    target_type: Mapped[str | None] = mapped_column(String(80), index=True)
    target_id: Mapped[str | None] = mapped_column(String(80), index=True)
    url: Mapped[str | None] = mapped_column(Text, nullable=True)
    position_x: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    position_y: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    width: Mapped[float] = mapped_column(Float, nullable=False, default=320.0)
    height: Mapped[float] = mapped_column(Float, nullable=False, default=220.0)
    z_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    style: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)
    data: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)
    connections: Mapped[list[dict[str, object]]] = mapped_column(JSON, default=list, nullable=False)
    metadata_json: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)

    owner: Mapped[User | None] = relationship("User")
    project: Mapped[Project | None] = relationship("Project")
    session: Mapped[ResearchSession | None] = relationship("ResearchSession")


class WorkspaceSettings(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "workspace_settings"
    __table_args__ = (UniqueConstraint("owner_user_id", name="uq_workspace_settings_owner_user_id"),)

    owner_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    default_project_id: Mapped[str | None] = mapped_column(ForeignKey("projects.id", ondelete="SET NULL"), index=True)
    favorite_topics: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    frequently_used_concepts: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    recent_research: Mapped[list[dict[str, object]]] = mapped_column(JSON, default=list, nullable=False)
    reading_history: Mapped[list[dict[str, object]]] = mapped_column(JSON, default=list, nullable=False)
    search_history: Mapped[list[dict[str, object]]] = mapped_column(JSON, default=list, nullable=False)
    bookmarks_snapshot: Mapped[list[dict[str, object]]] = mapped_column(JSON, default=list, nullable=False)
    recent_ai_conversations: Mapped[list[dict[str, object]]] = mapped_column(JSON, default=list, nullable=False)
    preferences: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)
    layout: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)
    memory_profile: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)

    owner: Mapped[User | None] = relationship("User")
    default_project: Mapped[Project | None] = relationship("Project")
