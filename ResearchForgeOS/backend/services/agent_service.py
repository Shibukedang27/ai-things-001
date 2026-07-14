from __future__ import annotations

from ai.agents import AgentManager, AgentOrchestrator
from ai.agents.core.types import (
    AgentDNA,
    AgentDocument,
    AgentExecutionContext,
    AgentOutput,
    AgentRole,
    AgentTaskResult,
    PipelineStatus,
    TaskStatus,
)
from sqlalchemy.orm import Session

from backend.exceptions import NotFoundError, ValidationError
from backend.models.agent import Agent, AgentResponse, AgentTask, ExecutionLog, PipelineHistory
from backend.models.document import Document
from backend.models.knowledge_dna import KnowledgeDNA
from backend.models.user import User
from backend.repositories.agent_repository import AgentRepository, AgentTaskRepository, PipelineHistoryRepository
from backend.repositories.document_repository import DocumentRepository
from backend.repositories.knowledge_dna_repository import KnowledgeDNARepository
from backend.schemas.agent import MultiAgentAnalysisRequest, PipelineStatusRead, TaskActionResponse


class AgentService:
    def __init__(self, session: Session, orchestrator: AgentOrchestrator | None = None) -> None:
        self.session = session
        self.orchestrator = orchestrator or AgentOrchestrator()
        self.manager = AgentManager(self.orchestrator.registry)
        self.agents = AgentRepository(session)
        self.pipelines = PipelineHistoryRepository(session)
        self.tasks = AgentTaskRepository(session)
        self.documents = DocumentRepository(session)
        self.dna = KnowledgeDNARepository(session)

    async def run_analysis(self, payload: MultiAgentAnalysisRequest, current_user: User) -> PipelineHistory:
        self.ensure_agent_catalog()
        document = self._document(payload.document_id)
        dna = self.dna.get_by_document_id(document.id)
        pipeline = PipelineHistory(
            document_id=document.id,
            knowledge_dna_id=dna.id if dna else None,
            requested_by_user_id=current_user.id,
            status=PipelineStatus.RUNNING.value,
            final_response={},
            request_options=payload.request_options,
        )
        self.pipelines.add(pipeline)
        self.session.commit()

        roles = self._roles(payload.include_agents)
        context = self._context(document, dna, payload.request_options)
        result = await self.orchestrator.run(context, pipeline_id=pipeline.id, roles=roles)

        pipeline.status = result.status.value
        pipeline.final_response = result.final_response
        self._persist_results(pipeline, result.task_results, result.execution_log)
        self.session.commit()
        loaded = self.pipelines.get_full(pipeline.id)
        if loaded is None:
            raise NotFoundError("Pipeline history could not be loaded.")
        return loaded

    def list_agent_status(self) -> list[Agent]:
        self.ensure_agent_catalog()
        return list(self.agents.list_agents())

    def execution_history(self, *, offset: int, limit: int) -> list[PipelineHistory]:
        return list(self.pipelines.list_history(offset=offset, limit=limit))

    def pipeline_status(self, pipeline_id: str) -> PipelineStatusRead:
        pipeline = self._pipeline(pipeline_id)
        tasks = pipeline.tasks
        return PipelineStatusRead(
            pipeline_id=pipeline.id,
            status=pipeline.status,
            document_id=pipeline.document_id,
            task_count=len(tasks),
            completed_tasks=sum(1 for task in tasks if task.status == TaskStatus.COMPLETED.value),
            failed_tasks=sum(1 for task in tasks if task.status == TaskStatus.FAILED.value),
            canceled_tasks=sum(1 for task in tasks if task.status == TaskStatus.CANCELED.value),
        )

    def cancel_task(self, task_id: str) -> TaskActionResponse:
        task = self._task(task_id)
        if task.status in {TaskStatus.COMPLETED.value, TaskStatus.FAILED.value}:
            raise ValidationError("Only pending or running tasks can be canceled.")
        task.status = TaskStatus.CANCELED.value
        self.session.add(
            ExecutionLog(
                pipeline_id=task.pipeline_id,
                task_id=task.id,
                event_type="task_canceled",
                agent_role=task.agent_role,
                message=f"Task {task.id} was canceled.",
                metadata_json={},
            )
        )
        self.session.commit()
        return TaskActionResponse(task_id=task.id, status=task.status, message="Task canceled.")

    async def retry_task(self, task_id: str) -> TaskActionResponse:
        task = self._task(task_id)
        pipeline = self._pipeline(task.pipeline_id)
        document = self._document(pipeline.document_id)
        dna = self.dna.get_by_document_id(document.id)
        role = AgentRole(task.agent_role)

        task.status = TaskStatus.RETRYING.value
        self.session.commit()

        context = self._context(document, dna, pipeline.request_options)
        result = await self.orchestrator.run(context, pipeline_id=pipeline.id, roles=[role])
        self._persist_results(pipeline, result.task_results, result.execution_log)
        pipeline.status = (
            result.status.value
            if result.status == PipelineStatus.FAILED
            else PipelineStatus.COMPLETED.value
        )
        pipeline.final_response = result.final_response
        self.session.commit()
        return TaskActionResponse(task_id=task.id, status=TaskStatus.RETRYING.value, message="Task retry executed.")

    def ensure_agent_catalog(self) -> None:
        for agent_status in self.manager.status():
            role = str(agent_status["role"])
            model = self.agents.get_by_role(role)
            capabilities = self._capabilities_for(role)
            if model is None:
                self.agents.add(
                    Agent(
                        role=role,
                        name=str(agent_status["name"]),
                        description=str(agent_status["description"]),
                        status=str(agent_status["status"]),
                        default_priority=int(agent_status["default_priority"]),
                        timeout_seconds=float(agent_status["timeout_seconds"]),
                        max_retries=int(agent_status["max_retries"]),
                        capabilities=capabilities,
                    )
                )
            else:
                model.name = str(agent_status["name"])
                model.description = str(agent_status["description"])
                model.status = str(agent_status["status"])
                model.default_priority = int(agent_status["default_priority"])
                model.timeout_seconds = float(agent_status["timeout_seconds"])
                model.max_retries = int(agent_status["max_retries"])
                model.capabilities = capabilities
        self.session.commit()

    def _persist_results(
        self,
        pipeline: PipelineHistory,
        task_results: list[AgentTaskResult],
        execution_log: list[dict[str, object]],
    ) -> None:
        agent_lookup = {agent.role: agent for agent in self.agents.list_agents()}
        task_lookup: dict[str, AgentTask] = {}
        for result in task_results:
            agent = agent_lookup.get(result.role.value)
            task = AgentTask(
                id=result.task_id,
                pipeline_id=pipeline.id,
                agent_id=agent.id if agent else None,
                agent_role=result.role.value,
                status=result.status.value,
                priority=self.orchestrator.priority_manager.priority_for(result.role),
                attempts=result.attempts,
                max_retries=agent.max_retries if agent else 0,
                timeout_seconds=agent.timeout_seconds if agent else 0,
                duration_ms=result.duration_ms,
                error_message=result.error_message,
                task_payload={"pipeline_id": pipeline.id, "agent_role": result.role.value},
            )
            self.session.merge(task)
            task_lookup[result.task_id] = task
            if result.output is not None:
                self.session.add(self._response(result.task_id, result.output))

        for log_item in execution_log:
            task_id = str(log_item.get("task_id")) if log_item.get("task_id") else None
            role = str(log_item.get("agent")) if log_item.get("agent") else None
            self.session.add(
                ExecutionLog(
                    pipeline_id=pipeline.id,
                    task_id=task_id if task_id in task_lookup else None,
                    event_type=str(log_item.get("event", "pipeline_event")),
                    agent_role=role,
                    message=str(log_item),
                    metadata_json=log_item,
                )
            )

    def _response(self, task_id: str, output: AgentOutput) -> AgentResponse:
        return AgentResponse(
            task_id=task_id,
            agent_role=output.role.value,
            title=output.title,
            summary=output.summary,
            confidence_score=output.confidence_score,
            response_data=output.data,
            warnings=output.warnings,
            sources=output.sources,
        )

    def _context(
        self,
        document: Document,
        dna: KnowledgeDNA | None,
        request_options: dict[str, object],
    ) -> AgentExecutionContext:
        summaries = {summary.summary_type: summary.content for summary in document.summaries}
        agent_document = AgentDocument(
            id=document.id,
            title=document.title,
            category=document.category,
            difficulty=document.difficulty,
            estimated_reading_time_minutes=document.estimated_reading_time_minutes,
            topics=document.topics,
            cleaned_text=document.cleaned_text,
            summaries=summaries,
            concepts=[
                {
                    "id": concept.id,
                    "name": concept.name,
                    "concept_type": concept.concept_type,
                    "description": concept.description,
                    "prerequisites": concept.prerequisites,
                    "dependencies": concept.dependencies,
                    "difficulty_level": concept.difficulty_level,
                    "confidence_score": concept.confidence_score,
                }
                for concept in document.concepts
            ],
            keywords=[keyword.value for keyword in document.keywords],
            technologies=[
                {
                    "id": technology.id,
                    "name": technology.name,
                    "category": technology.category,
                    "confidence_score": technology.confidence_score,
                    "evidence": technology.evidence,
                }
                for technology in document.technologies
            ],
            algorithms=[algorithm.get("name", "") for algorithm in document.algorithms if algorithm.get("name")],
            definitions=document.definitions,
            code_snippets=document.code_snippets,
            references=[
                {
                    "title": reference.title,
                    "authors": reference.authors,
                    "year": reference.year,
                    "url": reference.url,
                    "citation_text": reference.citation_text,
                }
                for reference in document.references
            ],
        )
        agent_dna = None
        if dna is not None:
            agent_dna = AgentDNA(
                id=dna.id,
                research_category=dna.research_category,
                knowledge_score=dna.knowledge_score,
                interview_importance=dna.interview_importance,
                industry_relevance=dna.industry_relevance,
                implementation_complexity=dna.implementation_complexity,
                primary_concepts=dna.primary_concepts,
                secondary_concepts=dna.secondary_concepts,
                prerequisites=dna.prerequisites,
                future_learning_topics=dna.future_learning_topics,
                learning_order=dna.learning_order,
                estimated_mastery_time_hours=dna.estimated_mastery_time_hours,
                parent_topics=dna.parent_topics,
                child_topics=dna.child_topics,
                sibling_topics=dna.sibling_topics,
                knowledge_chains=dna.knowledge_chains,
                research_evolution=dna.research_evolution,
            )
        return AgentExecutionContext(document=agent_document, dna=agent_dna, request_options=request_options)

    def _document(self, document_id: str) -> Document:
        document = self.documents.get_full(document_id)
        if document is None:
            raise NotFoundError("Document was not found.")
        return document

    def _pipeline(self, pipeline_id: str) -> PipelineHistory:
        pipeline = self.pipelines.get_full(pipeline_id)
        if pipeline is None:
            raise NotFoundError("Pipeline history was not found.")
        return pipeline

    def _task(self, task_id: str) -> AgentTask:
        task = self.tasks.get_full(task_id)
        if task is None:
            raise NotFoundError("Agent task was not found.")
        return task

    def _roles(self, include_agents: list[str] | None) -> list[AgentRole] | None:
        if include_agents is None:
            return None
        try:
            return [AgentRole(value) for value in include_agents]
        except ValueError as exc:
            valid_roles = [role.value for role in AgentRole]
            raise ValidationError("Unsupported agent role.", details={"valid_roles": valid_roles}) from exc

    def _capabilities_for(self, role: str) -> list[str]:
        capability_map = {
            AgentRole.RESEARCH.value: ["context", "purpose", "overview"],
            AgentRole.CONCEPT.value: ["concepts", "definitions", "hierarchy", "prerequisites"],
            AgentRole.TEACHER.value: ["explanations", "analogies", "teaching_levels"],
            AgentRole.CODE.value: ["python", "java", "sql", "api_examples", "algorithm_explanation"],
            AgentRole.QUIZ.value: ["mcq", "coding_questions", "flashcards", "interview_questions"],
            AgentRole.SUMMARY.value: ["executive_summary", "technical_summary", "detailed_summary"],
            AgentRole.CITATION.value: ["references", "bibliography", "source_tracking"],
            AgentRole.ROADMAP.value: ["learning_path", "projects", "books", "courses"],
            AgentRole.KNOWLEDGE_GRAPH.value: ["nodes", "edges", "deduplication", "consistency"],
            AgentRole.QUALITY_ASSURANCE.value: ["validation", "clarity", "deduplication"],
        }
        return capability_map.get(role, [])
