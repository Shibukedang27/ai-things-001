from backend.repositories.agent_repository import AgentRepository, AgentTaskRepository, PipelineHistoryRepository
from backend.repositories.document_repository import DocumentRepository
from backend.repositories.graph_repository import (
    GraphEdgeRepository,
    GraphLayoutRepository,
    GraphNodeRepository,
    GraphSnapshotRepository,
    NodeMetadataRepository,
    RelationshipMetadataRepository,
)
from backend.repositories.knowledge_dna_repository import KnowledgeDNARepository
from backend.repositories.learning_repository import (
    AchievementRepository,
    CertificateRepository,
    CodingChallengeRepository,
    FlashcardRepository,
    LearningSessionRepository,
    MemoryTrackingRepository,
    ProgressRepository,
    QuizAttemptRepository,
    QuizQuestionRepository,
    QuizRepository,
    ReviewRepository,
    RevisionPlanRepository,
)
from backend.repositories.permission_repository import PermissionRepository
from backend.repositories.retrieval_repository import (
    CitationHistoryRepository,
    KnowledgeCacheRepository,
    ReasoningLogRepository,
    RetrievalEmbeddingRepository,
    RetrievalHistoryRepository,
    RetrievalQueryRepository,
)
from backend.repositories.role_repository import RoleRepository
from backend.repositories.user_repository import UserRepository
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

__all__ = [
    "AchievementRepository",
    "AgentRepository",
    "AgentTaskRepository",
    "BookmarkRepository",
    "CanvasObjectRepository",
    "CertificateRepository",
    "CitationHistoryRepository",
    "CodingChallengeRepository",
    "CollectionRepository",
    "DocumentRepository",
    "FlashcardRepository",
    "GraphEdgeRepository",
    "GraphLayoutRepository",
    "GraphNodeRepository",
    "GraphSnapshotRepository",
    "KnowledgeCacheRepository",
    "KnowledgeDNARepository",
    "LearningSessionRepository",
    "MemoryTrackingRepository",
    "NodeMetadataRepository",
    "NoteRepository",
    "PermissionRepository",
    "PipelineHistoryRepository",
    "ProgressRepository",
    "ProjectRepository",
    "QuizAttemptRepository",
    "QuizQuestionRepository",
    "QuizRepository",
    "ReasoningLogRepository",
    "RelationshipMetadataRepository",
    "ResearchSessionRepository",
    "ReviewRepository",
    "RevisionPlanRepository",
    "RetrievalEmbeddingRepository",
    "RetrievalHistoryRepository",
    "RetrievalQueryRepository",
    "RoleRepository",
    "UserRepository",
    "WorkspaceSettingsRepository",
    "WorkspaceTaskRepository",
]
