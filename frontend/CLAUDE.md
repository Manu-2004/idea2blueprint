@AGENTS.md

# Idea2Blueprint frontend

Next.js 16 (App Router) + React 19 + TypeScript app. Turns a plain-language product idea
into a scoped MVP spec via a six-question form. Currently a fully client-side prototype —
no backend, no API routes, no auth: everything is mocked in `lib/data.ts` and driven by
local component state.

## Commands

- `npm run dev` — dev server (Turbopack)
- `npm run build` — production build
- `npm run lint` — lint

No test suite exists yet.

## Architecture

- `app/page.tsx` is a single client component (`"use client"`) holding one `screen` state
  value (`Screen` type in `lib/types.ts`: `landing | auth | dashboard | templates | new |
  generating | spec`). All navigation is `setScreen`/`go()` calls, not routing — there are
  no nested routes or `app/**/page.tsx` segments per screen.
- Each screen is one component in `components/` (`Landing`, `AuthScreen`, `Dashboard`,
  `Templates`, `NewSpecForm`, `Generating`, `SpecView`, `ExportDialog`). Screens are dumb:
  they take state and callbacks as props from `page.tsx` and hold no navigation logic
  themselves.
- `AppShell` wraps the authenticated screens (dashboard/templates/new/generating/spec)
  with the sidebar nav; `Landing` and `AuthScreen` render outside it.
- The "generate spec" step (`Generating` → `spec`) is a fake `setInterval` timer stepping
  through `GEN_LABELS`, not a real async call.
- `lib/data.ts` holds all static content: form templates, question copy, the sample spec's
  section content, and dashboard spec list. `lib/types.ts` holds the shared types. Extend
  these rather than inlining new mock data in components.

## Conventions

- Imports are relative (`../lib/types`), never the `@/*` tsconfig path alias — stay
  consistent with existing files even though the alias is configured.
- Styling is the "Nocturne" design system in `app/globals.css`: CSS custom properties
  (`--color-*`, `--space-*`, `--radius-*`, `--shadow-*`) plus utility classes (`.btn`,
  `.card`, `.tag`, `.input`, `.dialog`, etc.). Components mix these classes with inline
  `style={{ ... }}` for one-off layout — that split is intentional in this codebase, not
  something to "clean up" into all-classes or all-inline.
- Accent color is a red hue rotated in OKLCH from the original Nocturne palette — don't
  hardcode hex colors; use the existing `var(--color-*)` tokens.
- `tsconfig.json` has `strict: true` — keep new code strict-clean.
