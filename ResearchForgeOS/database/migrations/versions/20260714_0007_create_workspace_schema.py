"""create workspace and second brain schema

Revision ID: 20260714_0007
Revises: 20260714_0006
Create Date: 2026-07-14 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260714_0007"
down_revision: str | None = "20260714_0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "projects",
        sa.Column("owner_user_id", sa.String(length=36), nullable=True),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=60), nullable=False),
        sa.Column("research_domain", sa.String(length=140), nullable=True),
        sa.Column("goals", sa.JSON(), nullable=False),
        sa.Column("milestones", sa.JSON(), nullable=False),
        sa.Column("resources", sa.JSON(), nullable=False),
        sa.Column("progress_percent", sa.Float(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("target_date", sa.Date(), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["owner_user_id"],
            ["users.id"],
            name=op.f("fk_projects_owner_user_id_users"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_projects")),
    )
    op.create_index(op.f("ix_projects_owner_user_id"), "projects", ["owner_user_id"])
    op.create_index(op.f("ix_projects_research_domain"), "projects", ["research_domain"])
    op.create_index(op.f("ix_projects_status"), "projects", ["status"])
    op.create_index(op.f("ix_projects_title"), "projects", ["title"])

    op.create_table(
        "collections",
        sa.Column("owner_user_id", sa.String(length=36), nullable=True),
        sa.Column("parent_collection_id", sa.String(length=36), nullable=True),
        sa.Column("project_id", sa.String(length=36), nullable=True),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("collection_type", sa.String(length=80), nullable=False),
        sa.Column("color", sa.String(length=24), nullable=False),
        sa.Column("icon", sa.String(length=80), nullable=False),
        sa.Column("tags", sa.JSON(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["owner_user_id"],
            ["users.id"],
            name=op.f("fk_collections_owner_user_id_users"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["parent_collection_id"],
            ["collections.id"],
            name=op.f("fk_collections_parent_collection_id_collections"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            name=op.f("fk_collections_project_id_projects"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_collections")),
    )
    op.create_index(op.f("ix_collections_collection_type"), "collections", ["collection_type"])
    op.create_index(op.f("ix_collections_name"), "collections", ["name"])
    op.create_index(op.f("ix_collections_owner_user_id"), "collections", ["owner_user_id"])
    op.create_index(op.f("ix_collections_parent_collection_id"), "collections", ["parent_collection_id"])
    op.create_index(op.f("ix_collections_project_id"), "collections", ["project_id"])

    op.create_table(
        "research_sessions",
        sa.Column("owner_user_id", sa.String(length=36), nullable=True),
        sa.Column("project_id", sa.String(length=36), nullable=True),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("objective", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=60), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("active_concepts", sa.JSON(), nullable=False),
        sa.Column("recent_document_ids", sa.JSON(), nullable=False),
        sa.Column("recent_note_ids", sa.JSON(), nullable=False),
        sa.Column("search_history", sa.JSON(), nullable=False),
        sa.Column("ai_conversation_refs", sa.JSON(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("memory_snapshot", sa.JSON(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["owner_user_id"],
            ["users.id"],
            name=op.f("fk_research_sessions_owner_user_id_users"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            name=op.f("fk_research_sessions_project_id_projects"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_research_sessions")),
    )
    op.create_index(op.f("ix_research_sessions_owner_user_id"), "research_sessions", ["owner_user_id"])
    op.create_index(op.f("ix_research_sessions_project_id"), "research_sessions", ["project_id"])
    op.create_index(op.f("ix_research_sessions_started_at"), "research_sessions", ["started_at"])
    op.create_index(op.f("ix_research_sessions_status"), "research_sessions", ["status"])
    op.create_index(op.f("ix_research_sessions_title"), "research_sessions", ["title"])

    op.create_table(
        "notes",
        sa.Column("owner_user_id", sa.String(length=36), nullable=True),
        sa.Column("project_id", sa.String(length=36), nullable=True),
        sa.Column("collection_id", sa.String(length=36), nullable=True),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("slug", sa.String(length=220), nullable=False),
        sa.Column("note_type", sa.String(length=80), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("category", sa.String(length=120), nullable=False),
        sa.Column("author", sa.String(length=160), nullable=True),
        sa.Column("status", sa.String(length=60), nullable=False),
        sa.Column("tags", sa.JSON(), nullable=False),
        sa.Column("keywords", sa.JSON(), nullable=False),
        sa.Column("concepts", sa.JSON(), nullable=False),
        sa.Column("action_items", sa.JSON(), nullable=False),
        sa.Column("related_note_ids", sa.JSON(), nullable=False),
        sa.Column("related_document_ids", sa.JSON(), nullable=False),
        sa.Column("related_graph_node_ids", sa.JSON(), nullable=False),
        sa.Column("duplicate_note_ids", sa.JSON(), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("duplicate_key", sa.String(length=64), nullable=False),
        sa.Column("embedding", sa.JSON(), nullable=False),
        sa.Column("is_pinned", sa.Boolean(), nullable=False),
        sa.Column("pinned_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("note_date", sa.Date(), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["collection_id"],
            ["collections.id"],
            name=op.f("fk_notes_collection_id_collections"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["owner_user_id"],
            ["users.id"],
            name=op.f("fk_notes_owner_user_id_users"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            name=op.f("fk_notes_project_id_projects"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_notes")),
        sa.UniqueConstraint("owner_user_id", "content_hash", name="uq_notes_owner_content_hash"),
    )
    op.create_index(op.f("ix_notes_author"), "notes", ["author"])
    op.create_index(op.f("ix_notes_category"), "notes", ["category"])
    op.create_index(op.f("ix_notes_collection_id"), "notes", ["collection_id"])
    op.create_index(op.f("ix_notes_content_hash"), "notes", ["content_hash"])
    op.create_index(op.f("ix_notes_duplicate_key"), "notes", ["duplicate_key"])
    op.create_index(op.f("ix_notes_is_pinned"), "notes", ["is_pinned"])
    op.create_index(op.f("ix_notes_note_date"), "notes", ["note_date"])
    op.create_index(op.f("ix_notes_note_type"), "notes", ["note_type"])
    op.create_index(op.f("ix_notes_owner_user_id"), "notes", ["owner_user_id"])
    op.create_index(op.f("ix_notes_project_id"), "notes", ["project_id"])
    op.create_index(op.f("ix_notes_slug"), "notes", ["slug"])
    op.create_index(op.f("ix_notes_status"), "notes", ["status"])
    op.create_index(op.f("ix_notes_title"), "notes", ["title"])

    op.create_table(
        "bookmarks",
        sa.Column("owner_user_id", sa.String(length=36), nullable=True),
        sa.Column("collection_id", sa.String(length=36), nullable=True),
        sa.Column("project_id", sa.String(length=36), nullable=True),
        sa.Column("target_type", sa.String(length=80), nullable=False),
        sa.Column("target_id", sa.String(length=80), nullable=True),
        sa.Column("title", sa.String(length=220), nullable=False),
        sa.Column("url", sa.Text(), nullable=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("source_title", sa.String(length=220), nullable=True),
        sa.Column("category", sa.String(length=120), nullable=False),
        sa.Column("tags", sa.JSON(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["collection_id"],
            ["collections.id"],
            name=op.f("fk_bookmarks_collection_id_collections"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["owner_user_id"],
            ["users.id"],
            name=op.f("fk_bookmarks_owner_user_id_users"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            name=op.f("fk_bookmarks_project_id_projects"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_bookmarks")),
    )
    op.create_index(op.f("ix_bookmarks_category"), "bookmarks", ["category"])
    op.create_index(op.f("ix_bookmarks_collection_id"), "bookmarks", ["collection_id"])
    op.create_index(op.f("ix_bookmarks_owner_user_id"), "bookmarks", ["owner_user_id"])
    op.create_index(op.f("ix_bookmarks_project_id"), "bookmarks", ["project_id"])
    op.create_index(op.f("ix_bookmarks_target_id"), "bookmarks", ["target_id"])
    op.create_index(op.f("ix_bookmarks_target_type"), "bookmarks", ["target_type"])
    op.create_index(op.f("ix_bookmarks_title"), "bookmarks", ["title"])

    op.create_table(
        "workspace_tasks",
        sa.Column("owner_user_id", sa.String(length=36), nullable=True),
        sa.Column("project_id", sa.String(length=36), nullable=True),
        sa.Column("session_id", sa.String(length=36), nullable=True),
        sa.Column("parent_task_id", sa.String(length=36), nullable=True),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("task_type", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=60), nullable=False),
        sa.Column("priority", sa.String(length=40), nullable=False),
        sa.Column("checklist", sa.JSON(), nullable=False),
        sa.Column("tags", sa.JSON(), nullable=False),
        sa.Column("related_note_ids", sa.JSON(), nullable=False),
        sa.Column("related_document_ids", sa.JSON(), nullable=False),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["owner_user_id"],
            ["users.id"],
            name=op.f("fk_workspace_tasks_owner_user_id_users"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["parent_task_id"],
            ["workspace_tasks.id"],
            name=op.f("fk_workspace_tasks_parent_task_id_workspace_tasks"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            name=op.f("fk_workspace_tasks_project_id_projects"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["research_sessions.id"],
            name=op.f("fk_workspace_tasks_session_id_research_sessions"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_workspace_tasks")),
    )
    op.create_index(op.f("ix_workspace_tasks_due_at"), "workspace_tasks", ["due_at"])
    op.create_index(op.f("ix_workspace_tasks_owner_user_id"), "workspace_tasks", ["owner_user_id"])
    op.create_index(op.f("ix_workspace_tasks_parent_task_id"), "workspace_tasks", ["parent_task_id"])
    op.create_index(op.f("ix_workspace_tasks_priority"), "workspace_tasks", ["priority"])
    op.create_index(op.f("ix_workspace_tasks_project_id"), "workspace_tasks", ["project_id"])
    op.create_index(op.f("ix_workspace_tasks_session_id"), "workspace_tasks", ["session_id"])
    op.create_index(op.f("ix_workspace_tasks_status"), "workspace_tasks", ["status"])
    op.create_index(op.f("ix_workspace_tasks_task_type"), "workspace_tasks", ["task_type"])
    op.create_index(op.f("ix_workspace_tasks_title"), "workspace_tasks", ["title"])

    op.create_table(
        "canvas_objects",
        sa.Column("owner_user_id", sa.String(length=36), nullable=True),
        sa.Column("project_id", sa.String(length=36), nullable=True),
        sa.Column("session_id", sa.String(length=36), nullable=True),
        sa.Column("canvas_id", sa.String(length=80), nullable=False),
        sa.Column("object_type", sa.String(length=80), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("target_type", sa.String(length=80), nullable=True),
        sa.Column("target_id", sa.String(length=80), nullable=True),
        sa.Column("url", sa.Text(), nullable=True),
        sa.Column("position_x", sa.Float(), nullable=False),
        sa.Column("position_y", sa.Float(), nullable=False),
        sa.Column("width", sa.Float(), nullable=False),
        sa.Column("height", sa.Float(), nullable=False),
        sa.Column("z_index", sa.Integer(), nullable=False),
        sa.Column("style", sa.JSON(), nullable=False),
        sa.Column("data", sa.JSON(), nullable=False),
        sa.Column("connections", sa.JSON(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["owner_user_id"],
            ["users.id"],
            name=op.f("fk_canvas_objects_owner_user_id_users"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            name=op.f("fk_canvas_objects_project_id_projects"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["research_sessions.id"],
            name=op.f("fk_canvas_objects_session_id_research_sessions"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_canvas_objects")),
    )
    op.create_index(op.f("ix_canvas_objects_canvas_id"), "canvas_objects", ["canvas_id"])
    op.create_index(op.f("ix_canvas_objects_object_type"), "canvas_objects", ["object_type"])
    op.create_index(op.f("ix_canvas_objects_owner_user_id"), "canvas_objects", ["owner_user_id"])
    op.create_index(op.f("ix_canvas_objects_project_id"), "canvas_objects", ["project_id"])
    op.create_index(op.f("ix_canvas_objects_session_id"), "canvas_objects", ["session_id"])
    op.create_index(op.f("ix_canvas_objects_target_id"), "canvas_objects", ["target_id"])
    op.create_index(op.f("ix_canvas_objects_target_type"), "canvas_objects", ["target_type"])
    op.create_index(op.f("ix_canvas_objects_title"), "canvas_objects", ["title"])

    op.create_table(
        "workspace_settings",
        sa.Column("owner_user_id", sa.String(length=36), nullable=True),
        sa.Column("default_project_id", sa.String(length=36), nullable=True),
        sa.Column("favorite_topics", sa.JSON(), nullable=False),
        sa.Column("frequently_used_concepts", sa.JSON(), nullable=False),
        sa.Column("recent_research", sa.JSON(), nullable=False),
        sa.Column("reading_history", sa.JSON(), nullable=False),
        sa.Column("search_history", sa.JSON(), nullable=False),
        sa.Column("bookmarks_snapshot", sa.JSON(), nullable=False),
        sa.Column("recent_ai_conversations", sa.JSON(), nullable=False),
        sa.Column("preferences", sa.JSON(), nullable=False),
        sa.Column("layout", sa.JSON(), nullable=False),
        sa.Column("memory_profile", sa.JSON(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["default_project_id"],
            ["projects.id"],
            name=op.f("fk_workspace_settings_default_project_id_projects"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["owner_user_id"],
            ["users.id"],
            name=op.f("fk_workspace_settings_owner_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_workspace_settings")),
        sa.UniqueConstraint("owner_user_id", name="uq_workspace_settings_owner_user_id"),
    )
    op.create_index(op.f("ix_workspace_settings_default_project_id"), "workspace_settings", ["default_project_id"])
    op.create_index(op.f("ix_workspace_settings_owner_user_id"), "workspace_settings", ["owner_user_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_workspace_settings_owner_user_id"), table_name="workspace_settings")
    op.drop_index(op.f("ix_workspace_settings_default_project_id"), table_name="workspace_settings")
    op.drop_table("workspace_settings")

    op.drop_index(op.f("ix_canvas_objects_title"), table_name="canvas_objects")
    op.drop_index(op.f("ix_canvas_objects_target_type"), table_name="canvas_objects")
    op.drop_index(op.f("ix_canvas_objects_target_id"), table_name="canvas_objects")
    op.drop_index(op.f("ix_canvas_objects_session_id"), table_name="canvas_objects")
    op.drop_index(op.f("ix_canvas_objects_project_id"), table_name="canvas_objects")
    op.drop_index(op.f("ix_canvas_objects_owner_user_id"), table_name="canvas_objects")
    op.drop_index(op.f("ix_canvas_objects_object_type"), table_name="canvas_objects")
    op.drop_index(op.f("ix_canvas_objects_canvas_id"), table_name="canvas_objects")
    op.drop_table("canvas_objects")

    op.drop_index(op.f("ix_workspace_tasks_title"), table_name="workspace_tasks")
    op.drop_index(op.f("ix_workspace_tasks_task_type"), table_name="workspace_tasks")
    op.drop_index(op.f("ix_workspace_tasks_status"), table_name="workspace_tasks")
    op.drop_index(op.f("ix_workspace_tasks_session_id"), table_name="workspace_tasks")
    op.drop_index(op.f("ix_workspace_tasks_project_id"), table_name="workspace_tasks")
    op.drop_index(op.f("ix_workspace_tasks_priority"), table_name="workspace_tasks")
    op.drop_index(op.f("ix_workspace_tasks_parent_task_id"), table_name="workspace_tasks")
    op.drop_index(op.f("ix_workspace_tasks_owner_user_id"), table_name="workspace_tasks")
    op.drop_index(op.f("ix_workspace_tasks_due_at"), table_name="workspace_tasks")
    op.drop_table("workspace_tasks")

    op.drop_index(op.f("ix_bookmarks_title"), table_name="bookmarks")
    op.drop_index(op.f("ix_bookmarks_target_type"), table_name="bookmarks")
    op.drop_index(op.f("ix_bookmarks_target_id"), table_name="bookmarks")
    op.drop_index(op.f("ix_bookmarks_project_id"), table_name="bookmarks")
    op.drop_index(op.f("ix_bookmarks_owner_user_id"), table_name="bookmarks")
    op.drop_index(op.f("ix_bookmarks_collection_id"), table_name="bookmarks")
    op.drop_index(op.f("ix_bookmarks_category"), table_name="bookmarks")
    op.drop_table("bookmarks")

    op.drop_index(op.f("ix_notes_title"), table_name="notes")
    op.drop_index(op.f("ix_notes_status"), table_name="notes")
    op.drop_index(op.f("ix_notes_slug"), table_name="notes")
    op.drop_index(op.f("ix_notes_project_id"), table_name="notes")
    op.drop_index(op.f("ix_notes_owner_user_id"), table_name="notes")
    op.drop_index(op.f("ix_notes_note_type"), table_name="notes")
    op.drop_index(op.f("ix_notes_note_date"), table_name="notes")
    op.drop_index(op.f("ix_notes_is_pinned"), table_name="notes")
    op.drop_index(op.f("ix_notes_duplicate_key"), table_name="notes")
    op.drop_index(op.f("ix_notes_content_hash"), table_name="notes")
    op.drop_index(op.f("ix_notes_collection_id"), table_name="notes")
    op.drop_index(op.f("ix_notes_category"), table_name="notes")
    op.drop_index(op.f("ix_notes_author"), table_name="notes")
    op.drop_table("notes")

    op.drop_index(op.f("ix_research_sessions_title"), table_name="research_sessions")
    op.drop_index(op.f("ix_research_sessions_status"), table_name="research_sessions")
    op.drop_index(op.f("ix_research_sessions_started_at"), table_name="research_sessions")
    op.drop_index(op.f("ix_research_sessions_project_id"), table_name="research_sessions")
    op.drop_index(op.f("ix_research_sessions_owner_user_id"), table_name="research_sessions")
    op.drop_table("research_sessions")

    op.drop_index(op.f("ix_collections_project_id"), table_name="collections")
    op.drop_index(op.f("ix_collections_parent_collection_id"), table_name="collections")
    op.drop_index(op.f("ix_collections_owner_user_id"), table_name="collections")
    op.drop_index(op.f("ix_collections_name"), table_name="collections")
    op.drop_index(op.f("ix_collections_collection_type"), table_name="collections")
    op.drop_table("collections")

    op.drop_index(op.f("ix_projects_title"), table_name="projects")
    op.drop_index(op.f("ix_projects_status"), table_name="projects")
    op.drop_index(op.f("ix_projects_research_domain"), table_name="projects")
    op.drop_index(op.f("ix_projects_owner_user_id"), table_name="projects")
    op.drop_table("projects")
