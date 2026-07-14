# Installation

ResearchForge OS is currently in the architecture and planning phase. This guide prepares the local workspace and infrastructure dependencies only.

## Prerequisites

- Git
- Docker Desktop or a compatible Docker runtime
- Python 3.11 or newer
- Node.js 20 or newer, planned for the future frontend

## Clone

```bash
git clone <repository-url>
cd ResearchForgeOS
```

## Create a Python Environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The dependency file lists the planned Python surface. Exact versions should be pinned when implementation begins.

## Start Local Infrastructure

```bash
docker compose up -d
```

Planned local services:

- PostgreSQL for application records
- Redis for queueing and cache
- Qdrant for vector search
- Neo4j for knowledge graph storage
- MinIO for object storage

## Verify Services

```bash
docker compose ps
```

## Current Phase Note

There is no frontend or backend server to start yet. That is intentional. This repository is ready for the next implementation phase once the product architecture is approved.
