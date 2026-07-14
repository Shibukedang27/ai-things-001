from fastapi import APIRouter

from backend.routers import (
    agents,
    auth,
    documents,
    graph,
    health,
    knowledge_dna,
    learning,
    retrieval,
    roles,
    users,
    workspace,
)

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(agents.router, prefix="/agents", tags=["Multi-Agent Research"])
api_router.include_router(retrieval.router, prefix="/retrieval", tags=["Hybrid Retrieval and Reasoning"])
api_router.include_router(graph.router, prefix="/graph", tags=["Interactive Knowledge Graph"])
api_router.include_router(workspace.router, prefix="/workspace", tags=["AI Workspace and Second Brain"])
api_router.include_router(learning.router, prefix="/learning", tags=["Adaptive Learning"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(roles.router, prefix="/roles", tags=["Roles and Permissions"])
api_router.include_router(documents.router, prefix="/documents", tags=["Knowledge Documents"])
api_router.include_router(knowledge_dna.router, prefix="/knowledge-dna", tags=["Knowledge DNA"])
