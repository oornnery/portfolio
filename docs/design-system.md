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

Core UI components in `app/templates/ui`:

- `button.jinja` (variants: default, primary, secondary, ghost, link,
  accent, danger, outline)
- `input.jinja` (text/textarea, size and variant support)
- `card.jinja` (default, elevated, outlined, ghost, glass, gradient)
- `tag.jinja` (status and accent variants)
- `alert.jinja`, `navbar.jinja`, `footer.jinja`, `breadcrumb.jinja`
- `icon.jinja`, `section-link.jinja`, `social-links.jinja`

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

There are two active token layers:

1. Semantic tokens in `tokens.css` (`--bg`, `--surface`, `--accent`, etc.)
2. Additional palette in `style.css` (`--bg-primary`, `--accent-primary`, etc.)

This works today, but long-term maintenance is easier
if all components converge to one semantic token source.

For detailed handoff values, see [Figma Tokens and Handoff](figma-tokens.md).
