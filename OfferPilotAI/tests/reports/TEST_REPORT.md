# OfferPilot AI Test Report

Status: **PASSED**
Generated: `2026-07-14 13:51:32 IST`
Command: `/Users/maniacsday/Documents/Codex/2026-07-14/you-are-a-senior-software-architect/OfferPilotAI/.venv/bin/python -m pytest tests --junitxml /Users/maniacsday/Documents/Codex/2026-07-14/you-are-a-senior-software-architect/OfferPilotAI/tests/reports/junit.xml`

## Suite Summary

| Tests | Failures | Errors | Skipped | Time (s) | Exit Code |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 69 | 0 | 0 | 0 | 2.495 | 0 |

## Slowest Tests

| Test | Outcome | Time (s) |
| --- | --- | ---: |
| `tests.backend.api.test_api_contracts::test_openapi_documents_all_product_api_surfaces` | passed | 0.277 |
| `tests.backend.test_openapi::test_openapi_schema_is_available` | passed | 0.277 |
| `tests.backend.test_security::test_password_hashing_and_verification` | passed | 0.111 |
| `tests.backend.database.test_database_metadata::test_alembic_migrations_form_single_linear_chain` | passed | 0.063 |
| `tests.backend.test_analytics::test_analytics_overview_generates_all_requested_views` | passed | 0.063 |
| `tests.backend.api.test_api_contracts::test_public_get_contracts_return_standard_response[/-expected_keys0]` | passed | 0.045 |
| `tests.backend.api.test_api_contracts::test_protected_get_contracts_require_bearer_token[/api/v1/interview-history/]` | passed | 0.045 |
| `tests.backend.api.test_api_contracts::test_protected_get_contracts_require_bearer_token[/api/v1/leaderboard/]` | passed | 0.042 |
| `tests.backend.api.test_api_contracts::test_protected_get_contracts_require_bearer_token[/api/v1/sessions/]` | passed | 0.040 |
| `tests.backend.api.test_api_contracts::test_public_get_contracts_return_standard_response[/api/v1/questions/categories-None]` | passed | 0.038 |

## Failures

No failures or errors.
