# Tests

OfferPilot AI uses pytest for backend unit, integration, API, database, and authentication coverage.

## Run Everything

```bash
python tests/run_reports.py
```

The report runner writes:

- `tests/reports/junit.xml`
- `tests/reports/TEST_REPORT.md`
- `tests/reports/latest-summary.json`

## Focused Runs

```bash
pytest tests/backend/unit
pytest tests/backend/integration
pytest tests/backend/api
pytest tests/backend/database
pytest tests/backend/auth
```

Markers are registered in `pytest.ini` for CI filtering.
