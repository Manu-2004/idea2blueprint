# Idea2Blueprint

Turn a plain-language product idea into a scoped MVP spec. Describe the idea, answer six
questions, and get back a problem statement, feature cuts, user stories, flows, tech stack,
and risks — exportable as PDF or Markdown.

## How it works

Four AI agents collaborate to produce the spec:

- **Product** — frames the problem/users, scopes features (must/should/won't), flags risks.
- **UX** — writes user stories and flows based on the scoped features.
- **Technical** — picks a tech stack based on budget and technical comfort.
- **Spec Generator / Reviewer** — checks the three outputs for consistency, can send work
  back for revision, then assembles the final spec.

## Structure

```
backend/    LangGraph agent pipeline (Python) — the agentic core
frontend/   Next.js app (TypeScript) — the UI
```

Each has its own README with setup and run instructions.

## Deployment

- **Frontend** — deployed on [Vercel](https://vercel.com).
- **Backend** — deployed on [Render](https://render.com).
