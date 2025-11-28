---
description: Master plan for Portfolio refactoring project
---

# Portfolio Refactor Plan

## Overview
Complete refactoring of the portfolio project with Docker setup, Ant Design migration, page restructuring, and blog implementation.

**Last Updated:** 2025-11-26

---

## 🚀 Quick Start - Development Commands

### Backend (Python + uv)
```bash
cd backend

# Install dependencies
uv sync

# Run development server
uv run uvicorn app.main:app --reload

# Linting & Formatting (run before commits)
uv run ruff format . && uv run ruff check . --fix --unsafe-fixes

# Type checking
uv run ty check .

# Add new dependency
uv add <package>
```

### Frontend (TypeScript + bun)
```bash
cd frontend

# Install dependencies
bun install

# Run development server
bun run dev

# Linting & Formatting (run before commits)
bunx biome check --write --unsafe .
bunx tsc --noEmit

# Build for production
bun run build
```

### Docker
```bash
# Development (full stack)
docker compose -f docker-compose.dev.yml up --build

# Production (full stack)
docker compose -f docker-compose.prod.yml up -d --build
```

---

## 📊 Implementation Phases Overview

| Phase | File | Status | Description |
|-------|------|--------|-------------|
| 1 | [fase1-docker-setup.prompt.md](./fase1-docker-setup.prompt.md) | ✅ COMPLETE | Docker Setup (Chainguard) |
| 2 | [fase2-page-restructuring.prompt.md](./fase2-page-restructuring.prompt.md) | 🔄 IN PROGRESS | Page Restructuring & Routing |
| 3 | [fase3-home-page.prompt.md](./fase3-home-page.prompt.md) | 🔄 IN PROGRESS | Home Page Components |
| 4 | [fase4-projects-page.prompt.md](./fase4-projects-page.prompt.md) | 🔲 NOT STARTED | Projects System |
| 5 | [fase5-blog-system.prompt.md](./fase5-blog-system.prompt.md) | 🔄 IN PROGRESS | Blog System |
| 6 | [fase6-comments-auth.prompt.md](./fase6-comments-auth.prompt.md) | 🔲 NOT STARTED | Comments & Authentication |
| 7 | [fase7-security-performance.prompt.md](./fase7-security-performance.prompt.md) | 🔄 IN PROGRESS | Security & Performance |
| 8 | [fase8-deploy-cicd.prompt.md](./fase8-deploy-cicd.prompt.md) | 🔲 NOT STARTED | Deploy & CI/CD |
| 9 | [fase9-polish-extras.prompt.md](./fase9-polish-extras.prompt.md) | 🔲 NOT STARTED | Polish & Extras |

---

## ✅ Progress Tracker (Detailed)

### Phase 1: Docker Setup (Dev & Prod) ✅ COMPLETE
> See: [fase1-docker-setup.prompt.md](./fase1-docker-setup.prompt.md)
- [x] `backend/docker/Dockerfile` - Chainguard Python (zero CVE)
- [x] `backend/docker/docker-compose.yml`
- [x] `backend/docker/docker-compose.dev.yml`
- [x] `backend/docker/docker-compose.prod.yml`
- [x] `frontend/docker/Dockerfile` - Chainguard Node + Nginx
- [x] `frontend/docker/docker-compose.yml`
- [x] `frontend/docker/docker-compose.dev.yml`
- [x] `frontend/docker/docker-compose.prod.yml`
- [x] `frontend/docker/nginx.chainguard.conf`
- [x] Root `docker-compose.dev.yml`
- [x] Root `docker-compose.prod.yml`

### Phase 2: Ant Design Migration ✅ COMPLETE
- [x] Remove Chakra UI dependencies
- [x] Install Ant Design v6 + @ant-design/icons
- [x] Update `src/theme.ts` with Tokyo Night tokens
- [x] Update `src/main.tsx` with ConfigProvider
- [x] Migrate components to Ant Design
- [x] Add Framer Motion for animations
- [x] Switch from npm to bun

### Phase 3: Page Restructuring 🔄 IN PROGRESS
> See: [fase2-page-restructuring.prompt.md](./fase2-page-restructuring.prompt.md)
- [x] React Router setup
- [x] Create route structure (`pages/index.ts`)
- [x] `pages/Home.tsx` - Landing page
- [x] `pages/Status.tsx` - Status page
- [x] `pages/Blog.tsx` - Blog listing
- [x] `pages/BlogPost.tsx` - Blog post detail
- [ ] Layout component with responsive Navbar/Footer
- [ ] About page (`/about`)
- [ ] Projects page (`/projects`)
- [ ] Contact page (`/contact`)
- [ ] 404 page customizada

### Phase 4: Home Page (Portfolio Landing) 🔄 IN PROGRESS
> See: [fase3-home-page.prompt.md](./fase3-home-page.prompt.md)
- [x] `components/home/Hero.tsx` - Hero section
- [x] `components/home/About.tsx` - About section
- [x] `components/home/Experience.tsx` - Experience timeline
- [x] `components/home/Contact.tsx` - Contact section
- [ ] Typing animation effect
- [ ] Skills grid with progress bars
- [ ] Education section
- [ ] Fun facts carousel
- [ ] Scroll reveal animations
- [ ] Download CV button
- [ ] GitHub stats integration

### Phase 5: Blog Backend ✅ COMPLETE
> See: [fase5-blog-system.prompt.md](./fase5-blog-system.prompt.md)
- [x] `backend/app/models/blog.py` - SQLModel schemas with proper validation
- [x] `backend/app/api/blog.py` - Full CRUD + reactions + categories/tags
- [x] Rate limiting on all endpoints (slowapi)
- [x] Comprehensive OpenAPI documentation
- [x] Input validation with Pydantic
- [ ] `backend/app/services/markdown_service.py` - Markdown utilities

### Phase 6: Security & Middleware ✅ COMPLETE
> See: [fase7-security-performance.prompt.md](./fase7-security-performance.prompt.md)
- [x] CORS configured (localhost:5173, 5174, 3000)
- [x] TrustedHostMiddleware
- [x] SecurityHeadersMiddleware (custom)
- [x] RequestLoggingMiddleware
- [x] Rate limiting (slowapi): 100/min global, 60/min read, 10/min write, 30/min reactions
- [ ] CSRF protection for forms
- [ ] Input sanitization (bleach)
- [ ] Content Security Policy header

### Phase 7: Blog Frontend 🔄 IN PROGRESS
> See: [fase5-blog-system.prompt.md](./fase5-blog-system.prompt.md)
- [x] `components/blog/PostCard.tsx` - Post card component
- [x] `components/blog/CodeBlock.tsx` - Syntax highlighting
- [x] `components/blog/Callout.tsx` - Callout components
- [x] `components/blog/ReadingProgress.tsx` - Progress bar
- [ ] Post listing with filters and search
- [ ] Table of contents (auto-generated)
- [ ] Share buttons (social)
- [ ] Reactions UI component
- [ ] Related posts section
- [ ] Comments (Giscus or custom)

### Phase 8: Projects System 🔲 NOT STARTED
> See: [fase4-projects-page.prompt.md](./fase4-projects-page.prompt.md)
- [ ] `backend/app/models/project.py` - Project model
- [ ] `backend/app/api/projects.py` - Projects API
- [ ] `pages/Projects.tsx` - Projects listing
- [ ] `pages/ProjectDetail.tsx` - Project detail
- [ ] `components/projects/ProjectCard.tsx`
- [ ] `components/projects/ProjectFilters.tsx`
- [ ] GitHub API integration (stars/forks)

### Phase 9: Authentication & Comments 🔲 NOT STARTED
> See: [fase6-comments-auth.prompt.md](./fase6-comments-auth.prompt.md)
- [ ] OAuth with GitHub
- [ ] OAuth with Google
- [ ] User model and sessions
- [ ] Comments system
- [ ] Protected routes
- [ ] User dropdown menu

### Phase 10: Deploy & CI/CD 🔲 NOT STARTED
> See: [fase8-deploy-cicd.prompt.md](./fase8-deploy-cicd.prompt.md)
- [ ] GitHub Actions CI workflow
- [ ] GitHub Actions CD workflow
- [ ] Dependabot configuration
- [ ] Alembic migrations
- [ ] Production deployment
- [ ] SSL/HTTPS setup
- [ ] Monitoring (Prometheus/Grafana)

### Phase 11: Polish & Extras 🔲 NOT STARTED
> See: [fase9-polish-extras.prompt.md](./fase9-polish-extras.prompt.md)
- [ ] 404/500 error pages
- [ ] Loading skeletons
- [ ] PWA setup
- [ ] SEO meta tags
- [ ] RSS feed
- [ ] Analytics (Plausible)
- [ ] Easter eggs

---

## 📁 Current Project Structure

```
portfolio/
├── backend/                     # FastAPI + SQLModel + Python 3.14+
│   ├── app/
│   │   ├── api/
│   │   │   └── blog.py         # ✅ Full blog API with rate limiting
│   │   ├── models/
│   │   │   └── blog.py         # ✅ Post, Reaction, Category schemas
│   │   ├── config.py           # Pydantic Settings
│   │   ├── db.py               # Async SQLAlchemy engine
│   │   └── main.py             # ✅ FastAPI app with middleware stack
│   ├── docker/
│   │   ├── Dockerfile          # ✅ Chainguard Python (zero CVE)
│   │   ├── docker-compose.yml
│   │   ├── docker-compose.dev.yml
│   │   └── docker-compose.prod.yml
│   └── pyproject.toml
├── frontend/                    # React 19 + TypeScript + Vite 7 + Ant Design v6
│   ├── src/
│   │   ├── components/
│   │   │   ├── blog/           # ✅ PostCard, CodeBlock, Callout, ReadingProgress
│   │   │   ├── home/           # ✅ Hero, About, Experience, Contact
│   │   │   ├── common/
│   │   │   └── status/
│   │   ├── pages/
│   │   │   ├── Home.tsx        # ✅ Landing page
│   │   │   ├── Blog.tsx        # ✅ Blog listing
│   │   │   ├── BlogPost.tsx    # ✅ Post detail
│   │   │   └── Status.tsx      # ✅ System status
│   │   ├── hooks/
│   │   │   └── useHealthMonitor.ts
│   │   ├── contexts/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── theme.ts            # ✅ Tokyo Night theme config
│   ├── docker/
│   │   ├── Dockerfile          # ✅ Chainguard Node + Nginx
│   │   ├── nginx.chainguard.conf # ✅ Nginx config
│   │   ├── docker-compose.yml
│   │   ├── docker-compose.dev.yml
│   │   └── docker-compose.prod.yml
│   └── package.json
├── docker-compose.dev.yml      # ✅ Full stack dev
├── docker-compose.prod.yml     # ✅ Full stack prod
└── .github/
    ├── copilot-instructions.md # ✅ Project guidelines
    └── prompts/
        ├── plan-portfolioRefactor.prompt.md  # This file
        ├── fase1-docker-setup.prompt.md      # ✅ Complete
        ├── fase2-page-restructuring.prompt.md
        ├── fase3-home-page.prompt.md
        ├── fase4-projects-page.prompt.md
        ├── fase5-blog-system.prompt.md
        ├── fase6-comments-auth.prompt.md
        ├── fase7-security-performance.prompt.md
        ├── fase8-deploy-cicd.prompt.md
        └── fase9-polish-extras.prompt.md
```

---

## 🔧 Code Quality Rules

### Backend (Python)
- **Package Manager:** `uv` (NOT pip)
- **Formatter/Linter:** Ruff
- **Type Checker:** ty (red-knot)
- **SQLModel:** Use `model_config = ConfigDict(json_schema_extra={...})` at class level
- **SQLModel Field:** Do NOT use `json_schema_extra` inside `Field()` calls - it causes errors

```python
# ✅ CORRECT - json_schema_extra at class level
class PostBase(SQLModel):
    model_config = ConfigDict(
        json_schema_extra={"example": {"title": "My Post"}}
    )
    title: str = Field(min_length=1, description="Post title")

# ❌ WRONG - json_schema_extra in Field() causes errors
class PostBase(SQLModel):
    title: str = Field(json_schema_extra={"example": "My Post"})  # ERROR!
```

### Frontend (TypeScript)
- **Package Manager:** `bun` (NOT npm)
- **Formatter/Linter:** Biome
- **Type Checker:** TypeScript (`tsc --noEmit`)
- **UI Framework:** Ant Design v6 with ConfigProvider
- **Animations:** Framer Motion

---

## 🎨 Theme Reference (Tokyo Night)

### Dark Mode
```typescript
{
  colorPrimary: '#7aa2f7',   // Blue accent
  colorBgBase: '#1a1b26',    // Background
  colorBgContainer: '#16161e', // Card background
  colorTextBase: '#c0caf5',  // Primary text
  colorBorder: '#292e42',    // Borders
  colorSuccess: '#9ece6a',   // Green
  colorError: '#f7768e',     // Red/Pink
  colorWarning: '#e0af68',   // Orange
}
```

### Light Mode
```typescript
{
  colorPrimary: '#2e7de9',   // Blue accent
  colorBgBase: '#d5d6db',    // Background
  colorBgContainer: '#e9e9ed', // Card background
  colorTextBase: '#33467c',  // Primary text
  colorBorder: '#9699a3',    // Borders
  colorSuccess: '#2d7a6e',   // Green
  colorError: '#c73866',     // Red/Pink
  colorWarning: '#d59422',   // Orange
}
```

---

## 📡 API Endpoints (Backend)

### Core Endpoints
| Method | Endpoint | Rate Limit | Description |
|--------|----------|------------|-------------|
| GET | `/` | - | Root check |
| GET | `/health` | - | Health status with version |
| GET | `/ping` | - | Simple ping |
| GET | `/version` | - | Version info |
| GET | `/docs` | - | Swagger UI (dev only) |

### Blog API (`/api/blog`)
| Method | Endpoint | Rate Limit | Description |
|--------|----------|------------|-------------|
| GET | `/posts` | 60/min | List posts with filters |
| GET | `/posts/{slug}` | 60/min | Get post by slug (+views) |
| POST | `/posts` | 10/min | Create new post |
| PUT | `/posts/{slug}` | 10/min | Update post |
| DELETE | `/posts/{slug}` | 10/min | Delete post |
| GET | `/posts/{slug}/reactions` | 60/min | Get reactions |
| POST | `/posts/{slug}/react` | 30/min | Add reaction |
| GET | `/categories` | 60/min | List categories with counts |
| GET | `/tags` | 60/min | List tags with counts |
| GET | `/stats` | 30/min | Blog statistics |

---

## 🐳 Docker Setup (Chainguard - Zero CVE)

### Images Used
| Purpose | Image | Security |
|---------|-------|----------|
| Python Dev | `cgr.dev/chainguard/python:latest-dev` | Zero CVE |
| Python Prod | `cgr.dev/chainguard/python:latest` | Zero CVE |
| Node.js Dev | `cgr.dev/chainguard/node:latest-dev` | Zero CVE |
| Nginx Prod | `cgr.dev/chainguard/nginx:latest` | Zero CVE |
| PostgreSQL | `cgr.dev/chainguard/postgres:16` | Zero CVE |

### Port Mappings
| Service | Dev Port | Prod Port | Container Port |
|---------|----------|-----------|----------------|
| Frontend | 127.0.0.1:5173 | 0.0.0.0:80 | 5173/8080 |
| Backend | 127.0.0.1:8000 | 0.0.0.0:8000 | 8000 |
| PostgreSQL | 127.0.0.1:5432 | - | 5432 |

### Docker Commands
```bash
# Development
docker compose -f docker-compose.dev.yml up --build

# Production
docker compose -f docker-compose.prod.yml up -d --build

# Per-service development
cd backend && docker compose -f docker/docker-compose.dev.yml up --build
cd frontend && docker compose -f docker/docker-compose.dev.yml up --build

# Linting
hadolint backend/docker/Dockerfile frontend/docker/Dockerfile
bunx dclint backend/docker/ frontend/docker/ --fix
```

---

## 📋 Next Steps (Priority Order)

1. **[FASE 2]** Complete Layout component with responsive Navbar/Footer
2. **[FASE 3]** Add typing animation and skills grid to Home
3. **[FASE 5]** Implement Table of Contents and Reactions UI
4. **[FASE 4]** Create Projects page and API
5. **[FASE 6]** Implement OAuth authentication
6. **[FASE 8]** Setup CI/CD with GitHub Actions

---

## 🔐 Environment Variables

### Backend `.env`
```bash
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/portfolio_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=portfolio_db
ENV=development  # production disables /docs
```

### Frontend `.env`
```bash
VITE_API_URL=http://localhost:8000
```

---

## ❓ Open Questions

1. **Blog Storage**: PostgreSQL (full CMS) vs GitHub markdown files?
   - Decision: PostgreSQL with optional GitHub sync
2. **Comments**: Giscus (GitHub Discussions) or custom?
   - Recommendation: Start with Giscus, migrate later if needed
3. **Analytics**: Plausible/Umami for privacy-friendly tracking?
   - Recommendation: Plausible (self-hosted or cloud)
4. **Domain**: Deployment target?
   - Recommendation: Railway or Fly.io for easy setup
