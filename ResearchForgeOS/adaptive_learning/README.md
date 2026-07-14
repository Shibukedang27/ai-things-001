# Adaptive Learning Engine

The Adaptive Learning Engine converts processed ResearchForge knowledge into a personalized learning system.

It generates:

- Definition, concept, formula, algorithm, code, interview, true/false, image-placeholder, fill-in-the-blank, and reverse flashcards
- Adaptive timed quizzes with MCQ, multiple-correct, fill-in-the-blank, code-completion, scenario, case-study, research, debugging, and algorithm questions
- Interview preparation questions across behavioral, technical, ML, system design, backend, NLP, generative AI, prompt engineering, Python, Java, and SQL categories
- Coding challenges with starter code, hints, optimal solution, complexity analysis, alternative solutions, edge cases, and unit tests
- Daily, weekly, monthly, quick, exam, interview, and coding revision plans
- Memory state, spaced repetition schedules, retention scores, mastery percentages, learning analytics, achievements, and certificate signals

## Core Modules

```text
adaptive_learning/
  engine.py        Orchestrates learning asset generation
  flashcards.py    Generates multiple flashcard families
  quizzes.py       Generates and grades adaptive knowledge tests
  interviews.py    Generates interview preparation assets
  coding.py        Generates coding challenges
  scheduling.py    FSRS-inspired spaced repetition scheduler
  revision.py      Builds revision plans
  analytics.py     Produces learning and mastery analytics
  achievements.py  Emits badges, milestones, streaks, and skill-level signals
  types.py         Typed dataclasses and enums
```

The package is deterministic and model-provider independent, so it can run during document ingestion, tests, workers, and API requests without external AI credentials.
