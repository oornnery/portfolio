# Figma Tokens and Handoff

This file maps current implementation tokens to a Figma-ready structure.

## Token Source Files

- `app/static/css/tokens.css`
- `app/static/css/style.css`
- `tailwind.config.cjs`

## Suggested Figma Variable Collections

1. `Color / Semantic`
2. `Color / Legacy-Extended`
3. `Typography`
4. `Spacing`
5. `Radius`
6. `Shadow`
7. `Motion`
8. `Layout`

## Color Mapping (Semantic, from `tokens.css`)

### Dark Theme (default)

| Token       | Value                       |
| ----------- | --------------------------- |
| `bg`        | `#0b0b0d`                   |
| `surface`   | `#121215`                   |
| `surface-2` | `#1a1a1f`                   |
| `text`      | `#ededed`                   |
| `text-2`    | `#a1a1aa`                   |
| `text-3`    | `#6b7280`                   |
| `border`    | `#1f1f26`                   |
| `accent`    | `#7c7cff`                   |
| `accent-2`  | `#22c55e`                   |
| `warn`      | `#f59e0b`                   |
| `danger`    | `#ef4444`                   |
| `focus`     | `rgba(124, 124, 255, 0.38)` |

### Light Theme

| Token       | Value                     |
| ----------- | ------------------------- |
| `bg`        | `#fafafa`                 |
| `surface`   | `#ffffff`                 |
| `surface-2` | `#f4f4f5`                 |
| `text`      | `#0f172a`                 |
| `text-2`    | `#334155`                 |
| `text-3`    | `#64748b`                 |
| `border`    | `#e5e7eb`                 |
| `accent`    | `#4f46e5`                 |
| `accent-2`  | `#16a34a`                 |
| `warn`      | `#d97706`                 |
| `danger`    | `#dc2626`                 |
| `focus`     | `rgba(79, 70, 229, 0.25)` |

## Extended Palette (from `style.css` and Tailwind)

| Token              | Value     | Current usage      |
| ------------------ | --------- | ------------------ |
| `bg-primary`       | `#0a0a0a` | Page background    |
| `bg-secondary`     | `#111111` | Surface backdrop   |
| `bg-tertiary`      | `#1a1a1a` | Secondary sections |
| `surface`          | `#1e1e1e` | Cards and panels   |
| `text-primary`     | `#fafafa` | Primary text       |
| `text-secondary`   | `#a1a1aa` | Secondary text     |
| `text-muted`       | `#71717a` | Muted captions     |
| `accent-primary`   | `#64ffda` | Highlight accents  |
| `accent-secondary` | `#7c3aed` | CTA/brand accent   |
| `accent-glow`      | `#a78bfa` | Accent hover/glow  |
| `border`           | `#27272a` | Border default     |
| `border-hover`     | `#3f3f46` | Border hover       |

## Typography Tokens

| Token       | Value                                  |
| ----------- | -------------------------------------- |
| `font-sans` | `Inter, system-ui, ...`                |
| `font-mono` | `JetBrains Mono, Fira Code, monospace` |

## Spacing Tokens

| Token     | Value  |
| --------- | ------ |
| `space-1` | `8px`  |
| `space-2` | `16px` |
| `space-3` | `24px` |
| `space-4` | `32px` |
| `space-5` | `48px` |
| `space-6` | `64px` |

## Radius Tokens

| Token         | Value                                         |
| ------------- | --------------------------------------------- |
| `radius-sm`   | `10px` (semantic) / `0.375rem` (legacy layer) |
| `radius-md`   | `14px` (semantic) / `0.5rem` (legacy layer)   |
| `radius-lg`   | `18px` (semantic) / `0.75rem` (legacy layer)  |
| `radius-pill` | `999px`                                       |

## Shadow Tokens

| Token       | Value                                    |
| ----------- | ---------------------------------------- |
| `shadow-sm` | `0 6px 16px rgba(0, 0, 0, 0.18)`         |
| `shadow-md` | `0 10px 30px rgba(0, 0, 0, 0.22)`        |
| `shadow`    | `rgba(0, 0, 0, 0.3)` (legacy raw)        |
| `glow`      | `rgba(100, 255, 218, 0.15)` (legacy raw) |

## Motion Tokens

| Token      | Value                            |
| ---------- | -------------------------------- |
| `ease-out` | `cubic-bezier(0.2, 0.8, 0.2, 1)` |
| `dur-1`    | `120ms`                          |
| `dur-2`    | `180ms`                          |
| `dur-3`    | `240ms`                          |

## Layout Tokens

| Token                      | Value    |
| -------------------------- | -------- |
| `container-max`            | `1120px` |
| `container-pad`            | `24px`   |
| `nav-height`               | `64px`   |
| `container-width` (legacy) | `896px`  |
| `header-height` (legacy)   | `64px`   |

## Figma Component Set Mapping

| Figma component    | Implementation path                  |
| ------------------ | ------------------------------------ |
| `Button`           | `app/components/ui/button.jinja`     |
| `Input / Textarea` | `app/components/ui/input.jinja`      |
| `Card`             | `app/components/ui/card.jinja`       |
| `Tag`              | `app/components/ui/tag.jinja`        |
| `Alert`            | `app/components/ui/alert.jinja`      |
| `Navbar`           | `app/components/ui/navbar.jinja`     |
| `Footer`           | `app/components/ui/footer.jinja`     |
| `Breadcrumb`       | `app/components/ui/breadcrumb.jinja` |

## Handoff Checklist

- Create color variables for dark and light modes.
- Create text styles for body, heading, muted, label, and code.
- Create component variants matching Jinja props.
- Bind interactive states: default, hover, focus, disabled, loading.
- Add motion specs from `motion.css` for transitions and enter animations.
- Keep semantic and legacy token groups separate until full token unification.
