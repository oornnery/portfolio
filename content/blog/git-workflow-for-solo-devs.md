---
title: "Git Workflow for Solo Devs"
slug: "git-workflow-for-solo-devs"
description: "A lightweight but disciplined Git workflow that keeps solo projects clean and deployable."
date: "2025-07-01"
author: "Fabio Souza"
tags:
  - "git"
  - "devx"
featured: false
discussion_url: "https://github.com/oornnery/proj/portfolio/discussions"
---

Working alone removes the pressure to follow a team workflow, but discipline
matters more when there is no code review to catch mistakes.

## Keep main always deployable

Never commit broken or half-finished code to main. Use short-lived feature
branches even when working alone.

## Commit by concern, not by time

A good commit encapsulates one logical change. A bad commit bundles three
unrelated fixes because "I was working on that file anyway." Atomic commits
make `git bisect` and `git log` actually useful.

## Write commit messages that explain why

```text
fix: prevent CSRF token reuse after form submission

Tokens were being accepted twice in high-latency requests. Added a
one-time-use check in the validation layer.
```

The "what" is in the diff. The "why" belongs in the message.

## Use tags for releases

A `git tag v1.2.0` with a semantic version at each deploy creates a permanent
reference. When a bug is reported "after the last update," you know exactly
where to look.

## Rebase before merging into main

`git rebase main` keeps the history linear. Merge commits add noise when you
are the only contributor.
