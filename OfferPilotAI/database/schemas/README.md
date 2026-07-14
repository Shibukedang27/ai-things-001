# Database Schema

Alembic migrations are the source of truth for the OfferPilot AI PostgreSQL schema.

Current schema entrypoint:

- `backend/migrations/versions/20260714_0001_initial_product_schema.py`

Current production tables:

- `users`
- `interviews`
- `questions`
- `answers`
- `reports`
- `learning_roadmaps`
- `leaderboard`
- `sessions`
- `interview_history`
- `auth_credentials`
- `roles`
- `user_roles`
- `refresh_tokens`
- `password_reset_tokens`
- `answer_evaluations`

`learning_roadmaps` also stores generated recommendation sections:

- `weak_topics`
- `leetcode_problems`
- `hackerrank_problems`
- `books`
- `courses`
- `youtube_videos`
- `daily_practice_plan`
- `weekly_roadmap`
- `monthly_roadmap`
- `source_summary`

Generate SQL without applying it:

```bash
alembic -c backend/alembic.ini upgrade head --sql
```
