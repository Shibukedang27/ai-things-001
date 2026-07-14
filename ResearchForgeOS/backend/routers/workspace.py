from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.dependencies.auth import require_permissions
from backend.dependencies.database import get_db
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
from backend.schemas.common import MessageResponse
from backend.schemas.workspace import (
    BookmarkCreate,
    BookmarkRead,
    BookmarkUpdate,
    CanvasConnectionRequest,
    CanvasObjectCreate,
    CanvasObjectRead,
    CanvasObjectUpdate,
    CollectionCreate,
    CollectionRead,
    CollectionUpdate,
    NoteCreate,
    NoteImproveRequest,
    NoteImproveResponse,
    NoteRead,
    NoteSearchRequest,
    NoteSearchResponse,
    NoteUpdate,
    ProjectCreate,
    ProjectRead,
    ProjectUpdate,
    ResearchSessionCreate,
    ResearchSessionRead,
    ResearchSessionUpdate,
    TaskAssistantRequest,
    TaskAssistantResponse,
    TimelineResponse,
    WorkspaceOverview,
    WorkspaceSettingsRead,
    WorkspaceSettingsUpdate,
    WorkspaceTaskCreate,
    WorkspaceTaskRead,
    WorkspaceTaskUpdate,
    WritingAssistantRequest,
    WritingAssistantResponse,
)
from backend.services.workspace_service import WorkspaceService

router = APIRouter()


@router.get("", response_model=WorkspaceOverview, summary="Get Workspace Overview")
async def get_workspace_overview(
    session: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("workspace:read"))],
) -> WorkspaceOverview:
    return WorkspaceService(session).overview(current_user)


@router.get("/settings", response_model=WorkspaceSettingsRead, summary="Get Workspace Settings")
async def get_workspace_settings(
    session: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("workspace:read"))],
) -> WorkspaceSettings:
    return WorkspaceService(session).get_settings(current_user)


@router.patch("/settings", response_model=WorkspaceSettingsRead, summary="Update Workspace Settings")
async def update_workspace_settings(
    payload: WorkspaceSettingsUpdate,
    session: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("workspace:write"))],
) -> WorkspaceSettings:
    return WorkspaceService(session).update_settings(payload, current_user)


@router.post("/notes", response_model=NoteRead, status_code=status.HTTP_201_CREATED, summary="Create Note")
async def create_note(
    payload: NoteCreate,
    session: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("workspace:write"))],
) -> Note:
    return WorkspaceService(session).create_note(payload, current_user)


@router.get("/notes", response_model=list[NoteRead], summary="List Notes")
async def list_notes(
    session: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("workspace:read"))],
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    project_id: str | None = None,
    collection_id: str | None = None,
    pinned: bool | None = None,
    note_type: str | None = Query(default=None, max_length=80),
) -> list[Note]:
    return WorkspaceService(session).list_notes(
        current_user,
        offset=offset,
        limit=limit,
        project_id=project_id,
        collection_id=collection_id,
        pinned=pinned,
        note_type=note_type,
    )


@router.post("/notes/search", response_model=NoteSearchResponse, summary="Search Notes")
async def search_notes(
    payload: NoteSearchRequest,
    session: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("workspace:read"))],
) -> NoteSearchResponse:
    return WorkspaceService(session).search_notes(payload, current_user)


@router.get("/notes/{note_id}", response_model=NoteRead, summary="Get Note")
async def get_note(
    note_id: str,
    session: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("workspace:read"))],
) -> Note:
    return WorkspaceService(session).get_note(note_id, current_user)


@router.patch("/notes/{note_id}", response_model=NoteRead, summary="Update Note")
async def update_note(
    note_id: str,
    payload: NoteUpdate,
    session: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("workspace:write"))],
) -> Note:
    return WorkspaceService(session).update_note(note_id, payload, current_user)


@router.delete("/notes/{note_id}", response_model=MessageResponse, summary="Delete Note")
async def delete_note(
    note_id: str,
    session: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("workspace:write"))],
) -> MessageResponse:
    WorkspaceService(session).delete_note(note_id, current_user)
    return MessageResponse(message="Workspace note deleted.")


@router.post("/notes/{note_id}/improve", response_model=NoteImproveResponse, summary="Improve Note")
async def improve_note(
    note_id: str,
    payload: NoteImproveRequest,
    session: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("workspace:write"))],
) -> NoteImproveResponse:
    return WorkspaceService(session).improve_note(note_id, payload, current_user)


@router.post("/writing/assist", response_model=WritingAssistantResponse, summary="AI Writing Assistant")
async def writing_assistant(
    payload: WritingAssistantRequest,
    session: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("workspace:write"))],
) -> WritingAssistantResponse:
    return WorkspaceService(session).assist_writing(payload)


@router.post(
    "/collections",
    response_model=CollectionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create Collection",
)
async def create_collection(
    payload: CollectionCreate,
    session: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("workspace:write"))],
) -> Collection:
    return WorkspaceService(session).create_collection(payload, current_user)


@router.get("/collections", response_model=list[CollectionRead], summary="List Collections")
async def list_collections(
    session: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("workspace:read"))],
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> list[Collection]:
    return WorkspaceService(session).list_collections(current_user, offset=offset, limit=limit)


@router.patch("/collections/{collection_id}", response_model=CollectionRead, summary="Update Collection")
async def update_collection(
    collection_id: str,
    payload: CollectionUpdate,
    session: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("workspace:write"))],
) -> Collection:
    return WorkspaceService(session).update_collection(collection_id, payload, current_user)


@router.delete("/collections/{collection_id}", response_model=MessageResponse, summary="Delete Collection")
async def delete_collection(
    collection_id: str,
    session: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("workspace:write"))],
) -> MessageResponse:
    WorkspaceService(session).delete_collection(collection_id, current_user)
    return MessageResponse(message="Collection deleted.")


@router.post("/bookmarks", response_model=BookmarkRead, status_code=status.HTTP_201_CREATED, summary="Bookmark")
async def create_bookmark(
    payload: BookmarkCreate,
    session: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("workspace:write"))],
) -> Bookmark:
    return WorkspaceService(session).create_bookmark(payload, current_user)


@router.get("/bookmarks", response_model=list[BookmarkRead], summary="List Bookmarks")
async def list_bookmarks(
    session: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("workspace:read"))],
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    target_type: str | None = Query(default=None, max_length=80),
    project_id: str | None = None,
) -> list[Bookmark]:
    return WorkspaceService(session).list_bookmarks(
        current_user,
        offset=offset,
        limit=limit,
        target_type=target_type,
        project_id=project_id,
    )


@router.patch("/bookmarks/{bookmark_id}", response_model=BookmarkRead, summary="Update Bookmark")
async def update_bookmark(
    bookmark_id: str,
    payload: BookmarkUpdate,
    session: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("workspace:write"))],
) -> Bookmark:
    return WorkspaceService(session).update_bookmark(bookmark_id, payload, current_user)


@router.delete("/bookmarks/{bookmark_id}", response_model=MessageResponse, summary="Delete Bookmark")
async def delete_bookmark(
    bookmark_id: str,
    session: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("workspace:write"))],
) -> MessageResponse:
    WorkspaceService(session).delete_bookmark(bookmark_id, current_user)
    return MessageResponse(message="Bookmark deleted.")


@router.post("/projects", response_model=ProjectRead, status_code=status.HTTP_201_CREATED, summary="Create Project")
async def create_project(
    payload: ProjectCreate,
    session: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("workspace:write"))],
) -> Project:
    return WorkspaceService(session).create_project(payload, current_user)


@router.get("/projects", response_model=list[ProjectRead], summary="List Projects")
async def list_projects(
    session: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("workspace:read"))],
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    status_filter: str | None = Query(default=None, alias="status", max_length=60),
) -> list[Project]:
    return WorkspaceService(session).list_projects(current_user, offset=offset, limit=limit, status=status_filter)


@router.get("/projects/{project_id}", response_model=ProjectRead, summary="Get Project")
async def get_project(
    project_id: str,
    session: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("workspace:read"))],
) -> Project:
    return WorkspaceService(session).get_project(project_id, current_user)


@router.patch("/projects/{project_id}", response_model=ProjectRead, summary="Update Project")
async def update_project(
    project_id: str,
    payload: ProjectUpdate,
    session: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("workspace:write"))],
) -> Project:
    return WorkspaceService(session).update_project(project_id, payload, current_user)


@router.delete("/projects/{project_id}", response_model=MessageResponse, summary="Delete Project")
async def delete_project(
    project_id: str,
    session: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("workspace:write"))],
) -> MessageResponse:
    WorkspaceService(session).delete_project(project_id, current_user)
    return MessageResponse(message="Project deleted.")


@router.post("/tasks", response_model=WorkspaceTaskRead, status_code=status.HTTP_201_CREATED, summary="Create Task")
async def create_task(
    payload: WorkspaceTaskCreate,
    session: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("workspace:write"))],
) -> WorkspaceTask:
    return WorkspaceService(session).create_task(payload, current_user)


@router.get("/tasks", response_model=list[WorkspaceTaskRead], summary="List Tasks")
async def list_tasks(
    session: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("workspace:read"))],
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    project_id: str | None = None,
    status_filter: str | None = Query(default=None, alias="status", max_length=60),
) -> list[WorkspaceTask]:
    return WorkspaceService(session).list_tasks(
        current_user,
        offset=offset,
        limit=limit,
        project_id=project_id,
        status=status_filter,
    )


@router.patch("/tasks/{task_id}", response_model=WorkspaceTaskRead, summary="Update Task")
async def update_task(
    task_id: str,
    payload: WorkspaceTaskUpdate,
    session: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("workspace:write"))],
) -> WorkspaceTask:
    return WorkspaceService(session).update_task(task_id, payload, current_user)


@router.delete("/tasks/{task_id}", response_model=MessageResponse, summary="Delete Task")
async def delete_task(
    task_id: str,
    session: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("workspace:write"))],
) -> MessageResponse:
    WorkspaceService(session).delete_task(task_id, current_user)
    return MessageResponse(message="Task deleted.")


@router.post("/tasks/assistant", response_model=TaskAssistantResponse, summary="AI Task Assistant")
async def generate_task_plan(
    payload: TaskAssistantRequest,
    session: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("workspace:write"))],
) -> TaskAssistantResponse:
    return WorkspaceService(session).generate_task_plan(payload, current_user)


@router.post(
    "/sessions",
    response_model=ResearchSessionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create Research Session",
)
async def create_research_session(
    payload: ResearchSessionCreate,
    session: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("workspace:write"))],
) -> ResearchSession:
    return WorkspaceService(session).create_session(payload, current_user)


@router.get("/sessions", response_model=list[ResearchSessionRead], summary="List Research Sessions")
async def list_research_sessions(
    session: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("workspace:read"))],
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    status_filter: str | None = Query(default=None, alias="status", max_length=60),
) -> list[ResearchSession]:
    return WorkspaceService(session).list_sessions(current_user, offset=offset, limit=limit, status=status_filter)


@router.patch("/sessions/{research_session_id}", response_model=ResearchSessionRead, summary="Update Research Session")
async def update_research_session(
    research_session_id: str,
    payload: ResearchSessionUpdate,
    session: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("workspace:write"))],
) -> ResearchSession:
    return WorkspaceService(session).update_session(research_session_id, payload, current_user)


@router.post(
    "/canvas/objects",
    response_model=CanvasObjectRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create Canvas Object",
)
async def create_canvas_object(
    payload: CanvasObjectCreate,
    session: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("workspace:write"))],
) -> CanvasObject:
    return WorkspaceService(session).create_canvas_object(payload, current_user)


@router.get("/canvas/objects", response_model=list[CanvasObjectRead], summary="List Canvas Objects")
async def list_canvas_objects(
    session: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("workspace:read"))],
    canvas_id: str = Query(default="default", min_length=1, max_length=80),
    project_id: str | None = None,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=200, ge=1, le=500),
) -> list[CanvasObject]:
    return WorkspaceService(session).list_canvas_objects(
        current_user,
        canvas_id=canvas_id,
        project_id=project_id,
        offset=offset,
        limit=limit,
    )


@router.patch("/canvas/objects/{object_id}", response_model=CanvasObjectRead, summary="Update Canvas Object")
async def update_canvas_object(
    object_id: str,
    payload: CanvasObjectUpdate,
    session: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("workspace:write"))],
) -> CanvasObject:
    return WorkspaceService(session).update_canvas_object(object_id, payload, current_user)


@router.post("/canvas/objects/{object_id}/connect", response_model=CanvasObjectRead, summary="Connect Canvas Objects")
async def connect_canvas_objects(
    object_id: str,
    payload: CanvasConnectionRequest,
    session: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("workspace:write"))],
) -> CanvasObject:
    return WorkspaceService(session).connect_canvas_objects(object_id, payload, current_user)


@router.delete("/canvas/objects/{object_id}", response_model=MessageResponse, summary="Delete Canvas Object")
async def delete_canvas_object(
    object_id: str,
    session: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("workspace:write"))],
) -> MessageResponse:
    WorkspaceService(session).delete_canvas_object(object_id, current_user)
    return MessageResponse(message="Canvas object deleted.")


@router.get("/timeline", response_model=TimelineResponse, summary="Knowledge Timeline")
async def knowledge_timeline(
    session: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("workspace:read"))],
    limit: int = Query(default=50, ge=1, le=200),
) -> TimelineResponse:
    return WorkspaceService(session).timeline(current_user, limit=limit)
