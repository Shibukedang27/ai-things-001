# OfferPilot AI Documentation

This folder contains the professional documentation set for OfferPilot AI. It is intended for product owners, engineers, security reviewers, deployment operators, and commercial stakeholders.

## Core Documents

| Document | Purpose |
| --- | --- |
| [Architecture](Architecture.md) | System design, module boundaries, request flows, deployment topology |
| [API](API.md) | REST standards, endpoints, authentication, response formats |
| [Database](Database.md) | PostgreSQL schema, relationships, migrations, seed data |
| [Installation](Installation.md) | Local setup, Docker startup, developer workflows |
| [Deployment](Deployment.md) | Production deployment, environment strategy, release process |
| [Brand Guidelines](../BrandGuidelines.md) | OfferPilot AI palette, typography, logo placeholders, theme, and UI standards |
| [Security](Security.md) | Authentication, authorization, data protection, operational controls |
| [Folder Structure](FolderStructure.md) | Repository layout and ownership boundaries |
| [Tech Stack](TechStack.md) | Frameworks, libraries, infrastructure, testing tools |
| [Future Scope](FutureScope.md) | Roadmap and planned product expansion |
| [Commercial Applications](CommercialApplications.md) | Business use cases, market segments, monetization paths |
| [Screenshots Placeholder](Screenshots.md) | Planned screenshot inventory and capture guidance |

## Maintainer Notes

- Keep docs aligned with the implemented codebase.
- Update endpoint tables when routers change.
- Update database documentation when Alembic migrations are added.
- Update deployment documentation when runtime configuration changes.
- Do not place secrets or real user data in documentation examples.
