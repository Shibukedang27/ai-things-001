# Seed Data

Seed data is applied after Alembic migrations, not during PostgreSQL container initialization.

Run from the project root:

```bash
python backend/scripts/seed_data.py
```

The seed script is idempotent and creates representative records for:

- Users
- Interviews
- Questions
- Answers
- Reports
- LearningRoadmaps
- Leaderboard
- Sessions
- InterviewHistory
- AuthCredentials
- Roles
- UserRoles
- RefreshTokens

The sample candidate login is:

- Email: `candidate@example.com`
- Password: `OfferPilotAI!2026`
