# Idea2Blueprint backend — agentic core

A LangGraph pipeline that turns a 6-question product brief into a scoped MVP spec, using
four OpenAI-backed agents:

- **Product** — problem/user framing, feature scoping (must/should/won't), product risks.
- **UX** — user stories and user flows, grounded in the Product agent's scoped features.
- **Technical** — tech stack choice, informed by the brief's budget/comfort answers.
- **Spec Generator / Reviewer** — checks the three outputs for consistency (e.g. does the
  stack match the stated budget/comfort? do flows reference in-scope features?), can send
  work back to Product/UX/Technical for a bounded revision, then assembles the final spec.

This pass implements only the agentic core (the LangGraph graph + a CLI to run it locally).
No HTTP API, database, or frontend wiring yet — see `../frontend` for the Next.js prototype
this will eventually feed.

## Setup

```bash
cd backend
uv sync --extra dev
cp .env.example .env   # then fill in OPENAI_API_KEY
```

## Run

```bash
uv run blueprint-agents --template saas
uv run blueprint-agents --template saas --verbose   # prints reviewer trace + revision rounds
uv run blueprint-agents --brief path/to/brief.json
```

Requires a real `OPENAI_API_KEY` in `.env`. Without one, use the test suite below instead.

## Test

```bash
uv run pytest
```

The full suite runs without any API key — the graph's structure, routing logic, and
assembly step are tested directly, and the end-to-end wiring (fan-out/fan-in, a forced
revision loop) is exercised against a stub chat model instead of OpenAI.

## Output shape

The graph returns a `Spec` (`{"sections": [...]}`) with exactly 6 `Section` objects, field-
for-field compatible with `Section`/`SectionGroup`/`SectionItem` in
`../frontend/lib/types.ts`, so `spec.sections` can eventually be dropped straight into the
frontend's data model.
