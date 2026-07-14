from knowledge_engine.dna.types import DNATechnologyInput


class TechnologyTaxonomy:
    PROGRAMMING_LANGUAGE_CATEGORIES = {"language"}
    FRAMEWORK_CATEGORIES = {"backend_framework", "frontend_framework", "ai_framework", "ml_framework"}
    LIBRARY_CATEGORIES = {"orm", "database_tooling", "ml_framework", "ai_framework"}
    INFRASTRUCTURE_CATEGORIES = {"database", "cache", "infrastructure", "cloud", "vector_database", "graph_database"}

    def programming_languages(self, technologies: list[DNATechnologyInput]) -> list[str]:
        return self._names_for_categories(technologies, self.PROGRAMMING_LANGUAGE_CATEGORIES)

    def frameworks(self, technologies: list[DNATechnologyInput]) -> list[str]:
        return self._names_for_categories(technologies, self.FRAMEWORK_CATEGORIES)

    def libraries(self, technologies: list[DNATechnologyInput]) -> list[str]:
        return self._names_for_categories(technologies, self.LIBRARY_CATEGORIES)

    def infrastructure(self, technologies: list[DNATechnologyInput]) -> list[str]:
        return self._names_for_categories(technologies, self.INFRASTRUCTURE_CATEGORIES)

    def _names_for_categories(self, technologies: list[DNATechnologyInput], categories: set[str]) -> list[str]:
        return [
            technology.name
            for technology in technologies
            if technology.category in categories
        ]
