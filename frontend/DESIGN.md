# Design system

Register: **product** (the UI serves the task; earned familiarity over novelty).
Framed with UI/UX Pro Max ("Data-Dense Dashboard" style) and refined in
Impeccable product mode. Optional Taste pass at the end.

## Style direction

Data-Dense Dashboard: KPI/metric surfaces, tables, panels; space-efficient grids;
maximum data visibility; light and dark, WCAG AA. Calm and trustworthy - this is a
decision-support tool, so the interface disappears into the task.

## Color (OKLCH tokens in `src/app/globals.css`)

Strategy: **Restrained** - faintly teal-tinted neutrals + one deep-teal brand accent (matched to the Alfred AI mark).

- `--primary` deep teal: primary actions, selection, focus ring. White foreground (teal kept dark enough for WCAG AA).
- `--highlight` amber: reserved for sparse attention states only (<=10% of surface), never decoration.
- Neutrals tinted ~0.01 chroma toward the brand hue (264). `--card` is pure white to layer above the tinted `--background`.
- `--muted-foreground` is darkened from the shadcn default to clear 4.5:1 on light.
- `--destructive` for errors. Status hues live in the status badge dots only.

## Typography

- **Fira Sans** - all UI text, labels, headings, body. Fixed rem scale (product UIs view at consistent DPI; no fluid clamp headings).
- **Fira Code (mono)** - numerics, tabular data, IDs. A restrained "analytical" signal, not mono everywhere. Pair `font-mono` with `tabular-nums` for figures.
- **Space Grotesk** - brand/logo face, used only for the "Alfred AI" wordmark next to the tree mark.

## Components & states

- shadcn/ui (base-ui) primitives. Every interactive element: default / hover / focus / active / disabled, plus loading and error where relevant.
- Loading = **skeletons**, not mid-content spinners.
- Empty states **teach** the flow (interview -> score -> recommend), never "nothing here".
- Status badge: uniform pill chrome + a single colored dot per lifecycle stage (DRAFT, INTERVIEW_ACTIVE, STRUCTURED, SCORING, RECOMMENDED, REVIEW). Color lives only in the dot, so it reads cohesive, not rainbow.

## Motion

- 150-250 ms on state transitions (hover, focus, filters). Conveys state, never decoration.
- No orchestrated page-load sequences. Respect `prefers-reduced-motion`.

## Checklist (per surface)

- [ ] Text contrast >= 4.5:1 (light and dark)
- [ ] Visible focus states for keyboard nav
- [ ] `cursor-pointer` on clickable elements; smooth hover transitions
- [ ] Responsive at 375 / 768 / 1024 / 1440
- [ ] SVG icons (Lucide), never emoji
- [ ] `prefers-reduced-motion` honored
