# Idea2Blueprint

Turn a plain-language product idea into a scoped MVP spec. Describe the idea, answer six
questions, and get back a problem statement, feature cuts, user stories, flows, tech stack,
and risks — exportable as PDF or Markdown.

## How it works

1. The user fills out a six-question form in the **frontend** describing their product idea
   (problem, users, budget, technical comfort, etc.).
2. The frontend sends that brief to the **backend** API, which kicks off a LangGraph pipeline
   of four AI agents:
   - **Product** — frames the problem/users, scopes features (must/should/won't), flags risks.
   - **UX** — writes user stories and flows based on the scoped features.
   - **Technical** — picks a tech stack based on budget and technical comfort.
   - **Spec Generator / Reviewer** — checks the three outputs for consistency, can send work
     back to Product/UX/Technical for a bounded revision, then assembles the final spec.
3. The backend streams job status back; once done, the frontend renders the finished spec,
   which the user can export as PDF or Markdown.

## Structure

```
backend/    FastAPI + LangGraph agent pipeline (Python) — the agentic core and API
frontend/   Next.js app (TypeScript) — the UI, talks to the backend over HTTP
```

Each has its own README with more detail.

## Running it locally

You need both the backend (API) and frontend (UI) running at the same time.

### 1. Backend

```bash
cd backend
uv sync --extra dev --extra api
cp .env.example .env   # fill in OPENAI_API_KEY
uv run blueprint-agents-api
```

This starts the API on `http://localhost:8000`.

### 2. Frontend

In a separate terminal:

```bash
cd frontend
npm install
npm run dev
```

This starts the UI on `http://localhost:3000`, which talks to the backend at
`http://localhost:8000` by default (override with `NEXT_PUBLIC_API_BASE_URL` in a
`frontend/.env.local` if needed).

Open [http://localhost:3000](http://localhost:3000) and you're good to go.

## Deployment

- **Frontend** — deployed on [Vercel](https://vercel.com).
- **Backend** — deployed on [Render](https://render.com).
