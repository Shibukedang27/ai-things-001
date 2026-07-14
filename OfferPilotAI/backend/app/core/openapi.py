"""OpenAPI metadata."""

OPENAPI_TAGS = [
    {
        "name": "Health",
        "description": "Operational health, liveness, and readiness checks.",
    },
    {
        "name": "Authentication",
        "description": "Signup, login, logout, JWT refresh, password reset, profile, roles, and sessions.",
    },
    {
        "name": "Analytics",
        "description": "Topic accuracy, progress, heat maps, radar charts, trends, history, and performance graphs.",
    },
    {
        "name": "Interview Engine",
        "description": "Role-based question generation, timed interview sessions, answers, and history.",
    },
    {
        "name": "AI Evaluation",
        "description": "Answer scoring, ideal answers, improvement suggestions, related topics, and difficulty analysis.",
    },
    {
        "name": "Learning Recommendations",
        "description": "Automatic weak-topic analysis, resource suggestions, and personalized practice roadmaps.",
    },
    {
        "name": "Live Coding",
        "description": "Code editor support, execution, static analysis, complexity review, optimization, and submissions.",
    },
    {
        "name": "Resume Analyzer",
        "description": "Resume PDF analysis, skill extraction, ATS scoring, job matching, and skill gap reporting.",
    },
    {
        "name": "Question Catalog",
        "description": "Supported question categories and difficulty metadata.",
    },
    {
        "name": "Interview Sessions",
        "description": "Interview session planning and lifecycle endpoints.",
    },
    {"name": "Users", "description": "User profile persistence endpoints."},
    {"name": "Answers", "description": "Candidate answer persistence endpoints."},
    {"name": "Reports", "description": "Interview report persistence endpoints."},
    {"name": "Learning Roadmaps", "description": "Personalized learning roadmap endpoints."},
    {"name": "Leaderboard", "description": "Candidate ranking and progress endpoints."},
    {"name": "Sessions", "description": "Authenticated session persistence endpoints."},
    {"name": "Interview History", "description": "Interview audit history endpoints."},
]
