from datetime import date, datetime
from typing import Any, Literal

from pydantic import Field
from workspace_engine.types import ChecklistType, NoteType, SearchMode, WritingMode

from backend.schemas.common import APIModel, TimestampedRead


class CollectionCreate(APIModel):
    name: str = Field(min_length=1, max_length=160)
    description: str = Field(default="", max_length=4000)
    collection_type: str = Field(default="research", min_length=1, max_length=80)
    parent_collection_id: str | None = None
    project_id: str | None = None
    color: str = Field(default="#2563eb", max_length=24)
    icon: str = Field(default="folder", max_length=80)
    tags: list[str] = Field(default_factory=list, max_length=30)
    metadata_json: dict[str, Any] = Field(default_factory=dict)


class CollectionUpdate(APIModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    description: str | None = Field(default=None, max_length=4000)
    collection_type: str | None = Field(default=None, min_length=1, max_length=80)
    parent_collection_id: str | None = None
    project_id: str | None = None
    color: str | None = Field(default=None, max_length=24)
    icon: str | None = Field(default=None, max_length=80)
    tags: list[str] | None = Field(default=None, max_length=30)
    metadata_json: dict[str, Any] | None = None


class CollectionRead(TimestampedRead):
    id: str
    owner_user_id: str | None
    parent_collection_id: str | None
    project_id: str | None
    name: str
    description: str
    collection_type: str
    color: str
    icon: str
    tags: list[str]
    metadata_json: dict[str, Any]


class NoteCreate(APIModel):
    content: str = Field(min_length=1, max_length=200_000)
    title: str | None = Field(default=None, max_length=180)
    note_type: NoteType = NoteType.SMART_NOTE
    category: str | None = Field(default=None, max_length=120)
    author: str | None = Field(default=None, max_length=160)
    project_id: str | None = None
    collection_id: str | None = None
    tags: list[str] = Field(default_factory=list, max_length=30)
    is_pinned: bool = False
    note_date: date | None = None
    metadata_json: dict[str, Any] = Field(default_factory=dict)


class NoteUpdate(APIModel):
    content: str | None = Field(default=None, min_length=1, max_length=200_000)
    title: str | None = Field(default=None, min_length=1, max_length=180)
    note_type: NoteType | None = None
    category: str | None = Field(default=None, max_length=120)
    author: str | None = Field(default=None, max_length=160)
    project_id: str | None = None
    collection_id: str | None = None
    tags: list[str] | None = Field(default=None, max_length=30)
    is_pinned: bool | None = None
    note_date: date | None = None
    metadata_json: dict[str, Any] | None = None


class NoteRead(TimestampedRead):
    id: str
    owner_user_id: str | None
    project_id: str | None
    collection_id: str | None
    title: str
    slug: str
    note_type: str
    content: str
    summary: str
    category: str
    author: str | None
    status: str
    tags: list[str]
    keywords: list[str]
    concepts: list[str]
    action_items: list[str]
    related_note_ids: list[str]
    related_document_ids: list[str]
    related_graph_node_ids: list[str]
    duplicate_note_ids: list[str]
    content_hash: str
    duplicate_key: str
    is_pinned: bool
    pinned_at: datetime | None
    note_date: date | None
    metadata_json: dict[str, Any]


class NoteSearchRequest(APIModel):
    query: str = Field(default="", max_length=1000)
    mode: SearchMode = SearchMode.HYBRID
    tags: list[str] = Field(default_factory=list, max_length=30)
    project_id: str | None = None
    collection_id: str | None = None
    author: str | None = Field(default=None, max_length=160)
    concepts: list[str] = Field(default_factory=list, max_length=30)
    date_from: date | None = None
    date_to: date | None = None
    limit: int = Field(default=25, ge=1, le=100)


class NoteSearchResultRead(APIModel):
    note_id: str
    title: str
    summary: str
    score: float
    matched_fields: list[str]
    tags: list[str]
    concepts: list[str]
    project_id: str | None
    collection_id: str | None


class NoteSearchResponse(APIModel):
    query: str
    mode: str
    results: list[NoteSearchResultRead]


class NoteImproveRequest(APIModel):
    mode: Literal["clarify", "structure", "actionable"] = "clarify"


class NoteImproveResponse(APIModel):
    note_id: str
    improved_content: str
    analysis: dict[str, Any]


class WritingAssistantRequest(APIModel):
    text: str = Field(min_length=1, max_length=80_000)
    mode: WritingMode
    citation_sources: list[dict[str, str]] = Field(default_factory=list, max_length=50)


class WritingAssistantResponse(APIModel):
    mode: str
    original_text: str
    output_text: str
    changes: list[str]
    citations: list[str]
    metadata: dict[str, Any]


class BookmarkCreate(APIModel):
    target_type: str = Field(min_length=1, max_length=80)
    target_id: str | None = Field(default=None, max_length=80)
    title: str = Field(min_length=1, max_length=220)
    url: str | None = Field(default=None, max_length=2000)
    description: str = Field(default="", max_length=4000)
    source_title: str | None = Field(default=None, max_length=220)
    category: str = Field(default="Knowledge", max_length=120)
    tags: list[str] = Field(default_factory=list, max_length=30)
    collection_id: str | None = None
    project_id: str | None = None
    metadata_json: dict[str, Any] = Field(default_factory=dict)


class BookmarkUpdate(APIModel):
    title: str | None = Field(default=None, min_length=1, max_length=220)
    url: str | None = Field(default=None, max_length=2000)
    description: str | None = Field(default=None, max_length=4000)
    source_title: str | None = Field(default=None, max_length=220)
    category: str | None = Field(default=None, max_length=120)
    tags: list[str] | None = Field(default=None, max_length=30)
    collection_id: str | None = None
    project_id: str | None = None
    metadata_json: dict[str, Any] | None = None


class BookmarkRead(TimestampedRead):
    id: str
    owner_user_id: str | None
    collection_id: str | None
    project_id: str | None
    target_type: str
    target_id: str | None
    title: str
    url: str | None
    description: str
    source_title: str | None
    category: str
    tags: list[str]
    metadata_json: dict[str, Any]


class ProjectCreate(APIModel):
    title: str = Field(min_length=1, max_length=180)
    description: str = Field(default="", max_length=8000)
    status: str = Field(default="active", max_length=60)
    research_domain: str | None = Field(default=None, max_length=140)
    goals: list[str] = Field(default_factory=list, max_length=40)
    milestones: list[dict[str, Any]] = Field(default_factory=list, max_length=100)
    resources: list[dict[str, Any]] = Field(default_factory=list, max_length=100)
    progress_percent: float = Field(default=0.0, ge=0.0, le=100.0)
    start_date: date | None = None
    target_date: date | None = None
    metadata_json: dict[str, Any] = Field(default_factory=dict)


class ProjectUpdate(APIModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    description: str | None = Field(default=None, max_length=8000)
    status: str | None = Field(default=None, max_length=60)
    research_domain: str | None = Field(default=None, max_length=140)
    goals: list[str] | None = Field(default=None, max_length=40)
    milestones: list[dict[str, Any]] | None = Field(default=None, max_length=100)
    resources: list[dict[str, Any]] | None = Field(default=None, max_length=100)
    progress_percent: float | None = Field(default=None, ge=0.0, le=100.0)
    start_date: date | None = None
    target_date: date | None = None
    metadata_json: dict[str, Any] | None = None


class ProjectRead(TimestampedRead):
    id: str
    owner_user_id: str | None
    title: str
    description: str
    status: str
    research_domain: str | None
    goals: list[str]
    milestones: list[dict[str, Any]]
    resources: list[dict[str, Any]]
    progress_percent: float
    start_date: date | None
    target_date: date | None
    metadata_json: dict[str, Any]


class WorkspaceTaskCreate(APIModel):
    title: str = Field(min_length=1, max_length=180)
    description: str = Field(default="", max_length=8000)
    task_type: str = Field(default="research", max_length=80)
    status: str = Field(default="pending", max_length=60)
    priority: str = Field(default="medium", max_length=40)
    project_id: str | None = None
    session_id: str | None = None
    parent_task_id: str | None = None
    checklist: list[dict[str, Any]] = Field(default_factory=list, max_length=100)
    tags: list[str] = Field(default_factory=list, max_length=30)
    related_note_ids: list[str] = Field(default_factory=list, max_length=100)
    related_document_ids: list[str] = Field(default_factory=list, max_length=100)
    due_at: datetime | None = None
    metadata_json: dict[str, Any] = Field(default_factory=dict)


class WorkspaceTaskUpdate(APIModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    description: str | None = Field(default=None, max_length=8000)
    task_type: str | None = Field(default=None, max_length=80)
    status: str | None = Field(default=None, max_length=60)
    priority: str | None = Field(default=None, max_length=40)
    project_id: str | None = None
    session_id: str | None = None
    parent_task_id: str | None = None
    checklist: list[dict[str, Any]] | None = Field(default=None, max_length=100)
    tags: list[str] | None = Field(default=None, max_length=30)
    related_note_ids: list[str] | None = Field(default=None, max_length=100)
    related_document_ids: list[str] | None = Field(default=None, max_length=100)
    due_at: datetime | None = None
    metadata_json: dict[str, Any] | None = None


class WorkspaceTaskRead(TimestampedRead):
    id: str
    owner_user_id: str | None
    project_id: str | None
    session_id: str | None
    parent_task_id: str | None
    title: str
    description: str
    task_type: str
    status: str
    priority: str
    checklist: list[dict[str, Any]]
    tags: list[str]
    related_note_ids: list[str]
    related_document_ids: list[str]
    due_at: datetime | None
    completed_at: datetime | None
    metadata_json: dict[str, Any]


class TaskAssistantRequest(APIModel):
    prompt: str = Field(min_length=1, max_length=8000)
    plan_type: ChecklistType
    concepts: list[str] = Field(default_factory=list, max_length=30)
    resources: list[str] = Field(default_factory=list, max_length=30)
    create_tasks: bool = False
    project_id: str | None = None


class TaskAssistantResponse(APIModel):
    plan_type: str
    title: str
    overview: str
    checklist: list[dict[str, Any]]
    estimated_days: int
    milestones: list[str]
    resources: list[str]
    created_task_ids: list[str]
    metadata: dict[str, Any]


class ResearchSessionCreate(APIModel):
    title: str = Field(min_length=1, max_length=180)
    objective: str = Field(default="", max_length=8000)
    project_id: str | None = None
    active_concepts: list[str] = Field(default_factory=list, max_length=40)
    recent_document_ids: list[str] = Field(default_factory=list, max_length=100)
    recent_note_ids: list[str] = Field(default_factory=list, max_length=100)
    metadata_json: dict[str, Any] = Field(default_factory=dict)


class ResearchSessionUpdate(APIModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    objective: str | None = Field(default=None, max_length=8000)
    status: str | None = Field(default=None, max_length=60)
    project_id: str | None = None
    active_concepts: list[str] | None = Field(default=None, max_length=40)
    recent_document_ids: list[str] | None = Field(default=None, max_length=100)
    recent_note_ids: list[str] | None = Field(default=None, max_length=100)
    search_history: list[dict[str, Any]] | None = Field(default=None, max_length=500)
    ai_conversation_refs: list[dict[str, Any]] | None = Field(default=None, max_length=500)
    summary: str | None = Field(default=None, max_length=12000)
    memory_snapshot: dict[str, Any] | None = None
    metadata_json: dict[str, Any] | None = None


class ResearchSessionRead(TimestampedRead):
    id: str
    owner_user_id: str | None
    project_id: str | None
    title: str
    objective: str
    status: str
    started_at: datetime
    ended_at: datetime | None
    active_concepts: list[str]
    recent_document_ids: list[str]
    recent_note_ids: list[str]
    search_history: list[dict[str, Any]]
    ai_conversation_refs: list[dict[str, Any]]
    summary: str
    memory_snapshot: dict[str, Any]
    metadata_json: dict[str, Any]


class CanvasObjectCreate(APIModel):
    canvas_id: str = Field(default="default", min_length=1, max_length=80)
    object_type: str = Field(min_length=1, max_length=80)
    title: str = Field(min_length=1, max_length=180)
    content: str = Field(default="", max_length=120_000)
    target_type: str | None = Field(default=None, max_length=80)
    target_id: str | None = Field(default=None, max_length=80)
    url: str | None = Field(default=None, max_length=2000)
    project_id: str | None = None
    session_id: str | None = None
    position_x: float = 0.0
    position_y: float = 0.0
    width: float = Field(default=320.0, ge=40.0, le=4000.0)
    height: float = Field(default=220.0, ge=40.0, le=4000.0)
    z_index: int = 0
    style: dict[str, Any] = Field(default_factory=dict)
    data: dict[str, Any] = Field(default_factory=dict)
    connections: list[dict[str, Any]] = Field(default_factory=list, max_length=500)
    metadata_json: dict[str, Any] = Field(default_factory=dict)


class CanvasObjectUpdate(APIModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    content: str | None = Field(default=None, max_length=120_000)
    position_x: float | None = None
    position_y: float | None = None
    width: float | None = Field(default=None, ge=40.0, le=4000.0)
    height: float | None = Field(default=None, ge=40.0, le=4000.0)
    z_index: int | None = None
    style: dict[str, Any] | None = None
    data: dict[str, Any] | None = None
    connections: list[dict[str, Any]] | None = Field(default=None, max_length=500)
    metadata_json: dict[str, Any] | None = None


class CanvasConnectionRequest(APIModel):
    target_object_id: str
    relationship_type: str = Field(default="related_to", min_length=1, max_length=80)
    label: str = Field(default="Related", max_length=120)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CanvasObjectRead(TimestampedRead):
    id: str
    owner_user_id: str | None
    project_id: str | None
    session_id: str | None
    canvas_id: str
    object_type: str
    title: str
    content: str
    target_type: str | None
    target_id: str | None
    url: str | None
    position_x: float
    position_y: float
    width: float
    height: float
    z_index: int
    style: dict[str, Any]
    data: dict[str, Any]
    connections: list[dict[str, Any]]
    metadata_json: dict[str, Any]


class WorkspaceSettingsUpdate(APIModel):
    default_project_id: str | None = None
    favorite_topics: list[str] | None = Field(default=None, max_length=100)
    frequently_used_concepts: list[str] | None = Field(default=None, max_length=200)
    preferences: dict[str, Any] | None = None
    layout: dict[str, Any] | None = None
    memory_profile: dict[str, Any] | None = None


class WorkspaceSettingsRead(TimestampedRead):
    id: str
    owner_user_id: str | None
    default_project_id: str | None
    favorite_topics: list[str]
    frequently_used_concepts: list[str]
    recent_research: list[dict[str, Any]]
    reading_history: list[dict[str, Any]]
    search_history: list[dict[str, Any]]
    bookmarks_snapshot: list[dict[str, Any]]
    recent_ai_conversations: list[dict[str, Any]]
    preferences: dict[str, Any]
    layout: dict[str, Any]
    memory_profile: dict[str, Any]


class WorkspaceOverview(APIModel):
    recent_notes: list[NoteRead]
    pinned_notes: list[NoteRead]
    projects: list[ProjectRead]
    tasks: list[WorkspaceTaskRead]
    active_sessions: list[ResearchSessionRead]
    settings: WorkspaceSettingsRead


class TimelineItem(APIModel):
    item_type: str
    item_id: str
    title: str
    timestamp: datetime
    summary: str
    metadata: dict[str, Any]


class TimelineResponse(APIModel):
    items: list[TimelineItem]
