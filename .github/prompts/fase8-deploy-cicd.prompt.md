---
description: Phase 8 - GitHub Actions CI/CD and production deployment
---

# FASE 8: Deploy & CI/CD

## Status: 🔲 NÃO INICIADO

Configuração de deploy, GitHub Actions e monitoramento.

---

## 🔲 Tarefas Pendentes

### 8.1 GitHub Actions - CI
- [ ] Criar `.github/workflows/ci.yml`
- [ ] Backend: lint, type check, tests
- [ ] Frontend: lint, type check, build
- [ ] Docker build test
- [ ] Dependabot configuration

### 8.2 GitHub Actions - CD
- [ ] Criar `.github/workflows/deploy.yml`
- [ ] Deploy automático em push para main
- [ ] Rollback automático em caso de falha
- [ ] Environments (staging, production)
- [ ] Secrets management

### 8.3 Docker Production
- [ ] Docker Compose production-ready
- [ ] Nginx reverse proxy
- [ ] SSL/TLS com Let's Encrypt
- [ ] Health checks
- [ ] Log aggregation

### 8.4 Deployment Options
- [ ] Railway (recomendado para início)
- [ ] Vercel (frontend)
- [ ] Fly.io (backend)
- [ ] DigitalOcean Apps
- [ ] Self-hosted VPS

### 8.5 Database Production
- [ ] PostgreSQL managed (Railway, Supabase, Neon)
- [ ] Backup automático
- [ ] Connection pooling (PgBouncer)
- [ ] Migrations com Alembic

### 8.6 Monitoring
- [ ] Uptime monitoring (Better Uptime, UptimeRobot)
- [ ] Error tracking (Sentry)
- [ ] Log management (Logflare, Axiom)
- [ ] Performance monitoring
- [ ] Alertas (Discord, Slack)

### 8.7 Domain & DNS
- [ ] Domínio personalizado
- [ ] DNS configuration
- [ ] SSL certificate
- [ ] CDN (Cloudflare)

---

## 📋 Implementação

### CI Workflow
```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  PYTHON_VERSION: "3.14"
  NODE_VERSION: "22"

jobs:
  # Backend CI
  backend:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: backend

    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v4
        with:
          version: "latest"

      - name: Set up Python
        run: uv python install ${{ env.PYTHON_VERSION }}

      - name: Install dependencies
        run: uv sync

      - name: Lint with Ruff
        run: |
          uv run ruff check .
          uv run ruff format --check .

      - name: Type check
        run: uv run ty check .

      - name: Run tests
        run: uv run pytest -v --cov=app
        env:
          DATABASE_URL: sqlite+aiosqlite:///./test.db
          ENV: test

  # Frontend CI
  frontend:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: frontend

    steps:
      - uses: actions/checkout@v4

      - name: Setup Bun
        uses: oven-sh/setup-bun@v2
        with:
          bun-version: latest

      - name: Install dependencies
        run: bun install

      - name: Lint with Biome
        run: bunx biome check .

      - name: Type check
        run: bun run tsc --noEmit

      - name: Build
        run: bun run build

  # Docker Build Test
  docker:
    runs-on: ubuntu-latest
    needs: [backend, frontend]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Build Backend
        uses: docker/build-push-action@v6
        with:
          context: ./backend
          file: ./backend/docker/Dockerfile.prod
          push: false
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Build Frontend
        uses: docker/build-push-action@v6
        with:
          context: ./frontend
          file: ./frontend/docker/Dockerfile.prod
          push: false
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

### CD Workflow (Railway)
```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production

    steps:
      - uses: actions/checkout@v4

      - name: Install Railway CLI
        run: npm i -g @railway/cli

      - name: Deploy to Railway
        run: railway up --detach
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
```

### Dependabot Configuration
```yaml
# .github/dependabot.yml
version: 2
updates:
  # Python dependencies
  - package-ecosystem: "pip"
    directory: "/backend"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
    groups:
      python-deps:
        patterns:
          - "*"

  # JavaScript dependencies
  - package-ecosystem: "npm"
    directory: "/frontend"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
    groups:
      js-deps:
        patterns:
          - "*"

  # Docker
  - package-ecosystem: "docker"
    directory: "/backend/docker"
    schedule:
      interval: "weekly"

  - package-ecosystem: "docker"
    directory: "/frontend/docker"
    schedule:
      interval: "weekly"

  # GitHub Actions
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

### Alembic Setup
```bash
# backend/
cd backend
uv add alembic

# Initialize Alembic
uv run alembic init migrations
```

```python
# backend/migrations/env.py
import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

from app.config import settings
from app.models.blog import Post, Reaction  # Import all models
# from app.models.user import User
# from app.models.comment import Comment
# from app.models.project import Project

from sqlmodel import SQLModel

config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()

def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### Railway Configuration
```toml
# railway.toml
[build]
builder = "dockerfile"
dockerfilePath = "docker/Dockerfile.prod"

[deploy]
healthcheckPath = "/health"
healthcheckTimeout = 30
restartPolicyType = "on_failure"
restartPolicyMaxRetries = 3
```

### Production Environment Variables
```bash
# Railway / Hosting Environment Variables

# Backend
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
ENV=production
ALLOW_ORIGINS=["https://yourdomain.com"]
ALLOWED_HOSTS=["yourdomain.com","api.yourdomain.com"]
SECRET_KEY=your-super-secret-key-here
REDIS_URL=redis://user:pass@host:6379

# OAuth (optional)
GITHUB_CLIENT_ID=xxx
GITHUB_CLIENT_SECRET=xxx
GOOGLE_CLIENT_ID=xxx
GOOGLE_CLIENT_SECRET=xxx

# Sentry (optional)
SENTRY_DSN=https://xxx@sentry.io/xxx

# Frontend
VITE_API_URL=https://api.yourdomain.com
```

### Nginx SSL Configuration (Self-hosted)
```nginx
# /etc/nginx/sites-available/portfolio
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
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;

    # Frontend
    location / {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 🎯 Critérios de Conclusão

- [ ] CI workflow funcionando
- [ ] CD workflow funcionando
- [ ] Dependabot configurado
- [ ] Database migrations (Alembic)
- [ ] Deploy em produção
- [ ] SSL/HTTPS configurado
- [ ] Domínio personalizado
- [ ] Monitoring configurado
- [ ] Backups automáticos

---

## 🔗 Navegação entre Fases

← [FASE 7: Security & Performance](./fase7-security-performance.prompt.md)
→ [FASE 9: Polish & Extras](./fase9-polish-extras.prompt.md)
