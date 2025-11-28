---
description: Master plan for Portfolio refactoring project
---

# Portfolio Refactor Plan

## Overview
Refactoring of the portfolio project to a minimalist stack using **FastAPI**, **Jinja2**, and **HTMX**.

**Last Updated:** 2025-11-28

---

## 🚀 Quick Start - Development Commands

### Python (uv)
```bash
# Install dependencies
uv sync

# Run development server
uv run uvicorn app.main:app --reload

# Linting & Formatting
uv run ruff format . && uv run ruff check . --fix --unsafe-fixes

# Type checking
uv run ty check .
```

### Docker
```bash
# Development
docker compose -f docker/docker-compose.dev.yml up --build

# Production
docker compose -f docker/docker-compose.prod.yml up -d --build
```

---

## 📊 Implementation Phases Overview

| Phase | Status | Description |
|-------|--------|-------------|
| 1 | ✅ COMPLETE | Docker Setup (Chainguard) |
| 2 | ✅ COMPLETE | Backend Setup (FastAPI + SQLModel) |
| 3 | ✅ COMPLETE | Frontend Migration (Jinja2 + HTMX) |
| 4 | 🔄 IN PROGRESS | Blog System (Templates & HTMX) |
| 5 | 🔲 NOT STARTED | Projects System |
| 6 | 🔲 NOT STARTED | Comments & Authentication |
| 7 | 🔲 NOT STARTED | Deploy & CI/CD |

---

## ✅ Progress Tracker

### Phase 1: Docker Setup ✅ COMPLETE
- [x] `docker/Dockerfile.dev`
- [x] `docker/Dockerfile.prod`
- [x] `docker/docker-compose.dev.yml`
- [x] `docker/docker-compose.prod.yml`

### Phase 2: Backend Setup ✅ COMPLETE
- [x] FastAPI app structure (`app/main.py`)
- [x] SQLModel configuration (`app/db.py`)
- [x] Pydantic Settings (`app/config.py`)
- [x] Static files mounting

### Phase 3: Frontend Migration ✅ COMPLETE
- [x] Jinja2 Templates setup (`app/templates/`)
- [x] Base layout (`app/templates/base.html`)
- [x] Home page (`app/templates/pages/home.html`)
- [x] CSS Variables (Space/Night Theme)
- [x] HTMX integration

### Phase 4: Blog System 🔄 IN PROGRESS
- [x] Blog Models (`app/models/blog.py`)
- [x] Blog API (`app/api/blog.py`)
- [x] Blog List Template (`app/templates/blog/list.html`)
- [x] Blog Detail Template (`app/templates/blog/detail.html`)
- [ ] HTMX Search/Filter for Blog
- [ ] Markdown Rendering Improvements

### Phase 5: Projects System 🔲 NOT STARTED
- [x] Project Model (`app/models/project.py`)
- [ ] Projects API (`app/api/projects.py`)
- [ ] Projects List Template
- [ ] Projects Detail Template

### Phase 6: Comments & Auth 🔲 NOT STARTED
- [x] User Model (`app/models/user.py`)
- [x] Comment Model (`app/models/comment.py`)
- [x] Auth API (`app/api/auth.py`)
- [ ] Login/Register Templates
- [ ] Comments UI (HTMX)

---

## 📁 Current Project Structure

```
portfolio/
├── app/
│   ├── api/            # HTMX/JSON Endpoints
│   ├── core/           # Security & Deps
│   ├── models/         # SQLModel Schemas
│   ├── services/       # Business Logic
│   ├── static/         # CSS, JS, Images
│   ├── templates/      # Jinja2 Templates
│   ├── config.py
│   ├── db.py
│   ├── main.py
│   └── views.py        # Page Routes
├── docker/
├── pyproject.toml
└── .github/
```

---

## 🎨 Theme Reference (Space/Night)

```css
:root {
    --bg-primary: #0a0e27;
    --bg-secondary: #141b33;
    --text-primary: #e6e8f0;
    --accent-primary: #64ffda;
    --accent-secondary: #7c3aed;
}
```
