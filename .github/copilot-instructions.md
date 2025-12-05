# Copilot Instructions - Portfolio + Blog

## Arquitetura

Monorepo com frontend e backend separados, **Bun** como runtime.

```
frontend/  → Svelte 5 + Vite 7 (rolldown-vite) + Tailwind 4 + bits-ui
backend/   → Hono + Prisma 7 + PostgreSQL 17
plan/      → Documentação detalhada (consultar antes de implementar)
```

### Fluxo de Dados
```
Notion (fonte de verdade) → Backend sync → PostgreSQL (cache) → Frontend REST API
```
- Frontend **nunca** chama Notion diretamente
- Backend expõe `/api/posts`, `/api/projects`, `/api/sync`

## Comandos

```bash
# Backend - PostgreSQL + Dev
cd backend && docker compose -f docker/docker-compose.yml up -d
bun install && bun run index.ts
bunx prisma migrate dev --name <nome>
bunx prisma studio  # GUI localhost:5555

# Frontend
cd frontend && bun install && bun dev  # localhost:5173
```

## Convenções Específicas

### Frontend (`frontend/`)

**Svelte 5 - USE RUNES, não stores legados:**
```svelte
<script>
  let count = $state(0)           // ✅ Correto
  let doubled = $derived(count * 2)
  $effect(() => console.log(count))
</script>
```

**Vite usa rolldown-vite** (override em `package.json`):
```json
"overrides": { "vite": "npm:rolldown-vite@7.2.5" }
```

**Utilitário cn() para classes** (`src/lib/utils/cn.ts`):
```typescript
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

**Estrutura de pastas planejada:**
```
src/lib/
├── components/{ui,layout,blog}/
├── services/api.ts
├── stores/{posts,projects}.ts
└── utils/cn.ts
```

**Cores Tailwind** - Primary: `#208090` (teal):
```javascript
// frontend/tailwind.config.js
primary: { DEFAULT: '#208090', 700: '#208090', 800: '#1e5f6c' }
secondary: { DEFAULT: '#64748b' }
accent: { DEFAULT: '#f59e0b' }
```

### Backend (`backend/`)

**Hono + Zod validation:**
```typescript
import { zValidator } from '@hono/zod-validator'
import { z } from 'zod'
app.post('/api/posts', zValidator('json', schema), handler)
```

**Prisma 7** - Client em `generated/prisma`:
```typescript
// prisma.config.ts define output customizado
import { PrismaClient } from './generated/prisma'
```

**TypeScript strict** habilitado: `noUncheckedIndexedAccess`, `noImplicitOverride`

**Variáveis de ambiente (.env):**
```
DATABASE_URL="postgresql://dev:devpassword@localhost:5432/portfolio"
NOTION_API_KEY="secret_..."
NOTION_POSTS_DB_ID="..."
NOTION_PROJECTS_DB_ID="..."
```

## API Endpoints (Backend)

```
GET  /api/posts              # Lista posts publicados
GET  /api/posts/:slug        # Post por slug
GET  /api/posts/featured     # Posts em destaque
GET  /api/projects           # Lista projetos
GET  /api/projects/:slug     # Projeto por slug  
GET  /api/projects/featured  # Projetos em destaque
GET  /api/sync               # Trigger manual sync Notion → PostgreSQL
POST /api/sync/webhook       # Webhook para sync automático
```

## Prisma Schema (Models)

```prisma
// backend/prisma/schema.prisma
model Post {
  id          String    @id @default(cuid())
  slug        String    @unique
  title       String
  excerpt     String
  content     String?
  coverImage  String?
  tags        String[]
  published   Boolean   @default(false)
  featured    Boolean   @default(false)
  publishedAt DateTime?
  views       Int       @default(0)
  createdAt   DateTime  @default(now())
  updatedAt   DateTime  @updatedAt
}

model Project {
  id          String   @id @default(cuid())
  slug        String   @unique
  title       String
  description String
  content     String?
  coverImage  String
  images      String[]
  category    String   // web | mobile | design | fullstack
  tags        String[]
  link        String?
  repository  String?
  featured    Boolean  @default(false)
  views       Int      @default(0)
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt
}
```

## Schema Notion (Databases)

**Posts:** Title, Slug (único), Excerpt, Content, CoverImage, Tags, Published, Featured, PublishedAt, Views

**Projects:** Title, Slug (único), Description, Content, CoverImage, Images, Category (select: web/mobile/design/fullstack), Tags, Link, Repository, Featured, Views

## Autenticação (Admin - A Implementar)

Plano básico para painel admin:
- JWT ou session-based com Hono middleware
- Rotas protegidas: `POST /api/posts`, `PUT /api/posts/:slug`, `DELETE /api/posts/:slug`
- Frontend: página `/admin` com login
- Considerar: Lucia Auth ou auth próprio com bcrypt

## Deploy

### Frontend → Vercel
```bash
cd frontend && bun run build
# Configurar na dashboard Vercel:
# - VITE_API_URL=https://seu-backend.workers.dev
# - Build command: bun run build
# - Output directory: dist
```

### Backend → Cloudflare Workers
```bash
cd backend
# wrangler.toml já configurado
bunx wrangler deploy

# Secrets necessários:
wrangler secret put DATABASE_URL
wrangler secret put NOTION_API_KEY
wrangler secret put NOTION_POSTS_DB_ID
wrangler secret put NOTION_PROJECTS_DB_ID
```

### CI/CD (GitHub Actions)
```yaml
# .github/workflows/deploy.yml
name: Deploy
on:
  push:
    branches: [main]

jobs:
  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: oven-sh/setup-bun@v2
      - run: cd frontend && bun install && bun run build
      - uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: cloudflare/wrangler-action@v3
        with:
          apiToken: ${{ secrets.CF_API_TOKEN }}
          workingDirectory: backend
```

## Documentação de Referência

| Tarefa | Arquivo |
|--------|---------|
| Implementar frontend completo | `plan/frontend-docs.md` |
| Integração Notion + Services | `plan/notion-integration-updated.md` |
| Checklist passo-a-passo | `plan/checklist-completo.md` |
| Visão geral do projeto | `plan/guia-executivo.md` |

**IMPORTANTE:** Consulte `plan/` antes de criar novos arquivos - há templates prontos para NotionService, SyncService, componentes UI, stores e rotas.
