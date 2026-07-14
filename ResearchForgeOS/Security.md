# Security

ResearchForge OS handles private source material, model calls, generated knowledge, and potentially sensitive research. Security must be designed into the platform from the first implementation phase.

## Security Principles

- Workspace isolation is mandatory.
- User-uploaded files are untrusted input.
- AI outputs must not bypass authorization.
- Source citations must not leak inaccessible material.
- Secrets must never be committed.
- Deletion must propagate across all storage systems.

## Threat Model

Primary risks:

- Unauthorized access to private documents
- Cross-workspace data leakage in search or RAG
- Prompt injection from uploaded or crawled sources
- Malicious file uploads
- Hallucinated or fabricated citations
- Leaked model provider credentials
- Incomplete deletion across vector, graph, relational, and object stores

## Access Control

Future implementation should include:

- Workspace-scoped authorization on every request
- Role-based permissions
- Resource-level checks for sources and artifacts
- Audit logs for sensitive operations
- Short-lived signed URLs for file access

## Upload Security

Uploaded files should be:

- Size limited
- Type checked
- Malware scanned
- Parsed in isolated workers where possible
- Stored with content hashes
- Associated with explicit workspace ownership

## AI Security

AI workflows should:

- Treat source text as data, not instructions.
- Separate system instructions from retrieved content.
- Filter retrieval by workspace and permission scope.
- Require citations for source-grounded claims.
- Expose uncertainty when evidence is weak.
- Log model calls without storing unnecessary sensitive content.

## Data Privacy

Future privacy requirements:

- User-controlled deletion
- Workspace export
- Clear retention policies
- No training on private user data without explicit consent
- Configurable model provider routing
- Redaction support for sensitive documents

## Operational Security

- Use managed secrets.
- Rotate credentials.
- Enforce TLS in production.
- Restrict database network access.
- Use least-privilege service accounts.
- Monitor failed auth, unusual retrieval patterns, and high-volume exports.

## Security Review Gates

Before launch:

- Authentication review
- Authorization tests
- Prompt injection test suite
- Upload validation tests
- Data deletion tests
- Secret scanning
- Dependency scanning
- Penetration test for core flows
