from __future__ import annotations

import logging
from datetime import UTC, datetime

from graph_engine.utils import node_size, stable_edge_key, stable_node_key
from retrieval.embedding import RetrievalEmbeddingService
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from workspace_engine import SmartNoteEngine, TaskAssistantEngine, WorkspaceSearchEngine, WritingAssistant
from workspace_engine.types import NoteAnalysis, SearchableNote
from workspace_engine.utils import dedupe, normalize_key, token_overlap

from backend.exceptions import ConflictError, NotFoundError, ValidationError
from backend.models.interactive_graph import GraphEdge, GraphNode
from backend.models.user import User
from backend.models.workspace import (
    Bookmark,
    CanvasObject,
    Collection,
    Note,
    Project,
    ResearchSession,
    WorkspaceSettings,
    WorkspaceTask,
)
from backend.repositories.document_repository import DocumentRepository
from backend.repositories.graph_repository import GraphEdgeRepository, GraphNodeRepository
from backend.repositories.workspace_repository import (
    BookmarkRepository,
    CanvasObjectRepository,
    CollectionRepository,
    NoteRepository,
    ProjectRepository,
    ResearchSessionRepository,
    WorkspaceSettingsRepository,
    WorkspaceTaskRepository,
)
from backend.schemas.workspace import (
    BookmarkCreate,
    BookmarkUpdate,
    CanvasConnectionRequest,
    CanvasObjectCreate,
    CanvasObjectUpdate,
    CollectionCreate,
    CollectionUpdate,
    NoteCreate,
    NoteImproveRequest,
    NoteImproveResponse,
    NoteSearchRequest,
    NoteSearchResponse,
    NoteUpdate,
    ProjectCreate,
    ProjectUpdate,
    ResearchSessionCreate,
    ResearchSessionUpdate,
    TaskAssistantRequest,
    TaskAssistantResponse,
    TimelineItem,
    TimelineResponse,
    WorkspaceOverview,
    WorkspaceSettingsUpdate,
    WorkspaceTaskCreate,
    WorkspaceTaskUpdate,
    WritingAssistantRequest,
    WritingAssistantResponse,
)
from backend.services.graph_service import InteractiveKnowledgeGraphService
from backend.utils.datetime import utc_now

logger = logging.getLogger(__name__)


class WorkspaceService:
    def __init__(
        self,
        session: Session,
        note_engine: SmartNoteEngine | None = None,
        search_engine: WorkspaceSearchEngine | None = None,
        writing_assistant: WritingAssistant | None = None,
        task_assistant: TaskAssistantEngine | None = None,
        embedding_service: RetrievalEmbeddingService | None = None,
    ) -> None:
        self.session = session
        self.note_engine = note_engine or SmartNoteEngine()
        self.search_engine = search_engine or WorkspaceSearchEngine()
        self.writing_assistant = writing_assistant or WritingAssistant()
        self.task_assistant = task_assistant or TaskAssistantEngine()
        self.embedding_service = embedding_service or RetrievalEmbeddingService()
        self.notes = NoteRepository(session)
        self.collections = CollectionRepository(session)
        self.bookmarks = BookmarkRepository(session)
        self.projects = ProjectRepository(session)
        self.tasks = WorkspaceTaskRepository(session)
        self.sessions = ResearchSessionRepository(session)
        self.canvas = CanvasObjectRepository(session)
        self.settings = WorkspaceSettingsRepository(session)
        self.documents = DocumentRepository(session)
        self.graph_nodes = GraphNodeRepository(session)
        self.graph_edges = GraphEdgeRepository(session)

    def overview(self, current_user: User) -> WorkspaceOverview:
        settings = self.get_settings(current_user)
        return WorkspaceOverview(
            recent_notes=list(self.notes.list_notes(owner_user_id=current_user.id, limit=8)),
            pinned_notes=list(self.notes.list_notes(owner_user_id=current_user.id, pinned=True, limit=8)),
            projects=list(self.projects.list_projects(owner_user_id=current_user.id, limit=8)),
            tasks=list(self.tasks.list_tasks(owner_user_id=current_user.id, status="pending", limit=12)),
            active_sessions=list(self.sessions.list_sessions(owner_user_id=current_user.id, status="active", limit=5)),
            settings=settings,
        )

    def get_settings(self, current_user: User) -> WorkspaceSettings:
        return self._get_or_create_settings(current_user, commit_on_create=True)

    def _get_or_create_settings(self, current_user: User, *, commit_on_create: bool) -> WorkspaceSettings:
        settings = self.settings.get_by_owner(current_user.id)
        if settings is not None:
            return settings
        settings = WorkspaceSettings(
            owner_user_id=current_user.id,
            favorite_topics=[],
            frequently_used_concepts=[],
            recent_research=[],
            reading_history=[],
            search_history=[],
            bookmarks_snapshot=[],
            recent_ai_conversations=[],
            preferences={"daily_note_enabled": True, "auto_link_notes": True, "default_search_mode": "hybrid"},
            layout={"default_canvas_id": "default", "sidebar_sections": ["notes", "projects", "bookmarks"]},
            memory_profile={"engine": "workspace_memory_v1"},
        )
        self.settings.add(settings)
        if commit_on_create:
            self.session.commit()
        else:
            self.session.flush()
        return settings

    def update_settings(self, payload: WorkspaceSettingsUpdate, current_user: User) -> WorkspaceSettings:
        settings = self.get_settings(current_user)
        data = payload.model_dump(exclude_unset=True)
        for field_name, value in data.items():
            if value is not None:
                setattr(settings, field_name, value)
        self.session.commit()
        return self.get_settings(current_user)

    def create_note(self, payload: NoteCreate, current_user: User) -> Note:
        self._validate_project(payload.project_id, current_user)
        self._validate_collection(payload.collection_id, current_user)
        analysis = self.note_engine.analyze(
            payload.content,
            title=payload.title,
            category=payload.category,
            tags=payload.tags,
        )
        existing_exact = self.notes.find_duplicates(
            owner_user_id=current_user.id,
            duplicate_key=analysis.duplicate_key,
        )
        related_notes = self.note_engine.related_notes(
            analysis,
            self._searchable_notes(current_user.id),
            limit=8,
        )
        duplicate_notes = self.note_engine.detect_duplicate_notes(
            analysis,
            self._searchable_notes(current_user.id),
            limit=5,
        )
        related_documents = self._related_documents(analysis)
        related_graph_nodes = self._related_graph_nodes(analysis)
        note = Note(
            owner_user_id=current_user.id,
            project_id=payload.project_id,
            collection_id=payload.collection_id,
            title=analysis.title,
            slug=self._slug(analysis.title),
            note_type=payload.note_type.value,
            content=payload.content,
            summary=analysis.summary,
            category=analysis.category,
            author=payload.author or current_user.full_name,
            status="active",
            tags=analysis.tags,
            keywords=analysis.keywords,
            concepts=analysis.concepts,
            action_items=analysis.action_items,
            related_note_ids=dedupe([str(item["note_id"]) for item in related_notes]),
            related_document_ids=dedupe([str(item["document_id"]) for item in related_documents]),
            related_graph_node_ids=dedupe([str(item["node_id"]) for item in related_graph_nodes]),
            duplicate_note_ids=dedupe([str(item["note_id"]) for item in duplicate_notes]),
            content_hash=analysis.content_hash,
            duplicate_key=analysis.duplicate_key,
            embedding=self.embedding_service.embed_text(f"{analysis.title}\n{payload.content}"),
            is_pinned=payload.is_pinned,
            pinned_at=utc_now() if payload.is_pinned else None,
            note_date=payload.note_date,
            metadata_json={
                **payload.metadata_json,
                "analysis": analysis.metadata,
                "related_notes": related_notes,
                "related_documents": related_documents,
                "related_graph_nodes": related_graph_nodes,
                "duplicate_candidates": duplicate_notes,
                "duplicate_key_matches": [note.id for note in existing_exact],
            },
        )
        try:
            self.notes.add(note)
            self._link_related_notes(note)
            self._sync_note_graph(note)
            self._update_memory_for_note(note, current_user)
            self.session.commit()
        except IntegrityError as exc:
            self.session.rollback()
            raise ConflictError("A note with the same content already exists.") from exc
        logger.info("Workspace note created", extra={"note_id": note.id, "user_id": current_user.id})
        loaded = self.notes.get_owned(note.id, current_user.id)
        if loaded is None:
            raise NotFoundError("Created note could not be loaded.")
        return loaded

    def list_notes(
        self,
        current_user: User,
        *,
        offset: int,
        limit: int,
        project_id: str | None = None,
        collection_id: str | None = None,
        pinned: bool | None = None,
        note_type: str | None = None,
    ) -> list[Note]:
        return list(
            self.notes.list_notes(
                owner_user_id=current_user.id,
                offset=offset,
                limit=limit,
                project_id=project_id,
                collection_id=collection_id,
                pinned=pinned,
                note_type=note_type,
            )
        )

    def get_note(self, note_id: str, current_user: User) -> Note:
        note = self.notes.get_owned(note_id, current_user.id)
        if note is None:
            raise NotFoundError("Workspace note was not found.")
        return note

    def update_note(self, note_id: str, payload: NoteUpdate, current_user: User) -> Note:
        note = self.get_note(note_id, current_user)
        data = payload.model_dump(exclude_unset=True)
        content_changed = "content" in data or "title" in data or "tags" in data or "category" in data
        if payload.project_id is not None:
            self._validate_project(payload.project_id, current_user)
        if payload.collection_id is not None:
            self._validate_collection(payload.collection_id, current_user)
        if content_changed:
            content = data.get("content") or note.content
            analysis = self.note_engine.analyze(
                str(content),
                title=data.get("title") or note.title,
                category=data.get("category") or note.category,
                tags=data.get("tags") or note.tags,
            )
            self._apply_analysis(note, analysis, str(content))
        for field_name, value in data.items():
            if field_name in {"content", "title", "category", "tags"}:
                continue
            if value is not None:
                setattr(note, field_name, value.value if hasattr(value, "value") else value)
        if "is_pinned" in data:
            note.pinned_at = utc_now() if note.is_pinned else None
        self._sync_note_graph(note)
        self._update_memory_for_note(note, current_user)
        self.session.commit()
        return self.get_note(note_id, current_user)

    def delete_note(self, note_id: str, current_user: User) -> None:
        note = self.get_note(note_id, current_user)
        self._delete_note_graph(note)
        self.notes.delete(note)
        self.session.commit()

    def search_notes(self, payload: NoteSearchRequest, current_user: User) -> NoteSearchResponse:
        results = self.search_engine.search(
            payload.query,
            self._searchable_notes(current_user.id),
            mode=payload.mode,
            tags=payload.tags,
            project_id=payload.project_id,
            collection_id=payload.collection_id,
            author=payload.author,
            concepts=payload.concepts,
            date_from=payload.date_from,
            date_to=payload.date_to,
            limit=payload.limit,
        )
        self._record_search(payload, current_user)
        self.session.commit()
        return NoteSearchResponse(query=payload.query, mode=payload.mode.value, results=results)

    def improve_note(self, note_id: str, payload: NoteImproveRequest, current_user: User) -> NoteImproveResponse:
        note = self.get_note(note_id, current_user)
        improved = self.note_engine.improve(note.content, mode=payload.mode)
        analysis = self.note_engine.analyze(improved, title=note.title, category=note.category, tags=note.tags)
        return NoteImproveResponse(
            note_id=note.id,
            improved_content=improved,
            analysis={
                "title": analysis.title,
                "summary": analysis.summary,
                "keywords": analysis.keywords,
                "tags": analysis.tags,
                "concepts": analysis.concepts,
                "action_items": analysis.action_items,
            },
        )

    def assist_writing(self, payload: WritingAssistantRequest) -> WritingAssistantResponse:
        result = self.writing_assistant.assist(
            payload.text,
            mode=payload.mode,
            citation_sources=payload.citation_sources,
        )
        return WritingAssistantResponse(
            mode=result.mode.value,
            original_text=result.original_text,
            output_text=result.output_text,
            changes=result.changes,
            citations=result.citations,
            metadata=result.metadata,
        )

    def create_collection(self, payload: CollectionCreate, current_user: User) -> Collection:
        self._validate_project(payload.project_id, current_user)
        collection = Collection(owner_user_id=current_user.id, **payload.model_dump())
        self.collections.add(collection)
        self.session.commit()
        return collection

    def list_collections(self, current_user: User, *, offset: int, limit: int) -> list[Collection]:
        return list(self.collections.list_collections(owner_user_id=current_user.id, offset=offset, limit=limit))

    def get_collection(self, collection_id: str, current_user: User) -> Collection:
        collection = self.collections.get_owned(collection_id, current_user.id)
        if collection is None:
            raise NotFoundError("Collection was not found.")
        return collection

    def update_collection(self, collection_id: str, payload: CollectionUpdate, current_user: User) -> Collection:
        collection = self.get_collection(collection_id, current_user)
        self._update_model(collection, payload.model_dump(exclude_unset=True))
        self.session.commit()
        return self.get_collection(collection_id, current_user)

    def delete_collection(self, collection_id: str, current_user: User) -> None:
        collection = self.get_collection(collection_id, current_user)
        self.collections.delete(collection)
        self.session.commit()

    def create_bookmark(self, payload: BookmarkCreate, current_user: User) -> Bookmark:
        self._validate_project(payload.project_id, current_user)
        self._validate_collection(payload.collection_id, current_user)
        bookmark = Bookmark(owner_user_id=current_user.id, **payload.model_dump())
        self.bookmarks.add(bookmark)
        self._update_memory_for_bookmark(bookmark, current_user)
        self.session.commit()
        return bookmark

    def list_bookmarks(
        self,
        current_user: User,
        *,
        offset: int,
        limit: int,
        target_type: str | None = None,
        project_id: str | None = None,
    ) -> list[Bookmark]:
        return list(
            self.bookmarks.list_bookmarks(
                owner_user_id=current_user.id,
                offset=offset,
                limit=limit,
                target_type=target_type,
                project_id=project_id,
            )
        )

    def update_bookmark(self, bookmark_id: str, payload: BookmarkUpdate, current_user: User) -> Bookmark:
        bookmark = self._bookmark(bookmark_id, current_user)
        self._update_model(bookmark, payload.model_dump(exclude_unset=True))
        self.session.commit()
        return self._bookmark(bookmark_id, current_user)

    def delete_bookmark(self, bookmark_id: str, current_user: User) -> None:
        bookmark = self._bookmark(bookmark_id, current_user)
        self.bookmarks.delete(bookmark)
        self.session.commit()

    def create_project(self, payload: ProjectCreate, current_user: User) -> Project:
        project = Project(owner_user_id=current_user.id, **payload.model_dump())
        self.projects.add(project)
        self._sync_project_graph(project)
        self.session.commit()
        return project

    def list_projects(
        self,
        current_user: User,
        *,
        offset: int,
        limit: int,
        status: str | None = None,
    ) -> list[Project]:
        return list(
            self.projects.list_projects(
                owner_user_id=current_user.id,
                offset=offset,
                limit=limit,
                status=status,
            )
        )

    def get_project(self, project_id: str, current_user: User) -> Project:
        project = self.projects.get_owned(project_id, current_user.id)
        if project is None:
            raise NotFoundError("Project was not found.")
        return project

    def update_project(self, project_id: str, payload: ProjectUpdate, current_user: User) -> Project:
        project = self.get_project(project_id, current_user)
        self._update_model(project, payload.model_dump(exclude_unset=True))
        self._sync_project_graph(project)
        self.session.commit()
        return self.get_project(project_id, current_user)

    def delete_project(self, project_id: str, current_user: User) -> None:
        project = self.get_project(project_id, current_user)
        self.projects.delete(project)
        self.session.commit()

    def create_task(self, payload: WorkspaceTaskCreate, current_user: User) -> WorkspaceTask:
        self._validate_project(payload.project_id, current_user)
        self._validate_session(payload.session_id, current_user)
        task = WorkspaceTask(owner_user_id=current_user.id, **payload.model_dump())
        self.tasks.add(task)
        self._update_project_progress(task.project_id)
        self.session.commit()
        return task

    def list_tasks(
        self,
        current_user: User,
        *,
        offset: int,
        limit: int,
        project_id: str | None = None,
        status: str | None = None,
    ) -> list[WorkspaceTask]:
        return list(
            self.tasks.list_tasks(
                owner_user_id=current_user.id,
                offset=offset,
                limit=limit,
                project_id=project_id,
                status=status,
            )
        )

    def update_task(self, task_id: str, payload: WorkspaceTaskUpdate, current_user: User) -> WorkspaceTask:
        task = self._task(task_id, current_user)
        old_project_id = task.project_id
        data = payload.model_dump(exclude_unset=True)
        if payload.project_id is not None:
            self._validate_project(payload.project_id, current_user)
        if payload.session_id is not None:
            self._validate_session(payload.session_id, current_user)
        self._update_model(task, data)
        if data.get("status") == "completed" and task.completed_at is None:
            task.completed_at = utc_now()
        if data.get("status") and data.get("status") != "completed":
            task.completed_at = None
        self._update_project_progress(task.project_id)
        if old_project_id and old_project_id != task.project_id:
            self._update_project_progress(old_project_id)
        self.session.commit()
        return self._task(task_id, current_user)

    def delete_task(self, task_id: str, current_user: User) -> None:
        task = self._task(task_id, current_user)
        project_id = task.project_id
        self.tasks.delete(task)
        self._update_project_progress(project_id)
        self.session.commit()

    def generate_task_plan(self, payload: TaskAssistantRequest, current_user: User) -> TaskAssistantResponse:
        self._validate_project(payload.project_id, current_user)
        plan = self.task_assistant.generate_plan(
            payload.prompt,
            plan_type=payload.plan_type,
            concepts=payload.concepts,
            resources=payload.resources,
        )
        created_task_ids: list[str] = []
        if payload.create_tasks:
            for item in plan.checklist:
                task = WorkspaceTask(
                    owner_user_id=current_user.id,
                    project_id=payload.project_id,
                    title=str(item["title"]),
                    description=str(item["description"]),
                    task_type=payload.plan_type.value,
                    status=str(item["status"]),
                    priority=str(item["priority"]),
                    checklist=[],
                    tags=[tag for tag in plan.metadata.get("concepts", []) if isinstance(tag, str)][:8],
                    related_note_ids=[],
                    related_document_ids=[],
                    metadata_json={
                        "generated_from": "task_assistant",
                        "plan_title": plan.title,
                        "order": item["order"],
                    },
                )
                self.tasks.add(task)
                created_task_ids.append(task.id)
            self._update_project_progress(payload.project_id)
        self.session.commit()
        return TaskAssistantResponse(
            plan_type=plan.plan_type.value,
            title=plan.title,
            overview=plan.overview,
            checklist=plan.checklist,
            estimated_days=plan.estimated_days,
            milestones=plan.milestones,
            resources=plan.resources,
            created_task_ids=created_task_ids,
            metadata=plan.metadata,
        )

    def create_session(self, payload: ResearchSessionCreate, current_user: User) -> ResearchSession:
        self._validate_project(payload.project_id, current_user)
        research_session = ResearchSession(
            owner_user_id=current_user.id,
            project_id=payload.project_id,
            title=payload.title,
            objective=payload.objective,
            status="active",
            started_at=utc_now(),
            active_concepts=payload.active_concepts,
            recent_document_ids=payload.recent_document_ids,
            recent_note_ids=payload.recent_note_ids,
            search_history=[],
            ai_conversation_refs=[],
            summary="",
            memory_snapshot=self._memory_snapshot(current_user),
            metadata_json=payload.metadata_json,
        )
        self.sessions.add(research_session)
        self.session.commit()
        return research_session

    def list_sessions(
        self,
        current_user: User,
        *,
        offset: int,
        limit: int,
        status: str | None = None,
    ) -> list[ResearchSession]:
        return list(
            self.sessions.list_sessions(
                owner_user_id=current_user.id,
                offset=offset,
                limit=limit,
                status=status,
            )
        )

    def update_session(
        self,
        session_id: str,
        payload: ResearchSessionUpdate,
        current_user: User,
    ) -> ResearchSession:
        research_session = self._research_session(session_id, current_user)
        data = payload.model_dump(exclude_unset=True)
        self._update_model(research_session, data)
        if data.get("status") in {"completed", "archived"} and research_session.ended_at is None:
            research_session.ended_at = utc_now()
        if data.get("status") == "active":
            research_session.ended_at = None
        self.session.commit()
        return self._research_session(session_id, current_user)

    def create_canvas_object(self, payload: CanvasObjectCreate, current_user: User) -> CanvasObject:
        self._validate_project(payload.project_id, current_user)
        self._validate_session(payload.session_id, current_user)
        canvas_object = CanvasObject(owner_user_id=current_user.id, **payload.model_dump())
        self.canvas.add(canvas_object)
        self.session.commit()
        return canvas_object

    def list_canvas_objects(
        self,
        current_user: User,
        *,
        canvas_id: str,
        project_id: str | None,
        offset: int,
        limit: int,
    ) -> list[CanvasObject]:
        return list(
            self.canvas.list_objects(
                owner_user_id=current_user.id,
                canvas_id=canvas_id,
                project_id=project_id,
                offset=offset,
                limit=limit,
            )
        )

    def update_canvas_object(
        self,
        object_id: str,
        payload: CanvasObjectUpdate,
        current_user: User,
    ) -> CanvasObject:
        canvas_object = self._canvas_object(object_id, current_user)
        self._update_model(canvas_object, payload.model_dump(exclude_unset=True))
        self.session.commit()
        return self._canvas_object(object_id, current_user)

    def connect_canvas_objects(
        self,
        object_id: str,
        payload: CanvasConnectionRequest,
        current_user: User,
    ) -> CanvasObject:
        source = self._canvas_object(object_id, current_user)
        target = self._canvas_object(payload.target_object_id, current_user)
        connection = {
            "target_object_id": target.id,
            "relationship_type": payload.relationship_type,
            "label": payload.label,
            "metadata": payload.metadata,
            "created_at": utc_now().isoformat(),
        }
        reverse = {
            "target_object_id": source.id,
            "relationship_type": payload.relationship_type,
            "label": payload.label,
            "metadata": payload.metadata,
            "created_at": utc_now().isoformat(),
        }
        source.connections = self._append_unique_connection(source.connections, connection)
        target.connections = self._append_unique_connection(target.connections, reverse)
        self.session.commit()
        return source

    def delete_canvas_object(self, object_id: str, current_user: User) -> None:
        canvas_object = self._canvas_object(object_id, current_user)
        self.canvas.delete(canvas_object)
        self.session.commit()

    def timeline(self, current_user: User, *, limit: int = 50) -> TimelineResponse:
        items: list[TimelineItem] = []
        for note in self.notes.list_notes(owner_user_id=current_user.id, limit=limit):
            items.append(
                TimelineItem(
                    item_type="note",
                    item_id=note.id,
                    title=note.title,
                    timestamp=note.updated_at,
                    summary=note.summary,
                    metadata={"tags": note.tags, "concepts": note.concepts},
                )
            )
        for session in self.sessions.list_sessions(owner_user_id=current_user.id, limit=limit):
            items.append(
                TimelineItem(
                    item_type="research_session",
                    item_id=session.id,
                    title=session.title,
                    timestamp=session.started_at,
                    summary=session.summary or session.objective,
                    metadata={"status": session.status, "active_concepts": session.active_concepts},
                )
            )
        for project in self.projects.list_projects(owner_user_id=current_user.id, limit=limit):
            items.append(
                TimelineItem(
                    item_type="project",
                    item_id=project.id,
                    title=project.title,
                    timestamp=project.updated_at,
                    summary=project.description,
                    metadata={"status": project.status, "progress_percent": project.progress_percent},
                )
            )
        return TimelineResponse(items=sorted(items, key=lambda item: item.timestamp, reverse=True)[:limit])

    def _apply_analysis(self, note: Note, analysis: NoteAnalysis, content: str) -> None:
        related_notes = self.note_engine.related_notes(
            analysis,
            self._searchable_notes(note.owner_user_id or ""),
            limit=8,
        )
        related_documents = self._related_documents(analysis)
        related_graph_nodes = self._related_graph_nodes(analysis)
        duplicate_notes = self.note_engine.detect_duplicate_notes(
            analysis,
            [item for item in self._searchable_notes(note.owner_user_id or "") if item.id != note.id],
            limit=5,
        )
        note.title = analysis.title
        note.slug = self._slug(analysis.title)
        note.content = content
        note.summary = analysis.summary
        note.category = analysis.category
        note.tags = analysis.tags
        note.keywords = analysis.keywords
        note.concepts = analysis.concepts
        note.action_items = analysis.action_items
        note.related_note_ids = dedupe([str(item["note_id"]) for item in related_notes if item["note_id"] != note.id])
        note.related_document_ids = dedupe([str(item["document_id"]) for item in related_documents])
        note.related_graph_node_ids = dedupe([str(item["node_id"]) for item in related_graph_nodes])
        note.duplicate_note_ids = dedupe(
            [str(item["note_id"]) for item in duplicate_notes if item["note_id"] != note.id]
        )
        note.content_hash = analysis.content_hash
        note.duplicate_key = analysis.duplicate_key
        note.embedding = self.embedding_service.embed_text(f"{analysis.title}\n{content}")
        note.metadata_json = {
            **note.metadata_json,
            "analysis": analysis.metadata,
            "related_notes": related_notes,
            "related_documents": related_documents,
            "related_graph_nodes": related_graph_nodes,
            "duplicate_candidates": duplicate_notes,
        }

    def _searchable_notes(self, owner_user_id: str) -> list[SearchableNote]:
        return [
            SearchableNote(
                id=note.id,
                title=note.title,
                content=note.content,
                summary=note.summary,
                tags=note.tags,
                keywords=note.keywords,
                concepts=note.concepts,
                category=note.category,
                author=note.author,
                project_id=note.project_id,
                collection_id=note.collection_id,
                created_at=note.created_at,
                updated_at=note.updated_at,
                embedding=note.embedding,
                metadata=note.metadata_json,
            )
            for note in self.notes.list_for_search(owner_user_id)
        ]

    def _related_documents(self, analysis: NoteAnalysis, *, limit: int = 8) -> list[dict[str, object]]:
        scored: list[dict[str, object]] = []
        analysis_text = " ".join([analysis.title, *analysis.keywords, *analysis.concepts, *analysis.tags])
        for document in self.documents.list_documents(offset=0, limit=10_000):
            full_document = self.documents.get_full(document.id)
            if full_document is None:
                continue
            document_text = " ".join(
                [
                    full_document.title,
                    full_document.category,
                    " ".join(full_document.topics),
                    " ".join(keyword.value for keyword in full_document.keywords),
                    " ".join(concept.name for concept in full_document.concepts),
                    " ".join(technology.name for technology in full_document.technologies),
                ]
            )
            score = token_overlap(analysis_text, document_text)
            if score <= 0.05:
                continue
            scored.append(
                {
                    "document_id": full_document.id,
                    "title": full_document.title,
                    "score": round(score, 4),
                    "reason": "Overlapping concepts, topics, keywords, or technologies.",
                }
            )
        return sorted(scored, key=lambda item: (-float(item["score"]), str(item["title"])))[:limit]

    def _related_graph_nodes(self, analysis: NoteAnalysis, *, limit: int = 12) -> list[dict[str, object]]:
        related: dict[str, dict[str, object]] = {}
        for concept in [*analysis.concepts, *analysis.keywords[:4]]:
            for node in self.graph_nodes.search(concept, limit=3):
                related[node.id] = {
                    "node_id": node.id,
                    "stable_key": node.stable_key,
                    "name": node.name,
                    "node_type": node.node_type,
                    "score": round(token_overlap(concept, f"{node.name} {node.description}"), 4),
                }
        return sorted(related.values(), key=lambda item: (-float(item["score"]), str(item["name"])))[:limit]

    def _link_related_notes(self, note: Note) -> None:
        for note_id in note.related_note_ids:
            related = self.notes.get_owned(note_id, note.owner_user_id or "")
            if related is None:
                continue
            related.related_note_ids = dedupe([*related.related_note_ids, note.id])

    def _sync_note_graph(self, note: Note) -> None:
        note_node = self._upsert_graph_node(
            stable_key=f"note:{note.id}",
            node_type="note",
            name=note.title,
            label=note.title,
            description=note.summary or note.content[:500],
            importance=0.66 + min(0.2, len(note.related_note_ids) * 0.03),
            confidence=0.84,
            color="#14b8a6",
            metadata={
                "source": "workspace_note",
                "note_id": note.id,
                "tags": note.tags,
                "keywords": note.keywords,
                "concepts": note.concepts,
                "source_document_ids": note.related_document_ids,
            },
        )
        if note.project_id:
            project = self.projects.get(note.project_id)
            if project is not None:
                project_node = self._sync_project_graph(project, refresh=False)
                self._upsert_graph_edge(
                    source=project_node,
                    target=note_node,
                    relationship_type="supports",
                    label="Supports",
                    description=f"{project.title} contains workspace note {note.title}.",
                    weight=0.62,
                    confidence=0.82,
                    metadata={"project_id": project.id, "note_id": note.id},
                )
        for concept in note.concepts[:10]:
            concept_node = self._upsert_graph_node(
                stable_key=stable_node_key("concept", concept),
                node_type="concept",
                name=concept,
                label=concept,
                description=f"{concept} is referenced by workspace note {note.title}.",
                importance=0.58,
                confidence=0.78,
                color="#059669",
                metadata={"source": "workspace_note_concept", "note_ids": [note.id]},
            )
            self._upsert_graph_edge(
                source=note_node,
                target=concept_node,
                relationship_type="explains",
                label="Explains",
                description=f"{note.title} explains or references {concept}.",
                weight=0.7,
                confidence=0.8,
                metadata={"note_id": note.id, "concept": concept},
            )
        for document_id in note.related_document_ids[:12]:
            document_node = self.graph_nodes.get_by_stable_key(f"document:{document_id}")
            if document_node is None:
                continue
            self._upsert_graph_edge(
                source=note_node,
                target=document_node,
                relationship_type="referenced_by",
                label="References",
                description=f"{note.title} is connected to source document {document_node.name}.",
                weight=0.68,
                confidence=0.76,
                metadata={"note_id": note.id, "document_id": document_id},
            )
        for related_note_id in note.related_note_ids[:12]:
            related_node = self.graph_nodes.get_by_stable_key(f"note:{related_note_id}")
            if related_node is None:
                continue
            self._upsert_graph_edge(
                source=note_node,
                target=related_node,
                relationship_type="related_to",
                label="Related",
                description=f"{note.title} is related to workspace note {related_node.name}.",
                weight=0.58,
                confidence=0.72,
                metadata={"note_id": note.id, "related_note_id": related_note_id},
            )
        InteractiveKnowledgeGraphService(self.session).refresh_layout()

    def _sync_project_graph(self, project: Project, *, refresh: bool = True) -> GraphNode:
        project_node = self._upsert_graph_node(
            stable_key=f"project:{project.id}",
            node_type="project",
            name=project.title,
            label=project.title,
            description=project.description or f"Workspace project for {project.title}.",
            importance=0.72,
            confidence=0.9,
            color="#16a34a",
            metadata={
                "source": "workspace_project",
                "project_id": project.id,
                "goals": project.goals,
                "research_domain": project.research_domain,
                "progress_percent": project.progress_percent,
            },
        )
        if refresh:
            InteractiveKnowledgeGraphService(self.session).refresh_layout()
        return project_node

    def _delete_note_graph(self, note: Note) -> None:
        node = self.graph_nodes.get_by_stable_key(f"note:{note.id}")
        if node is None:
            return
        for edge in self.graph_edges.neighbors(node.id, limit=100_000):
            self.session.delete(edge)
        self.session.delete(node)
        self.session.flush()
        InteractiveKnowledgeGraphService(self.session).refresh_layout()

    def _upsert_graph_node(
        self,
        *,
        stable_key: str,
        node_type: str,
        name: str,
        label: str,
        description: str,
        importance: float,
        confidence: float,
        color: str,
        metadata: dict[str, object],
    ) -> GraphNode:
        node = self.graph_nodes.get_by_stable_key(stable_key)
        if node is None:
            node = GraphNode(
                stable_key=stable_key,
                node_type=node_type,
                name=name,
                label=label,
                description=description,
                document_id=None,
                importance_score=importance,
                confidence_score=confidence,
                degree=0,
                cluster_id=None,
                is_collapsed=False,
                position_x=0.0,
                position_y=0.0,
                size=node_size(importance, node_type),
                color=color,
                metadata_json=metadata,
            )
            self.graph_nodes.add(node)
            return node
        node.name = name
        node.label = label
        node.description = description
        node.importance_score = max(node.importance_score, importance)
        node.confidence_score = max(node.confidence_score, confidence)
        node.size = node_size(node.importance_score, node.node_type)
        node.color = color
        node.metadata_json = {**node.metadata_json, **metadata}
        self.session.flush()
        return node

    def _upsert_graph_edge(
        self,
        *,
        source: GraphNode,
        target: GraphNode,
        relationship_type: str,
        label: str,
        description: str,
        weight: float,
        confidence: float,
        metadata: dict[str, object],
    ) -> GraphEdge:
        if source.id == target.id:
            raise ValidationError("Graph edge source and target must be different.")
        stable_key = stable_edge_key(source.stable_key, target.stable_key, relationship_type)
        edge = self.graph_edges.get_by_stable_key(stable_key)
        if edge is None:
            edge = GraphEdge(
                stable_key=stable_key,
                source_node_id=source.id,
                target_node_id=target.id,
                relationship_type=relationship_type,
                label=label,
                description=description,
                weight=weight,
                confidence_score=confidence,
                is_bidirectional=False,
                metadata_json=metadata,
            )
            self.graph_edges.add(edge)
            return edge
        edge.weight = max(edge.weight, weight)
        edge.confidence_score = max(edge.confidence_score, confidence)
        edge.label = label
        edge.description = description
        edge.metadata_json = {**edge.metadata_json, **metadata}
        self.session.flush()
        return edge

    def _update_memory_for_note(self, note: Note, current_user: User) -> None:
        settings = self._get_or_create_settings(current_user, commit_on_create=False)
        recent_item = {
            "type": "note",
            "id": note.id,
            "title": note.title,
            "timestamp": utc_now().isoformat(),
            "concepts": note.concepts[:8],
        }
        settings.recent_research = self._prepend_limited(settings.recent_research, recent_item, key="id", limit=50)
        settings.frequently_used_concepts = dedupe([*note.concepts, *settings.frequently_used_concepts])[:100]
        settings.favorite_topics = dedupe([*settings.favorite_topics, *note.tags[:4]])[:100]
        settings.memory_profile = {
            **settings.memory_profile,
            "last_note_id": note.id,
            "last_note_title": note.title,
            "known_concept_count": len(settings.frequently_used_concepts),
        }

    def _update_memory_for_bookmark(self, bookmark: Bookmark, current_user: User) -> None:
        settings = self._get_or_create_settings(current_user, commit_on_create=False)
        item = {
            "id": bookmark.id,
            "target_type": bookmark.target_type,
            "title": bookmark.title,
            "timestamp": utc_now().isoformat(),
        }
        settings.bookmarks_snapshot = self._prepend_limited(settings.bookmarks_snapshot, item, key="id", limit=80)

    def _record_search(self, payload: NoteSearchRequest, current_user: User) -> None:
        settings = self._get_or_create_settings(current_user, commit_on_create=False)
        entry = {
            "query": payload.query,
            "mode": payload.mode.value,
            "timestamp": utc_now().isoformat(),
            "filters": {
                "tags": payload.tags,
                "project_id": payload.project_id,
                "collection_id": payload.collection_id,
                "author": payload.author,
                "concepts": payload.concepts,
                "date_from": payload.date_from.isoformat() if payload.date_from else None,
                "date_to": payload.date_to.isoformat() if payload.date_to else None,
            },
        }
        settings.search_history = self._prepend_limited(settings.search_history, entry, key="timestamp", limit=100)

    def _memory_snapshot(self, current_user: User) -> dict[str, object]:
        settings = self._get_or_create_settings(current_user, commit_on_create=False)
        return {
            "favorite_topics": settings.favorite_topics[:20],
            "frequently_used_concepts": settings.frequently_used_concepts[:30],
            "recent_research": settings.recent_research[:10],
            "reading_history": settings.reading_history[:10],
            "search_history": settings.search_history[:10],
        }

    def _update_project_progress(self, project_id: str | None) -> None:
        if not project_id:
            return
        project = self.projects.get(project_id)
        if project is None:
            return
        tasks = list(
            self.tasks.list_tasks(
                owner_user_id=project.owner_user_id or "",
                project_id=project.id,
                limit=10_000,
            )
        )
        if not tasks:
            project.progress_percent = 0.0
            return
        completed = sum(1 for task in tasks if task.status == "completed")
        project.progress_percent = round(completed / len(tasks) * 100, 2)

    def _validate_project(self, project_id: str | None, current_user: User) -> None:
        if project_id and self.projects.get_owned(project_id, current_user.id) is None:
            raise NotFoundError("Project was not found.")

    def _validate_collection(self, collection_id: str | None, current_user: User) -> None:
        if collection_id and self.collections.get_owned(collection_id, current_user.id) is None:
            raise NotFoundError("Collection was not found.")

    def _validate_session(self, session_id: str | None, current_user: User) -> None:
        if session_id and self.sessions.get_owned(session_id, current_user.id) is None:
            raise NotFoundError("Research session was not found.")

    def _bookmark(self, bookmark_id: str, current_user: User) -> Bookmark:
        bookmark = self.bookmarks.get_owned(bookmark_id, current_user.id)
        if bookmark is None:
            raise NotFoundError("Bookmark was not found.")
        return bookmark

    def _task(self, task_id: str, current_user: User) -> WorkspaceTask:
        task = self.tasks.get_owned(task_id, current_user.id)
        if task is None:
            raise NotFoundError("Task was not found.")
        return task

    def _research_session(self, session_id: str, current_user: User) -> ResearchSession:
        research_session = self.sessions.get_owned(session_id, current_user.id)
        if research_session is None:
            raise NotFoundError("Research session was not found.")
        return research_session

    def _canvas_object(self, object_id: str, current_user: User) -> CanvasObject:
        canvas_object = self.canvas.get_owned(object_id, current_user.id)
        if canvas_object is None:
            raise NotFoundError("Canvas object was not found.")
        return canvas_object

    def _update_model(self, model: object, data: dict[str, object]) -> None:
        for field_name, value in data.items():
            if value is not None:
                setattr(model, field_name, value.value if hasattr(value, "value") else value)

    def _append_unique_connection(
        self,
        connections: list[dict[str, object]],
        connection: dict[str, object],
    ) -> list[dict[str, object]]:
        key = (connection.get("target_object_id"), connection.get("relationship_type"))
        filtered = [
            item
            for item in connections
            if (item.get("target_object_id"), item.get("relationship_type")) != key
        ]
        return [*filtered, connection]

    def _prepend_limited(
        self,
        items: list[dict[str, object]],
        item: dict[str, object],
        *,
        key: str,
        limit: int,
    ) -> list[dict[str, object]]:
        item_key = item.get(key)
        filtered = [existing for existing in items if existing.get(key) != item_key]
        return [item, *filtered][:limit]

    def _slug(self, title: str) -> str:
        return f"{normalize_key(title)[:160]}-{datetime.now(UTC).strftime('%Y%m%d%H%M%S%f')}"
