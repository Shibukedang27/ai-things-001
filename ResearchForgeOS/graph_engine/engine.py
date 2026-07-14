from graph_engine.analytics import GraphAnalyticsEngine
from graph_engine.layout import InteractionManager, LayoutManager
from graph_engine.merge import NodeMerger, RelationshipMerger
from graph_engine.node_generator import NodeGenerator
from graph_engine.relationship_generator import RelationshipGenerator
from graph_engine.types import GraphBuildInput, GraphBuildResult


class InteractiveKnowledgeGraphEngine:
    def __init__(
        self,
        node_generator: NodeGenerator | None = None,
        relationship_generator: RelationshipGenerator | None = None,
        node_merger: NodeMerger | None = None,
        relationship_merger: RelationshipMerger | None = None,
        layout_manager: LayoutManager | None = None,
        analytics_engine: GraphAnalyticsEngine | None = None,
        interaction_manager: InteractionManager | None = None,
    ) -> None:
        self.node_generator = node_generator or NodeGenerator()
        self.relationship_generator = relationship_generator or RelationshipGenerator()
        self.node_merger = node_merger or NodeMerger()
        self.relationship_merger = relationship_merger or RelationshipMerger()
        self.layout_manager = layout_manager or LayoutManager()
        self.analytics_engine = analytics_engine or GraphAnalyticsEngine()
        self.interaction_manager = interaction_manager or InteractionManager()

    def build(self, graph_input: GraphBuildInput) -> GraphBuildResult:
        generated_nodes = self.node_generator.generate(graph_input)
        nodes = self.node_merger.merge(generated_nodes)
        generated_edges = self.relationship_generator.generate(graph_input)
        edges = self.relationship_merger.merge(generated_edges, {node.stable_key for node in nodes})
        layout = self.layout_manager.layout(nodes, edges)
        analytics = self.analytics_engine.analyze(nodes, edges)
        insights = self.analytics_engine.insights(nodes, edges)
        interaction = self.interaction_manager.interaction_payload(len(nodes), len(edges))
        return GraphBuildResult(
            nodes=nodes,
            edges=edges,
            layout=layout,
            analytics=analytics,
            insights=insights,
            interaction=interaction,
        )
