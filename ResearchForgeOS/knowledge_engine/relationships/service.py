from knowledge_engine.types import ConceptCandidate, RelationshipCandidate, TechnologyCandidate


class RelationshipExtractor:
    def extract(
        self,
        *,
        concepts: list[ConceptCandidate],
        technologies: list[TechnologyCandidate],
    ) -> list[RelationshipCandidate]:
        relationships: list[RelationshipCandidate] = []
        for concept in concepts:
            for dependency in concept.dependencies:
                relationships.append(
                    RelationshipCandidate(
                        source_name=concept.name,
                        target_name=dependency,
                        relationship_type="depends_on",
                        description=f"{concept.name} depends on {dependency}.",
                        confidence_score=min(0.86, concept.confidence_score),
                    )
                )
            for prerequisite in concept.prerequisites:
                relationships.append(
                    RelationshipCandidate(
                        source_name=prerequisite,
                        target_name=concept.name,
                        relationship_type="prerequisite_for",
                        description=f"{prerequisite} is useful before learning {concept.name}.",
                        confidence_score=0.68,
                    )
                )

        for technology in technologies[:8]:
            target = concepts[0].name if concepts else "Document"
            relationships.append(
                RelationshipCandidate(
                    source_name=technology.name,
                    target_name=target,
                    relationship_type="used_in",
                    description=f"{technology.name} appears as a {technology.category} in this source.",
                    confidence_score=technology.confidence_score,
                    metadata={"technology_category": technology.category},
                )
            )
        return relationships[:80]
