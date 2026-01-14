# Portfolio - FastAPI + JinjaX + HTMX

Minimalist full-stack portfolio with blog, projects, analytics, and resume management.

## Tech Stack

| Layer               | Technology                                 | Description                                     |
| ------------------- | ------------------------------------------ | ----------------------------------------------- |
| **Backend**         | [FastAPI](https://fastapi.tiangolo.com/)   | Async web framework with automatic OpenAPI docs |
| **Templates**       | [JinjaX](https://jinjax.scaletti.dev/)     | Component-based templating for Jinja2           |
| **Frontend**        | [HTMX](https://htmx.org/)                  | Dynamic interactions without JavaScript         |
| **Database**        | [SQLModel](https://sqlmodel.tiangolo.com/) | Async ORM built on SQLAlchemy + Pydantic        |
| **Styling**         | Custom CSS + Tailwind                      | Design system with dark/light themes            |
| **Package Manager** | [UV](https://github.com/astral-sh/uv)      | Fast Python package manager (Rust-based)        |
| **Database**        | PostgreSQL (prod) / SQLite (dev)           | Async with asyncpg/aiosqlite                    |

## Current Status & Features

### Core Features ✅

- 📝 **Blog** - Full-featured blog with categories, tags, reactions, and HTMX-powered comments.
- 📁 **Projects** - Portfolio showcase with tech stack tags and featured status.
- 📄 **Resume/CV** - Structured work experience, education, certificates, and skills.
- 🔐 **Admin Panel** - Secure dashboard for full content management (CRUD).
- 🔑 **Auth** - Secure cookie-based JWT authentication + GitHub OAuth support.
- 🛡️ **Security** - OWASP headers, CSP, rate limiting, and HTMX origin validation.
- 🌙 **Modern UI** - Component-based CamelCase architecture with responsive design (Dark/Light).

### Recent Revisions (Refactoring Phase) 🛠️

- **Component Architecture**: Renamed all 47 components to **CamelCase** (e.g., `Button.jinja`, `PostCard.jinja`) for better modularity.
- **Design System**: Implemented `tokens.css` (color palette, spacing, typography) and `motion.css` (animations).
- **Backend Restructuring**: Decoupled `BlogService` into a dedicated package and moved telemetry to file logs.
- **Bug Fixes**:
  - Resolved HTMX JSON rendering issues in comments.
  - Standardized special character encoding via HTML entities.
  - Improved Login UX with better placeholders.

### Roadmap (Pending Features) 🚀

- [ ] **Theme Toggle UI** - Dedicated component for manual theme switching (System/Light/Dark).
- [ ] **Search Improvements** - Enhanced real-time search for blog and projects using HTMX.
- [ ] **Advanced Analytics** - Detailed charts for pageview trends and visitor demographics.
- [ ] **Resume PDF Export** - Polished WeasyPrint integration for high-quality CV downloads.
- [ ] **Activity Log** - Admin-only view for tracking content changes and login attempts.

---

## Design System

### Color Palette

#### Dark Theme (default)

| Token         | Value     | Usage                   |
| ------------- | --------- | ----------------------- |
| `--bg`        | `#0b0b0d` | Page background         |
| `--surface`   | `#121215` | Card backgrounds        |
| `--surface-2` | `#1a1a1f` | Hover states            |
| `--text`      | `#ededed` | Primary text            |
| `--text-2`    | `#a1a1aa` | Secondary text          |
| `--text-3`    | `#6b7280` | Muted text              |
| `--border`    | `#1f1f26` | Borders                 |
| `--accent`    | `#7c7cff` | Primary accent (purple) |
| `--accent-2`  | `#22c55e` | Success (green)         |
| `--warn`      | `#f59e0b` | Warning (amber)         |
| `--danger`    | `#ef4444` | Error (red)             |

#### Light Theme

| Token         | Value     | Usage                   |
| ------------- | --------- | ----------------------- |
| `--bg`        | `#fafafa` | Page background         |
| `--surface`   | `#ffffff` | Card backgrounds        |
| `--surface-2` | `#f4f4f5` | Hover states            |
| `--text`      | `#0f172a` | Primary text            |
| `--accent`    | `#4f46e5` | Primary accent (indigo) |

### Typography

| Class    | Size | Line-height | Weight | Usage           |
| -------- | ---- | ----------- | ------ | --------------- |
| `.h1`    | 40px | 48px        | 600    | Page titles     |
| `.h2`    | 28px | 36px        | 600    | Section headers |
| `.h3`    | 22px | 30px        | 500    | Card titles     |
| `.body`  | 16px | 24px        | 400    | Body text       |
| `.small` | 14px | 20px        | 400    | Meta text       |
| `.tiny`  | 12px | 16px        | mono   | Tags, badges    |

**Fonts:**

- Sans: Inter, system-ui, -apple-system
- Mono: JetBrains Mono, Consolas

### Spacing Scale

| Token       | Value | Usage            |
| ----------- | ----- | ---------------- |
| `--space-1` | 8px   | Tight padding    |
| `--space-2` | 16px  | Standard padding |
| `--space-3` | 24px  | Card padding     |
| `--space-4` | 32px  | Section gap      |
| `--space-5` | 48px  | Large sections   |
| `--space-6` | 64px  | Page sections    |

### Border Radius

| Token           | Value | Usage           |
| --------------- | ----- | --------------- |
| `--radius-sm`   | 10px  | Buttons, inputs |
| `--radius-md`   | 14px  | Cards           |
| `--radius-lg`   | 18px  | Large cards     |
| `--radius-pill` | 999px | Tags, badges    |

### Shadows

| Token         | Value                          |
| ------------- | ------------------------------ |
| `--shadow-sm` | `0 6px 16px rgba(0,0,0,0.18)`  |
| `--shadow-md` | `0 10px 30px rgba(0,0,0,0.22)` |

---

## Animations

### Keyframes

| Animation      | Effect                      |
| -------------- | --------------------------- |
| `fadeUp`       | Fade in + translate up 10px |
| `fadeIn`       | Simple opacity fade         |
| `slideInRight` | Slide from right 20px       |
| `scaleIn`      | Scale from 0.95 to 1        |

### Utility Classes

| Class            | Effect                           |
| ---------------- | -------------------------------- |
| `.t`             | Base transition (180ms ease-out) |
| `.enter`         | fadeUp animation on mount        |
| `.hover-lift`    | translateY(-2px) on hover        |
| `.hover-scale`   | scale(1.02) on hover             |
| `.card-animated` | Hover lift + shadow              |
| `.nav-blur`      | backdrop-filter: blur(10px)      |

### Stagger Delays

```css
.stagger-1 { animation-delay: 50ms; }
.stagger-2 { animation-delay: 100ms; }
.stagger-3 { animation-delay: 150ms; }
.stagger-4 { animation-delay: 200ms; }
.stagger-5 { animation-delay: 250ms; }
.stagger-6 { animation-delay: 300ms; }
```

---

## UI Components

### Button

Variants: `primary`, `secondary`, `ghost`, `danger`  
Sizes: `sm`, `md`, `lg`  
States: `default`, `hover`, `active`, `disabled`, `loading`

```jinja
<Button variant="primary" size="lg">Click me</Button>
<Button variant="ghost" href="/about">Learn more →</Button>
```

### Card

Variants: `default`, `featured`  
Effects: Hover lift + shadow

```jinja
<Card title="Project Name" href="/projects/1">
  Description here
</Card>
```

### Tag

Style: Pill shape, mono font

```jinja
<Tag>Python</Tag>
<Tag variant="accent">Featured</Tag>
```

### Input

Types: `text`, `email`, `textarea`  
States: `default`, `focus`, `error`

```jinja
<Input name="email" type="email" placeholder="Email" required />
```

### Icon

Available: `github`, `linkedin`, `email`, `twitter`, `search`, `menu`, `plus`, `edit`, `trash`, `external-link`

```jinja
<Icon name="github" size="sm" />
```

### Navbar

Sticky, blur background on scroll

### EmptyState

Icon + message + optional CTA

---

## Pages & Routes

| Route              | Page            | Description                                 |
| ------------------ | --------------- | ------------------------------------------- |
| `/`                | Home            | Hero, featured projects, latest blog, CTA   |
| `/about`           | About           | Profile, experience, skills, certifications |
| `/projects`        | Projects        | Filterable project grid                     |
| `/projects/{id}`   | Project Detail  | Overview, features, tech stack              |
| `/blog`            | Blog            | Searchable post list by category            |
| `/blog/{slug}`     | Blog Post       | Content, share, comments                    |
| `/contact`         | Contact         | Social links + contact form                 |
| `/admin`           | Admin Dashboard | Stats overview                              |
| `/admin/blog`      | Admin Blog      | Post CRUD                                   |
| `/admin/projects`  | Admin Projects  | Project CRUD                                |
| `/admin/profile`   | Admin Profile   | Resume editing                              |
| `/admin/analytics` | Admin Analytics | Visitor stats                               |

---

## Responsive Breakpoints

| Breakpoint           | Columns | Margin | Gutter | Container  |
| -------------------- | ------- | ------ | ------ | ---------- |
| **Desktop (1440px)** | 12      | 160px  | 24px   | 1120px     |
| **Tablet (768px)**   | 8       | 32px   | 20px   | 704px      |
| **Mobile (390px)**   | 4       | 16px   | 16px   | full-width |

---

## Project Structure

```bash
app/
├── main.py                 # App entry, middleware, routers
├── config.py               # Settings via pydantic-settings
├── db.py                   # Engine, session factory
├── seed.py                 # Database seeding
├── catalog.py              # JinjaX catalog configuration
├── api/v1/endpoints/       # JSON API endpoints
│   ├── auth.py             # OAuth & login
│   ├── blog.py             # Posts & reactions CRUD
│   ├── comments.py         # Comments CRUD
│   ├── contact.py          # Contact form API
│   ├── projects.py         # Projects CRUD
│   ├── analytics.py        # Analytics data API
│   └── resume.py           # Resume PDF export
├── views/                  # HTML template views
│   ├── public/             # Public pages
│   └── admin/              # Admin panel routes
├── components/             # JinjaX components
│   ├── layouts/            # Base, Public, Admin, Home
│   ├── pages/              # Full page templates
│   ├── ui/                 # Button, Card, Input, Tag, Icon...
│   ├── blog/               # PostCard, Comments
│   ├── projects/           # ProjectCard
│   ├── profile/            # Header, Skills, Experience...
│   └── admin/              # Dashboard, forms
├── services/               # Business logic layer
│   └── blog/               # post_service, github_service
├── models/                 # SQLModel database schemas
├── core/                   # Auth, security, telemetry
├── middleware/             # Security headers, logging, analytics
└── static/
    ├── css/
    │   ├── tokens.css      # Design system tokens
    │   ├── motion.css      # Animations
    │   └── style.css       # Main styles
    └── js/                 # HTMX, theme toggle
logs/                       # Telemetry logs (gitignored)
```

---

## Getting Started

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Docker (optional, for PostgreSQL)

### 1. Clone & Install

```bash
git clone https://github.com/oornnery/portfolio.git
cd portfolio

# Install dependencies
uv sync
```

### 2. Environment Setup

```bash
# Copy example environment file
cp .env.example .env

# Edit with your settings
nano .env
```

**Required for development:**

```env
DATABASE_URL=sqlite+aiosqlite:///./portfolio.db
SECRET_KEY=dev-secret-key-change-in-production
ENV=development
```

### 3. Run Development Server

```bash
uv run uvicorn app.main:app --reload
```

Access points:

- **App**: <http://localhost:8000>
- **API Docs**: <http://localhost:8000/docs>
- **Admin**: <http://localhost:8000/admin>
  - Login: `admin@example.com` / `admin123`

---

## API Endpoints

### Public API

| Method | Endpoint                       | Description         |
| ------ | ------------------------------ | ------------------- |
| GET    | `/api/v1/posts`                | List blog posts     |
| GET    | `/api/v1/posts/{slug}`         | Get post by slug    |
| POST   | `/api/v1/posts/{id}/reactions` | Add reaction        |
| GET    | `/api/v1/projects`             | List projects       |
| GET    | `/api/v1/projects/{id}`        | Get project         |
| POST   | `/api/v1/contact`              | Submit contact form |
| GET    | `/api/v1/comments/{post_id}`   | Get post comments   |
| POST   | `/api/v1/comments`             | Create comment      |

### Auth API

| Method | Endpoint              | Description  |
| ------ | --------------------- | ------------ |
| POST   | `/api/v1/auth/login`  | Login        |
| POST   | `/api/v1/auth/logout` | Logout       |
| GET    | `/api/v1/auth/me`     | Current user |
| GET    | `/api/v1/auth/github` | GitHub OAuth |

### Admin API (authenticated)

| Method | Endpoint                | Description    |
| ------ | ----------------------- | -------------- |
| POST   | `/api/v1/posts`         | Create post    |
| PUT    | `/api/v1/posts/{id}`    | Update post    |
| DELETE | `/api/v1/posts/{id}`    | Delete post    |
| POST   | `/api/v1/projects`      | Create project |
| PUT    | `/api/v1/projects/{id}` | Update project |
| DELETE | `/api/v1/projects/{id}` | Delete project |
| GET    | `/api/v1/analytics`     | Get analytics  |

---

## Security Features

| Feature              | Description                                               |
| -------------------- | --------------------------------------------------------- |
| **OWASP Headers**    | X-Content-Type-Options, X-Frame-Options, X-XSS-Protection |
| **CSP**              | Content Security Policy (strict in production)            |
| **CORS**             | Configurable allowed origins                              |
| **HTTPS Redirect**   | Automatic redirect in production                          |
| **JWT Auth**         | Secure cookie-based authentication                        |
| **Rate Limiting**    | slowapi with per-endpoint limits                          |
| **HTMX Validation**  | Origin validation for HTMX requests                       |
| **Input Validation** | Pydantic models for all inputs                            |

### Rate Limits

| Endpoint | Limit     |
| -------- | --------- |
| Global   | 60/minute |
| Login    | 10/minute |
| Register | 5/minute  |
| Contact  | 10/minute |

---

## Development Commands

```bash
# Run dev server with hot-reload
uv run uvicorn app.main:app --reload

# Lint & format (REQUIRED before commits)
uv run ruff format . && uv run ruff check . --fix --unsafe-fixes

# Type checking
uv run ty check .

# Run tests
uv run pytest -v

# Add dependencies
uv add <package>
uv add --dev <dev-package>
```

---

## Docker

### Development

```bash
docker compose -f docker/docker-compose.yml up
```

### Production

```bash
export $(cat .env.prod | xargs)
docker compose -f docker/docker-compose.prod.yml up --build -d
```

---

## Environment Variables

| Variable                | Required       | Default       | Description                |
| ----------------------- | -------------- | ------------- | -------------------------- |
| `ENV`                   | No             | `development` | Environment mode           |
| `DATABASE_URL`          | Yes            | SQLite        | Database connection string |
| `SECRET_KEY`            | **Yes (prod)** | Random        | JWT signing key            |
| `ALLOWED_HOSTS`         | **Yes (prod)** | localhost     | Allowed host headers       |
| `FORCE_HTTPS`           | No             | `false`       | Redirect HTTP to HTTPS     |
| `ALLOW_ORIGINS`         | No             | localhost     | CORS allowed origins       |
| `RATE_LIMIT_PER_MINUTE` | No             | `60`          | Global rate limit          |
| `GITHUB_CLIENT_ID`      | No             | -             | GitHub OAuth client ID     |
| `GITHUB_CLIENT_SECRET`  | No             | -             | GitHub OAuth secret        |
| `SEED_DB_ON_STARTUP`    | No             | `true`        | Auto-seed database         |

---

## License

This project is open source and available under the [MIT License](LICENSE).
