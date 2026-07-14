# OfferPilot AI Future Scope

This roadmap captures planned product and technical expansion beyond the current implementation.

## Product Roadmap

### Near Term

- Full authentication UI and protected frontend routes.
- Interview Engine UI for session creation, timer, question flow, and answer capture.
- Evaluation UI for answer-level and interview-level feedback.
- Recommendation UI connected to persisted roadmaps.
- Resume analyzer history and comparison views.
- Live coding submission history and challenge templates.

### Mid Term

- External AI provider integration.
- Voice-based interview practice.
- Video interview simulation.
- Real-time transcription.
- Interview report export to PDF.
- Company and role-specific question packs.
- Team dashboards for bootcamps, universities, and recruiters.
- Admin portal for content and user management.

### Long Term

- Multi-tenant enterprise workspaces.
- Adaptive interview plans based on repeated performance.
- Human coach review workflows.
- ATS and job-board integrations.
- Calendar and meeting integrations.
- Browser extension for job description capture.
- Native mobile companion app.

## Technical Roadmap

- Background job processing for long-running AI, PDF, and analytics tasks.
- Object storage for uploaded resumes and generated report artifacts.
- Dedicated live coding sandbox service.
- Streaming APIs for interview progress and evaluation status.
- OpenTelemetry instrumentation.
- CI/CD pipelines with build, test, security scan, deploy, smoke tests.
- Row-level tenant isolation for enterprise customers.
- Data retention and privacy automation.

## AI Roadmap

- Pluggable provider system for OpenAI-compatible APIs.
- Prompt templates and evaluation rubrics per role and seniority.
- Model output validation and guardrails.
- Retrieval-augmented question generation from company role profiles.
- Explainable scoring with rubric evidence.
- A/B testing for coaching recommendations.

## Analytics Roadmap

- Cohort analytics.
- Skill velocity over time.
- Interview readiness score.
- Hiring funnel analytics for enterprise teams.
- Custom dashboards for organizations.
- Benchmarking by role, seniority, and geography.

## Commercial Roadmap

- Free tier with limited interview sessions.
- Pro tier for unlimited practice and resume analysis.
- Team tier for bootcamps and placement programs.
- Enterprise tier with SSO, tenant isolation, audit logs, and admin analytics.
- API tier for embedding interview preparation in third-party platforms.

## Future Risk Areas

- AI quality, hallucination, and bias.
- Resume and interview transcript privacy.
- Live code execution isolation.
- Multi-tenant authorization complexity.
- Data retention obligations by region.
- Cost control for AI inference and PDF processing.
