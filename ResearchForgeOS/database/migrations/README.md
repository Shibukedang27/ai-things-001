# Alembic Migrations

Run migrations from the project root:

```bash
alembic -c database/alembic.ini upgrade head
```

The migration environment reads `DATABASE_URL` through the backend settings module.
