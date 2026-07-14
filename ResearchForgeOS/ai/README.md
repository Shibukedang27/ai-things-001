# AI

Multi-agent research system for ResearchForge OS.

The AI layer is organized around specialized agents with one responsibility each.
Requests flow through an orchestrator that creates tasks, runs the configured
pipeline, collects structured outputs, and produces a reviewed final response.

## Agent Pipeline

```text
Research Agent
Concept Agent
Teacher Agent
Code Agent
Quiz Agent
Citation Agent
Roadmap Agent
Knowledge Graph Agent
Quality Assurance Agent
```

## Architecture

```text
ai/
  agents/
    core/          Orchestrator, registry, task queue, retry, execution, aggregation
    specialists/   Research, concept, teaching, code, quiz, citation, roadmap, graph, QA agents
```

Core components:

- `AgentOrchestrator` receives requests and coordinates the full pipeline.
- `AgentRegistry` keeps agent roles discoverable and replaceable.
- `AgentTaskQueue` prioritizes pending work.
- `ExecutionPipeline` applies timeouts, retry handling, and execution logging.
- `ErrorRecovery` classifies failures and marks whether retry is recommended.
- `ResponseAggregator` combines agent outputs into the final research response.
- `AgentManager` exposes runtime agent status and capabilities.

Current status: Phase 5 Multi-Agent AI Research System implemented.
