# Portfolio - FastAPI + JinjaX + HTMX

Minimalist full-stack portfolio with blog, projects, analytics, and resume management.

## Tech Stack

| Layer               | Technology                                 | Description                                     |
| ------------------- | ------------------------------------------ | ----------------------------------------------- |
| **Backend**         | [FastAPI](https://fastapi.tiangolo.com/)   | Async web framework with automatic OpenAPI docs |
| **Templates**       | [JinjaX](https://jinjax.scaletti.dev/)     | Component-based templating for Jinja2           |
| **Frontend**        | [HTMX](https://htmx.org/)                  | Dynamic interactions without JavaScript         |
| **Database**        | [SQLModel](https://sqlmodel.tiangolo.com/) | Async ORM built on SQLAlchemy + Pydantic        |
| **Styling**         | [Tailwind CSS](https://tailwindcss.com/)   | Utility-first CSS (via CDN)                     |
| **Package Manager** | [UV](https://github.com/astral-sh/uv)      | Fast Python package manager (Rust-based)        |
| **Database**        | PostgreSQL (prod) / SQLite (dev)           | Async with asyncpg/aiosqlite                    |

## Features

- 📝 **Blog** - Posts with categories, tags, reactions, comments
- 📁 **Projects** - Portfolio showcase with tech stack tags
- 📄 **Resume/CV** - Work experience, education, certificates, skills
- 📊 **Analytics** - Visitor tracking, pageviews, device stats
- 🔐 **Admin Panel** - Full CRUD for all content
- 🔑 **Auth** - Cookie-based JWT + optional GitHub/Google OAuth
- 🛡️ **Security** - OWASP headers, CORS, CSP, rate limiting
- 🖨️ **PDF Export** - Resume to PDF via WeasyPrint

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
│   ├── projects.py         # Projects CRUD
│   ├── analytics.py        # Analytics data API
│   └── resume.py           # Resume PDF export
├── views/                  # HTML template views
│   ├── public/             # Public pages (blog, projects, about)
│   └── admin/              # Admin panel routes
├── components/             # JinjaX components
│   ├── layouts/            # Base layouts (admin, public, home)
│   ├── pages/              # Full page templates
│   ├── ui/                 # Reusable UI components
│   ├── blog/               # Blog-specific components
│   ├── profile/            # Profile/resume components
│   └── admin/              # Admin panel components
├── services/               # Business logic layer
├── models/                 # SQLModel database schemas
├── core/                   # Auth, security, dependencies
├── middleware/             # Security headers, logging, analytics
└── static/                 # CSS, JS (htmx.min.js)
```

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

## Production Deployment

### Security Checklist

Before deploying to production, ensure:

- [ ] **SECRET_KEY** - Generate strong key: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- [ ] **ALLOWED_HOSTS** - Set to your domain(s)
- [ ] **ENV=production** - Disables debug features
- [ ] **FORCE_HTTPS=true** - Enable HTTPS redirect
- [ ] **Database passwords** - Use strong, unique passwords
- [ ] **SEED_DB_ON_STARTUP=false** - Disable after first run
- [ ] **Reverse proxy** - Use nginx/Caddy for SSL termination

### Docker Production

1. **Create production `.env`:**

```env
# .env.prod
ENV=production
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=postgresql+asyncpg://postgres:strong_password@db:5432/portfolio_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=strong_password
POSTGRES_DB=portfolio_db
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
FORCE_HTTPS=true
SEED_DB_ON_STARTUP=false
```

2. **Run with Docker Compose:**

```bash
# Load environment and start
export $(cat .env.prod | xargs)
docker compose -f docker/docker-compose.prod.yml up --build -d
```

### Recommended: Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Security headers
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/portfolio/app/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

## Security Features

### Implemented

| Feature              | Description                                               |
| -------------------- | --------------------------------------------------------- |
| **OWASP Headers**    | X-Content-Type-Options, X-Frame-Options, X-XSS-Protection |
| **CSP**              | Content Security Policy (strict in production)            |
| **CORS**             | Configurable allowed origins                              |
| **HTTPS Redirect**   | Automatic redirect in production                          |
| **JWT Auth**         | Secure cookie-based authentication                        |
| **Rate Limiting**    | slowapi with per-endpoint limits                          |
| **Trusted Hosts**    | Host header injection prevention                          |
| **Input Validation** | Pydantic models for all inputs                            |
| **SQL Injection**    | Protected via SQLModel ORM                                |

### Rate Limits

| Endpoint | Limit     |
| -------- | --------- |
| Global   | 60/minute |
| Login    | 10/minute |
| Register | 5/minute  |

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

## API Documentation

When running in development, interactive API docs are available:

- **Swagger UI**: <http://localhost:8000/docs>
- **ReDoc**: <http://localhost:8000/redoc>

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Run linting (`uv run ruff format . && uv run ruff check . --fix`)
4. Commit changes (`git commit -m 'Add amazing feature'`)
5. Push to branch (`git push origin feature/amazing-feature`)
6. Open Pull Request

## License

This project is open source and available under the [MIT License](LICENSE).

## Documentation

See [`.github/copilot-instructions.md`](.github/copilot-instructions.md) for detailed architecture, patterns, and conventions.
