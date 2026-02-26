# ADR 0003: Typed Page Context Contracts for Rendering

- Status: Accepted
- Date: 2026-02-26

## Context

Page rendering previously used loose `dict[str, Any]` contexts. This made
template wiring flexible but increased coupling and reduced confidence during
refactors.

## Decision

- Define explicit page context models (`HomePageContext`,
  `AboutPageContext`, `ProjectsListPageContext`, `ProjectDetailPageContext`,
  `ContactPageContext`).
- Keep `PageRenderData` as the transport object between use-cases and the
  rendering layer.
- Convert typed context models to template kwargs in one place (`render_page`).

## Consequences

- Stronger boundaries between use-cases and templates.
- Better static guarantees and easier review of required page data.
- Slightly more boilerplate when adding new pages, but with better
  maintainability.
