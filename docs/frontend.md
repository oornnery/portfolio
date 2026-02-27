# Frontend

## Rendering Model

The frontend is SSR-first using Jx/Jinja templates.

- No SPA framework
- HTML rendered on server for every route
- Progressive enhancement via small vanilla JS scripts

## Template Organization

| Group    | Path                        | Role                                            |
| -------- | --------------------------- | ----------------------------------------------- |
| Layouts  | `app/components/layouts/*`  | Global shell and page wrappers                  |
| Pages    | `app/components/pages/*`    | Route-level templates                           |
| Features | `app/components/features/*` | Domain page sections                            |
| UI       | `app/components/ui/*`       | Reusable components (button, input, card, etc.) |

## Jx Catalog

Registered in `app/core/dependencies.py` with prefixes:

- `@ui/*`
- `@layouts/*`
- `@features/*`
- `@pages/*`

This enables consistent imports and composable templates.

## Page Composition

### Home (`/`)

- Full-screen snap sections
- Profile summary
- Projects preview
- Contact preview

### About (`/about`)

- Resume-style sections from frontmatter
- Work experience, education, certificates, skills

### Projects (`/projects`, `/projects/{slug}`)

- Project cards list
- Detail page with tags and action buttons

### Contact (`/contact`)

- Social links
- Contact form with inline validation messages

## JavaScript Behavior

| File                         | Responsibility                                 |
| ---------------------------- | ---------------------------------------------- |
| `app/static/js/main.js`      | Mobile menu, year update, scroll snap behavior |
| `app/static/js/analytics.js` | Event queue, batching, beacon/fetch delivery   |

Analytics JS tracks:

- page view
- click events (`data-analytics-event`)
- section visibility (`data-analytics-section`)

## Styling Stack

| Layer         | File                          | Notes                                |
| ------------- | ----------------------------- | ------------------------------------ |
| Utility CSS   | `app/static/css/tailwind.css` | Generated from Tailwind config       |
| Base tokens   | `app/static/css/tokens.css`   | Semantic tokens and theme variants   |
| Motion        | `app/static/css/motion.css`   | Animations and interaction utilities |
| System/custom | `app/static/css/style.css`    | App-specific styles and layouts      |

## Responsive Strategy

- Mobile menu below `md`
- Containerized content widths
- Scroll-snap tuned for desktop and softened on mobile
- Small-screen fallback disables hard snap for short viewports
