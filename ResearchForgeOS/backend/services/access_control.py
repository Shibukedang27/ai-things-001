from dataclasses import dataclass


@dataclass(frozen=True)
class PermissionDefinition:
    name: str
    resource: str
    action: str
    description: str


SYSTEM_PERMISSIONS: tuple[PermissionDefinition, ...] = (
    PermissionDefinition("users:read", "users", "read", "Read user profiles in the workspace."),
    PermissionDefinition("users:write", "users", "write", "Create and update user profiles in the workspace."),
    PermissionDefinition("roles:read", "roles", "read", "Read role and permission configuration."),
    PermissionDefinition("roles:write", "roles", "write", "Create and update role assignments."),
    PermissionDefinition("permissions:read", "permissions", "read", "Read permission definitions."),
    PermissionDefinition("sources:read", "sources", "read", "Read source metadata and accessible content."),
    PermissionDefinition("sources:write", "sources", "write", "Create and update source records."),
    PermissionDefinition("artifacts:read", "artifacts", "read", "Read generated knowledge artifacts."),
    PermissionDefinition("artifacts:write", "artifacts", "write", "Create and update generated artifacts."),
    PermissionDefinition("agents:read", "agents", "read", "Read multi-agent status and execution history."),
    PermissionDefinition("agents:write", "agents", "write", "Run and manage multi-agent research pipelines."),
    PermissionDefinition(
        "retrieval:read",
        "retrieval",
        "read",
        "Read retrieval results, reasoning history, and citations.",
    ),
    PermissionDefinition("retrieval:write", "retrieval", "write", "Run hybrid retrieval and reasoning queries."),
    PermissionDefinition("documents:read", "documents", "read", "Read processed knowledge documents."),
    PermissionDefinition("documents:write", "documents", "write", "Upload and process knowledge documents."),
    PermissionDefinition("documents:delete", "documents", "delete", "Delete processed knowledge documents."),
    PermissionDefinition("knowledge_dna:read", "knowledge_dna", "read", "Read Knowledge DNA profiles."),
    PermissionDefinition(
        "knowledge_dna:write",
        "knowledge_dna",
        "write",
        "Generate and update Knowledge DNA profiles.",
    ),
    PermissionDefinition("knowledge_dna:delete", "knowledge_dna", "delete", "Delete Knowledge DNA profiles."),
    PermissionDefinition("graph:read", "graph", "read", "Read knowledge graph entities and relationships."),
    PermissionDefinition("graph:write", "graph", "write", "Create and update knowledge graph relationships."),
    PermissionDefinition(
        "workspace:read",
        "workspace",
        "read",
        "Read workspace notes, projects, tasks, and canvas state.",
    ),
    PermissionDefinition("workspace:write", "workspace", "write", "Create and organize workspace thinking artifacts."),
    PermissionDefinition("learning:read", "learning", "read", "Read adaptive learning assets and progress reports."),
    PermissionDefinition(
        "learning:write",
        "learning",
        "write",
        "Generate and review adaptive learning assets.",
    ),
    PermissionDefinition("admin:manage", "admin", "manage", "Manage administrative settings and access control."),
)

SYSTEM_ROLES: dict[str, dict[str, object]] = {
    "owner": {
        "description": "Full administrative control of ResearchForge OS.",
        "permissions": tuple(permission.name for permission in SYSTEM_PERMISSIONS),
    },
    "researcher": {
        "description": "Create, read, and organize research knowledge.",
        "permissions": (
            "sources:read",
            "sources:write",
            "artifacts:read",
            "artifacts:write",
            "agents:read",
            "agents:write",
            "retrieval:read",
            "retrieval:write",
            "documents:read",
            "documents:write",
            "documents:delete",
            "knowledge_dna:read",
            "knowledge_dna:write",
            "knowledge_dna:delete",
            "graph:read",
            "graph:write",
            "workspace:read",
            "workspace:write",
            "learning:read",
            "learning:write",
        ),
    },
    "viewer": {
        "description": "Read accessible sources, artifacts, and graph relationships.",
        "permissions": (
            "sources:read",
            "artifacts:read",
            "agents:read",
            "retrieval:read",
            "documents:read",
            "knowledge_dna:read",
            "graph:read",
            "workspace:read",
            "learning:read",
        ),
    },
}
