# Frontend

## Rendering Model

The frontend is SSR-first using Jx/Jinja templates.

- No SPA framework
- HTML rendered on server for every route
- Progressive enhancement via small vanilla JS scripts

## Template Organization

| Group    | Path                       | Role                                       |
| -------- | -------------------------- | ------------------------------------------ |
| Layouts  | `app/templates/layouts/*`  | Global shell and page wrappers             |
| Pages    | `app/templates/pages/*`    | Route-level templates                      |
| Features | `app/templates/features/*` | Domain page sections                       |
| UI       | `app/templates/ui/*`       | Reusable components, split into subfolders |

The `ui/` folder is organized into subfolders:

| Subfolder    | Contents                                                                                                                                 |
| ------------ | ---------------------------------------------------------------------------------------------------------------------------------------- |
| `ui/layout/` | `center`, `grid`, `row`, `section`, `stack`                                                                                              |
| `ui/nav/`    | `breadcrumb`, `footer`, `navbar`, `scroll-indicator`                                                                                     |
| `ui/card/`   | `card`, `card-heading`                                                                                                                   |
| `ui/form/`   | `button`, `input`                                                                                                                        |
| `ui/` root   | `alert`, `avatar`, `content-shell`, `empty-state`, `icon`, `meta-info`, `page-header`, `section-link`, `seo-head`, `social-links`, `tag` |

## Jx Catalog

Registered in `app/core/dependencies.py` with prefixes:

- `@ui/*` (recursive — subfolders use full path, e.g. `@ui/form/button.jinja`)
- `@layouts/*`
- `@features/*`
- `@pages/*`

This enables consistent imports and composable templates.

## Page Composition

### Home (`/`)

- Full-screen snap sections
- Profile summary
- Projects preview + latest blog posts preview
- Contact preview

### About (`/about`)

- Breadcrumb-first intro with the shared compact spacing rhythm
- Stronger profile hero with summary lines and CTA row
- Reuses the same right-side `On this page` minimap pattern as blog/project
  detail pages
- Frontmatter is limited to profile metadata; authored content comes from
  markdown sections in `content/about.md`
- Resume-style sections are parsed from markdown `##` / `###` headings with a
  highlighted experience timeline
- Education and certificates render as stacked resume entries with aligned dates
- Skills are grouped by category in lighter stacked groups

### Projects (`/projects`, `/projects/{slug}`)

- Project cards list with breadcrumb-first intro rhythm:
  breadcrumb, `8px-16px` gap, then title/subtitle block
- Detail page with breadcrumb-first header rhythm:
  breadcrumb, `8px-16px` gap, compact metadata row, `16px-24px` gap to title,
  then subtitle/tags/actions
- Detail page reuses the same right-side `On this page` minimap pattern as blog
  detail pages when markdown includes headings

### Blog (`/blog`, `/blog/posts`, `/blog/posts/{slug}`, `/blog/tags`)

- Blog home with breadcrumb-first intro rhythm, featured posts carousel
  (up to 3, prev/next, autoplay)
- Latest posts preview (up to 3) with shortcut to full list
- Tags preview (up to 10) with shortcut to full tags page
- Posts listing page with the same breadcrumb-first intro rhythm
- Post detail page with breadcrumb-first header rhythm:
  breadcrumb, `8px-16px` gap, compact metadata row, `16px-24px` gap to title,
  then subtitle/tags
- Post detail page with reading metadata, improved prose layout, right-side
  `On this page` minimap, and GitHub/Gist discussion CTA
- Tags index and filtered tag pages with the same breadcrumb-first intro rhythm
- RSS feed endpoint at `/blog/feed.xml`

### Contact (`/contact`)

- Breadcrumb-first intro with the shared compact spacing rhythm
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
| Base tokens   | `app/static/css/tokens.css`   | Semantic tokens and palette variants |
| Motion        | `app/static/css/motion.css`   | Animations and interaction utilities |
| System/custom | `app/static/css/style.css`    | App-specific styles and layouts      |

### Color and palette system

Theme is controlled via two `<html>` attributes:

- `data-theme` — `dark` or `light`
- `data-palette` — `default`, `ocean`, `sunset`, `rose`, `forest`, or `mono`

All color tokens use RGB channel variables (`--accent-rgb`, `--warn-rgb`,
`--danger-rgb`, `--accent-2-rgb`) so Tailwind opacity modifiers work:
`bg-accent/10`, `border-accent/20`. Palette overrides in `tokens.css` use
`:root[data-palette="..."]` selectors that come **after** the `data-theme`
block — cascade order is critical.

The Tailwind config maps semantic tokens as
`rgb(var(--accent-rgb) / <alpha-value>)` so all opacity variants are available.
Do not use plain `var(--accent)` in `tailwind.config.cjs` for colors that need
opacity modifiers — it breaks Tailwind's alpha injection.

## Responsive Strategy

- Mobile menu below `md`
- Containerized content widths
- Scroll-snap tuned for desktop and softened on mobile
- Small-screen fallback disables hard snap for short viewports
- Shared navbar now exposes `Home`, `About`, `Projects`, `Blog`, and `Contact`
