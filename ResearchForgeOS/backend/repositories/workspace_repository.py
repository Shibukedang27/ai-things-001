from collections.abc import Sequence
from datetime import date

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

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
from backend.repositories.base import BaseRepository


class NoteRepository(BaseRepository[Note]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Note)

    def get_owned(self, note_id: str, owner_user_id: str) -> Note | None:
        statement = select(Note).where(Note.id == note_id).where(Note.owner_user_id == owner_user_id)
        return self.session.scalars(statement).first()

    def list_notes(
        self,
        *,
        owner_user_id: str,
        offset: int = 0,
        limit: int = 50,
        project_id: str | None = None,
        collection_id: str | None = None,
        pinned: bool | None = None,
        note_type: str | None = None,
    ) -> Sequence[Note]:
        statement = select(Note).where(Note.owner_user_id == owner_user_id)
        if project_id:
            statement = statement.where(Note.project_id == project_id)
        if collection_id:
            statement = statement.where(Note.collection_id == collection_id)
        if pinned is not None:
            statement = statement.where(Note.is_pinned.is_(pinned))
        if note_type:
            statement = statement.where(Note.note_type == note_type)
        statement = statement.order_by(Note.updated_at.desc()).offset(offset).limit(limit)
        return self.session.scalars(statement).all()

    def list_for_search(self, owner_user_id: str, *, limit: int = 10_000) -> Sequence[Note]:
        statement = (
            select(Note)
            .where(Note.owner_user_id == owner_user_id)
            .where(Note.status != "deleted")
            .order_by(Note.updated_at.desc())
            .limit(limit)
        )
        return self.session.scalars(statement).all()

    def find_duplicates(
        self,
        *,
        owner_user_id: str,
        duplicate_key: str,
        exclude_note_id: str | None = None,
    ) -> Sequence[Note]:
        statement = (
            select(Note)
            .where(Note.owner_user_id == owner_user_id)
            .where(Note.duplicate_key == duplicate_key)
        )
        if exclude_note_id:
            statement = statement.where(Note.id != exclude_note_id)
        return self.session.scalars(statement).all()

    def search_title_or_content(self, *, owner_user_id: str, query: str, limit: int = 50) -> Sequence[Note]:
        pattern = f"%{query}%"
        statement = (
            select(Note)
            .where(Note.owner_user_id == owner_user_id)
            .where(or_(Note.title.ilike(pattern), Note.content.ilike(pattern), Note.summary.ilike(pattern)))
            .order_by(Note.updated_at.desc())
            .limit(limit)
        )
        return self.session.scalars(statement).all()

    def daily_note(self, *, owner_user_id: str, note_date: date) -> Note | None:
        statement = (
            select(Note)
            .where(Note.owner_user_id == owner_user_id)
            .where(Note.note_type == "daily_note")
            .where(Note.note_date == note_date)
        )
        return self.session.scalars(statement).first()


class CollectionRepository(BaseRepository[Collection]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Collection)

    def get_owned(self, collection_id: str, owner_user_id: str) -> Collection | None:
        statement = (
            select(Collection)
            .where(Collection.id == collection_id)
            .where(Collection.owner_user_id == owner_user_id)
        )
        return self.session.scalars(statement).first()

    def list_collections(self, *, owner_user_id: str, offset: int = 0, limit: int = 50) -> Sequence[Collection]:
        statement = (
            select(Collection)
            .where(Collection.owner_user_id == owner_user_id)
            .order_by(Collection.name.asc())
            .offset(offset)
            .limit(limit)
        )
        return self.session.scalars(statement).all()


class BookmarkRepository(BaseRepository[Bookmark]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Bookmark)

    def get_owned(self, bookmark_id: str, owner_user_id: str) -> Bookmark | None:
        statement = select(Bookmark).where(Bookmark.id == bookmark_id).where(Bookmark.owner_user_id == owner_user_id)
        return self.session.scalars(statement).first()

    def list_bookmarks(
        self,
        *,
        owner_user_id: str,
        offset: int = 0,
        limit: int = 50,
        target_type: str | None = None,
        project_id: str | None = None,
    ) -> Sequence[Bookmark]:
        statement = select(Bookmark).where(Bookmark.owner_user_id == owner_user_id)
        if target_type:
            statement = statement.where(Bookmark.target_type == target_type)
        if project_id:
            statement = statement.where(Bookmark.project_id == project_id)
        statement = statement.order_by(Bookmark.created_at.desc()).offset(offset).limit(limit)
        return self.session.scalars(statement).all()


class ProjectRepository(BaseRepository[Project]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Project)

    def get_owned(self, project_id: str, owner_user_id: str) -> Project | None:
        statement = (
            select(Project)
            .where(Project.id == project_id)
            .where(Project.owner_user_id == owner_user_id)
            .options(selectinload(Project.notes), selectinload(Project.tasks))
        )
        return self.session.scalars(statement).first()

    def list_projects(
        self,
        *,
        owner_user_id: str,
        offset: int = 0,
        limit: int = 50,
        status: str | None = None,
    ) -> Sequence[Project]:
        statement = select(Project).where(Project.owner_user_id == owner_user_id)
        if status:
            statement = statement.where(Project.status == status)
        statement = statement.order_by(Project.updated_at.desc()).offset(offset).limit(limit)
        return self.session.scalars(statement).all()


class WorkspaceTaskRepository(BaseRepository[WorkspaceTask]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, WorkspaceTask)

    def get_owned(self, task_id: str, owner_user_id: str) -> WorkspaceTask | None:
        statement = (
            select(WorkspaceTask)
            .where(WorkspaceTask.id == task_id)
            .where(WorkspaceTask.owner_user_id == owner_user_id)
        )
        return self.session.scalars(statement).first()

    def list_tasks(
        self,
        *,
        owner_user_id: str,
        offset: int = 0,
        limit: int = 50,
        project_id: str | None = None,
        status: str | None = None,
    ) -> Sequence[WorkspaceTask]:
        statement = select(WorkspaceTask).where(WorkspaceTask.owner_user_id == owner_user_id)
        if project_id:
            statement = statement.where(WorkspaceTask.project_id == project_id)
        if status:
            statement = statement.where(WorkspaceTask.status == status)
        statement = statement.order_by(WorkspaceTask.created_at.desc()).offset(offset).limit(limit)
        return self.session.scalars(statement).all()


class ResearchSessionRepository(BaseRepository[ResearchSession]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, ResearchSession)

    def get_owned(self, session_id: str, owner_user_id: str) -> ResearchSession | None:
        statement = (
            select(ResearchSession)
            .where(ResearchSession.id == session_id)
            .where(ResearchSession.owner_user_id == owner_user_id)
            .options(selectinload(ResearchSession.tasks))
        )
        return self.session.scalars(statement).first()

    def list_sessions(
        self,
        *,
        owner_user_id: str,
        offset: int = 0,
        limit: int = 50,
        status: str | None = None,
    ) -> Sequence[ResearchSession]:
        statement = select(ResearchSession).where(ResearchSession.owner_user_id == owner_user_id)
        if status:
            statement = statement.where(ResearchSession.status == status)
        statement = statement.order_by(ResearchSession.started_at.desc()).offset(offset).limit(limit)
        return self.session.scalars(statement).all()


class CanvasObjectRepository(BaseRepository[CanvasObject]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, CanvasObject)

    def get_owned(self, object_id: str, owner_user_id: str) -> CanvasObject | None:
        statement = (
            select(CanvasObject)
            .where(CanvasObject.id == object_id)
            .where(CanvasObject.owner_user_id == owner_user_id)
        )
        return self.session.scalars(statement).first()

    def list_objects(
        self,
        *,
        owner_user_id: str,
        canvas_id: str = "default",
        project_id: str | None = None,
        offset: int = 0,
        limit: int = 200,
    ) -> Sequence[CanvasObject]:
        statement = (
            select(CanvasObject)
            .where(CanvasObject.owner_user_id == owner_user_id)
            .where(CanvasObject.canvas_id == canvas_id)
        )
        if project_id:
            statement = statement.where(CanvasObject.project_id == project_id)
        statement = (
            statement.order_by(CanvasObject.z_index.asc(), CanvasObject.created_at.asc())
            .offset(offset)
            .limit(limit)
        )
        return self.session.scalars(statement).all()


class WorkspaceSettingsRepository(BaseRepository[WorkspaceSettings]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, WorkspaceSettings)

    def get_by_owner(self, owner_user_id: str) -> WorkspaceSettings | None:
        statement = select(WorkspaceSettings).where(WorkspaceSettings.owner_user_id == owner_user_id)
        return self.session.scalars(statement).first()


__all__ = [
    "BookmarkRepository",
    "CanvasObjectRepository",
    "CollectionRepository",
    "NoteRepository",
    "ProjectRepository",
    "ResearchSessionRepository",
    "WorkspaceSettingsRepository",
    "WorkspaceTaskRepository",
]
