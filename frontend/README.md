# Idea2Blueprint

Turn a plain-language product idea into a scoped MVP spec: describe the idea, answer six questions, and get back a problem statement, feature cuts, user stories, flows, tech stack and risks — exportable as PDF or Markdown.

Built with [Next.js](https://nextjs.org) (App Router) and TypeScript, styled with the Nocturne design system.

## Getting started

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Scripts

- `npm run dev` — start the dev server (Turbopack)
- `npm run build` — production build
- `npm run start` — run the production build
- `npm run lint` — lint the project

## Project structure

```
app/            Root layout, global styles, and the page-level state machine
components/     One component per screen (Landing, AuthScreen, Dashboard, Templates,
                NewSpecForm, Generating, SpecView, ExportDialog) plus shared icons
lib/            Static data (templates, questions, sample spec sections) and types
public/         Static assets
```

The app is a single client-side state machine (`app/page.tsx`) that switches between
screens — landing, auth, dashboard, templates, new-spec form, generating, and the
finished spec — all driven from one `screen` state value, mirroring the original
design's component structure.
