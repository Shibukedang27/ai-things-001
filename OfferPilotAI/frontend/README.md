# OfferPilot AI Frontend

Modern React client for OfferPilot AI authentication, candidate analytics, live coding practice, resume analysis, performance intelligence, and the public SaaS landing page.

## Stack

- Vite
- React
- TypeScript
- Recharts
- CodeMirror
- Lucide React

## Commands

```bash
npm install
npm run dev
npm run build
```

## Product Scope

The app opens with a secure login, signup, and forgot-password flow. Successful authentication stores the backend-issued access and refresh tokens before opening the dashboard.

The landing page includes the OfferPilot AI hero, features, workflow, testimonials, supported company segments, Free/Pro/Enterprise pricing, FAQ, footer, dark mode support, and startup-quality branding.

The dashboard currently includes average score, highest score, interview count, weak and strong topics, recent interviews, daily streak, performance charts, learning progress, leaderboard, dark mode, responsive layouts, animations, and loading screens.

The analytics workspace includes topic-wise accuracy, weekly progress, monthly progress, heat maps, radar charts, weakness trends, strength trends, interview history, and performance graphs. API calls use `/api/v1/analytics/*`.

The live coding workspace includes a CodeMirror editor, Python/Java/SQL templates, run/analyze/submit actions, terminal output, complexity panels, bug findings, optimized code, and submission history. API calls use `/api/v1/live-coding/*`.

The resume analyzer workspace includes PDF upload, job-description comparison, ATS score, analyzed skills, missing skills, resume suggestions, resume-based interview questions, and a skill gap report. API calls use `/api/v1/resume-analyzer/*`.

The Vite dev server proxies `/api` to `http://localhost:8000`.
