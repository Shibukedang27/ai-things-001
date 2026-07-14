# OfferPilot AI Security

This document describes security controls, implemented safeguards, and production hardening requirements for OfferPilot AI.

## Security Objectives

- Protect candidate identity, resumes, interview answers, and generated feedback.
- Prevent unauthorized access to protected APIs.
- Store credentials and tokens safely.
- Keep production secrets out of source control.
- Reduce risk from live code execution and file upload features.
- Provide operational visibility through logs and request IDs.

## Authentication

OfferPilot AI implements:

- Signup and login.
- JWT access tokens.
- Refresh token rotation.
- Logout and session revocation.
- Forgot password and reset password.
- Argon2 password hashing.
- User profile endpoints.
- Role management.
- Session management.

Protected routes require:

```http
Authorization: Bearer <access_token>
```

## Password Security

- Passwords are hashed with Argon2.
- Plaintext passwords are never stored.
- Password strength validation is enforced on signup and reset.
- Production should configure monitoring for repeated failed login attempts.

## Token Security

- Access tokens are short-lived JWTs.
- Refresh tokens are rotated.
- Refresh token fingerprints are stored server-side.
- Password reset tokens are stored as fingerprints.
- Logout revokes the current session and optional refresh token.

## Authorization

- Role-based access control supports admin-only operations.
- Role endpoints require admin privileges.
- Product data endpoints require a valid authenticated principal.
- Repository methods scope user-owned resources by user ID where applicable.

## API Security Controls

Implemented controls:

- Request validation through Pydantic schemas.
- Standardized error responses.
- Request ID propagation.
- Trusted host middleware.
- CORS allowlist configuration.
- Security headers:
  - `X-Content-Type-Options`
  - `X-Frame-Options`
  - `Referrer-Policy`
  - `Permissions-Policy`

## Resume Upload Security

Current controls:

- PDF upload endpoint requires authentication.
- File size is limited by configuration.
- Text extraction is isolated in service logic.
- Original files are not persisted by default.

Production recommendations:

- Virus scan uploaded files.
- Store original files in private object storage.
- Encrypt stored artifacts.
- Enforce retention and deletion policies.
- Avoid sending resume text to external providers without explicit consent.

## Live Coding Security

Current controls:

- Authentication required.
- Source length and stdin length are limited.
- Execution timeout is enforced.
- Python runner avoids shell invocation.
- Java and SQL execution use constrained adapters.
- Static safety checks block risky imports and patterns.

Production recommendations:

- Move execution into isolated worker containers.
- Use per-run containers or sandbox runtimes.
- Disable filesystem and network access for submissions.
- Add CPU, memory, file, and process limits at the container level.
- Store only necessary source and output data.

## Secrets Management

Never commit:

- JWT secret keys.
- API provider keys.
- Database passwords.
- Redis passwords.
- SMTP credentials.
- Production `.env` files.

Use `config/env/production.env.example` only as a template.

## Production Hardening Checklist

- Replace all placeholder secrets.
- Use HTTPS everywhere.
- Set strict CORS origins.
- Set trusted hosts to production domains.
- Disable Swagger in production unless protected.
- Enable centralized logging.
- Add rate limits at the edge.
- Add WAF or equivalent request filtering.
- Enable managed database backups.
- Use private networking between services.
- Review live coding isolation before enabling in public production.

## Privacy Considerations

OfferPilot AI can process sensitive data:

- Resume content.
- Interview transcripts.
- Performance reports.
- Skill gaps.
- Learning plans.

Recommended privacy controls:

- Data export and deletion workflows.
- Consent for AI provider processing.
- Explicit retention policy.
- Audit logs for admin actions.
- Tenant isolation before enterprise multi-tenant use.

## Security Test Coverage

The test suite includes authentication, protected route, validation, OpenAPI, database metadata, and provider tests. Run:

```bash
.venv/bin/python tests/run_reports.py
```
