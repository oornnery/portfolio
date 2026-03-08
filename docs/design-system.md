# Design System

## Design Direction

The UI follows a dark, developer-portfolio visual language:

- High-contrast typography
- Neutral surfaces with accent highlights
- Compact cards and rounded controls
- Motion feedback for navigation and section transitions

## Design Foundations

Foundations are split across:

- `app/static/css/tokens.css` (semantic tokens + theme variants)
- `tailwind.config.cjs` (utility palette and type families)
- `app/static/css/style.css` (component and layout styling)
- `app/static/css/motion.css` (animation utilities)

## Component Inventory

Core UI components in `app/templates/ui`, organized by subfolder:

**`ui/form/`**

- `button.jinja` — variants: default, primary, secondary, ghost, link,
  accent, danger, outline
- `input.jinja` — text/textarea, size and variant support; error and hint slots

**`ui/card/`**

- `card.jinja` — variants: default, elevated, outlined, ghost, glass, gradient;
  idle border uses `border-accent/20`, hover `border-accent/40`
- `card-heading.jinja` — title, date, featured badge

**`ui/nav/`**

- `navbar.jinja` — top navigation with theme/palette switcher
  (checkmark on active palette)
- `footer.jinja`, `breadcrumb.jinja`, `scroll-indicator.jinja`

**`ui/layout/`**

- `row.jinja`, `stack.jinja`, `grid.jinja`, `center.jinja`, `section.jinja`

**`ui/` root atoms**

- `tag.jinja` — variants: default, outline, accent, secondary, success, warning,
  danger; hover applies `hover:bg-surface-2/80` on all variants
- `alert.jinja`, `avatar.jinja`, `icon.jinja`, `section-link.jinja`,
  `social-links.jinja`
- `content-shell.jinja`, `empty-state.jinja`, `meta-info.jinja`,
  `page-header.jinja`, `seo-head.jinja`

## Page Design Patterns

- Home uses full-screen snap sections and guided scroll indicator.
- Public pages share a centered container with fixed top navigation.
- Public list/index pages use a shared intro rhythm:
  breadcrumb first, `8px-16px` gap, then title/subtitle.
- Contact page uses two-column layout on medium+ breakpoints.
- Detail pages use a shared header rhythm:
  breadcrumb first, `8px-16px` gap to metadata, `16px-24px` gap to title,
  then subtitle/tags/actions.
- Blog and project detail pages use the same right-side `On this page` minimap
  when rendered markdown includes headings.
- About uses the same minimap shell, but with authored section headings instead
  of markdown-generated headings.
- Project detail uses prose block plus metadata chips/actions.
- About combines a compact profile hero, highlighted timeline cards for
  experience, stacked resume entries for education/certificates, and grouped
  skill chips.

## Motion Principles

From `motion.css`:

- Entrance animations (`fade-up`, `fade-in`, `slide-in-*`, `scale-in`)
- Hover effects (`hover-lift`, `hover-scale`, `hover-glow`)
- Loading states (`pulse`, `bounce`, `spin`)
- Tokenized timing (`--dur-*`) and easing (`--ease-out`)

## Responsive Principles

- Navigation collapses to toggle menu on mobile.
- Home snap behavior adapts by viewport size and height.
- Containers and spacing scale down at mobile breakpoints.

## Notes on Token Consistency

`tokens.css` is the single source of truth for semantic tokens (`--bg`, `--surface`,
`--accent`, `--border`, `--radius-*`). All colors expose RGB channel variants
(`--accent-rgb`, `--warn-rgb`, `--danger-rgb`, `--accent-2-rgb`) so Tailwind opacity
modifiers (`bg-accent/10`, `border-accent/20`) work correctly. `tailwind.config.cjs`
maps these as `rgb(var(--accent-rgb) / <alpha-value>)` — never use plain `var(--accent)`
for colors that need opacity modifiers.

### Palette system

Six palettes: `default`, `ocean`, `sunset`, `rose`, `forest`, `mono`. Active
palette is stored in `localStorage` and applied as `data-palette` on `<html>`.
Palette overrides in `tokens.css` use `:root[data-palette="..."]` blocks that
must come **after** the `data-theme` block in the cascade.

All visual accent uses (borders, timeline dots, featured badges, minimap dots)
must reference `--accent-rgb` or `--accent`. Use `--interactive` only for text
link hover colors.

For detailed handoff values, see [Figma Tokens and Handoff](figma-tokens.md).
