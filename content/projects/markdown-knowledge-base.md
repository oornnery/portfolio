---
title: "Markdown Knowledge Base"
slug: "markdown-knowledge-base"
description: >-
  A content-driven site architecture using markdown frontmatter and
  component-based rendering.
thumbnail: "/static/images/projects/markdown-knowledge-base.svg"
tags: ["markdown", "jinja", "content"]
tech_stack: ["Python", "Jinja2", "Jx", "YAML"]
github_url: "https://github.com/oornnery/markdown-knowledge-base"
live_url: ""
date: 2024-12-21
featured: false
---

## Overview

This project focuses on content pipelines for static-like pages served from a
dynamic backend.
Markdown files are parsed, transformed to HTML, and injected into reusable page
components.

## Features

- YAML frontmatter support
- Render caching for content loading
- SEO metadata per page and per project
- Reusable page shells with component imports

## Outcome

The final result is simple to maintain for developers and editors.
Content updates do not require touching route code.
