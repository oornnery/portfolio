# ✅ Checklist Completo: Notion Integration + Frontend Setup

**Projeto**: Portfolio + Blog  
**Data**: Dezembro 2025  
**Status**: 🚀 Ready to Deploy

---

## 📋 FASE 1: Setup Backend PostgreSQL

### Docker & Database

- [ ] **Instalar Docker** (se não tiver)

  ```bash
  # Verificar
  docker --version
  ```

- [ ] **Criar `docker-compose.yml`** na pasta `backend/`

  ```yaml
  version: '3.8'
  services:
    db:
      image: postgres:17-alpine
      environment:
        POSTGRES_USER: user
        POSTGRES_PASSWORD: password
        POSTGRES_DB: portfolio
      ports:
        - "5432:5432"
      volumes:
        - postgres_data:/var/lib/postgresql/data

  volumes:
    postgres_data:
  ```

- [ ] **Iniciar PostgreSQL**

  ```bash
  cd ~/proj/portfolio/backend
  docker-compose up -d
  # Verificar
  docker ps | grep postgres
  ```

- [ ] **Configurar `.env`** backend

  ```env
  DATABASE_URL="postgresql://user:password@localhost:5432/portfolio?schema=public"
  NOTION_API_KEY="secret_..."
  NOTION_POSTS_DB_ID="abc123..."
  NOTION_PROJECTS_DB_ID="xyz789..."
  NOTION_SYNC_INTERVAL=3600
  NOTION_WEBHOOK_SECRET="seu-secret"
  PORT=3000
  FRONTEND_URL="http://localhost:5173"
  ```

- [ ] **Rodar Prisma Migration**

  ```bash
  cd ~/proj/portfolio/backend
  bunx prisma migrate dev --name init
  # ✅ Se sucesso: "✔ Generated Prisma Client"
  ```

- [ ] **Verificar banco criado**

  ```bash
  bunx prisma studio
  # Abrir http://localhost:5555
  ```

---

## 📋 FASE 2: Setup Notion API

### Integração Notion

- [ ] **Criar Integration**
  - Acesse <https://www.notion.com/my-integrations>
  - Criar nova integração: "Portfolio Blog"
  - Copiar `NOTION_API_KEY` (começa com `secret_`)

- [ ] **Criar Database: Posts**
  - Nova página no Notion → `/database` → "Full page database"
  - Nomear: **Posts**
  - Adicionar integração (•••  → Add connections)
  - Copiar ID: `https://www.notion.so/workspace/[ID]?v=...`
  - Salvar em `.env` como `NOTION_POSTS_DB_ID`

- [ ] **Criar Database: Projects**
  - Repetir processo
  - Nomear: **Projects**
  - Salvar em `.env` como `NOTION_PROJECTS_DB_ID`

- [ ] **Adicionar Colunas: Posts Database**

  ```
  ✅ Title (Text)
  ✅ Slug (Text - Unique)
  ✅ Excerpt (Text)
  ✅ Content (Rich text)
  ✅ CoverImage (URL)
  ✅ Tags (Multi-select)
  ✅ Published (Checkbox)
  ✅ Featured (Checkbox)
  ✅ PublishedAt (Date)
  ✅ Views (Number, default: 0)
  ```

- [ ] **Adicionar Colunas: Projects Database**

  ```
  ✅ Title (Text)
  ✅ Slug (Text - Unique)
  ✅ Description (Text)
  ✅ Content (Rich text)
  ✅ CoverImage (URL)
  ✅ Images (Multi-select)
  ✅ Category (Select: web, mobile, design, fullstack)
  ✅ Tags (Multi-select)
  ✅ Link (URL)
  ✅ Repository (URL)
  ✅ Featured (Checkbox)
  ✅ Views (Number, default: 0)
  ```

- [ ] **Testar Conexão**

  ```bash
  cd ~/proj/portfolio/backend
  bun --watch run src/index.ts
  # Deve iniciar sem erros
  ```

---

## 📋 FASE 3: Setup Backend Services

### Notion Client

- [ ] **Instalar Notion SDK**

  ```bash
  cd ~/proj/portfolio/backend
  bun add @notionhq/client
  ```

- [ ] **Criar `src/services/NotionService.ts`**
  - [ ] Copiar conteúdo da documentação
  - [ ] Verificar tipos TypeScript
  - [ ] Testar imports

- [ ] **Criar `src/services/SyncService.ts`**
  - [ ] Copiar conteúdo da documentação
  - [ ] Verificar método `syncAllFromNotion()`
  - [ ] Testar imports Prisma

- [ ] **Criar `src/routes/sync.ts`**
  - [ ] Copiar conteúdo da documentação
  - [ ] Adicionar em `src/index.ts`: `app.route('/api/sync', syncRouter)`

- [ ] **Atualizar `src/index.ts`**

  ```typescript
  // Adicionar sync inicial e automático
  
  (async () => {
    logger.info('⏳ Sync inicial...');
    await syncAllFromNotion().catch(err => {
      logger.warn('Sync inicial falhou (Notion indisponível?)', err);
    });
  })();

  setInterval(async () => {
    logger.info('🔄 Sync automático...');
    await syncAllFromNotion().catch(err => {
      logger.error('Erro no sync:', err);
    });
  }, parseInt(process.env.NOTION_SYNC_INTERVAL || '3600') * 1000);
  ```

- [ ] **Testar Sync Manual**

  ```bash
  # Terminal rodando backend
  # Em outro terminal:
  curl http://localhost:3000/api/sync
  
  # Verificar Prisma Studio
  bunx prisma studio
  # Deve ter Posts e Projects no banco
  ```

---

## 📋 FASE 4: Setup Frontend Dependências

### Instalação

- [ ] **Navegar para frontend**

  ```bash
  cd ~/proj/portfolio/frontend
  ```

- [ ] **Instalar dependências principais**

  ```bash
  bun add bits-ui clsx tailwind-merge
  # ✅ Se sucesso: "installed X packages"
  ```

- [ ] **Instalar tipagens (se necessário)**

  ```bash
  bun add -D @types/node
  ```

- [ ] **Verificar instaladas**

  ```bash
  bun ls | grep -E "vite|svelte|tailwindcss|bits-ui|lucide"
  # Deve listar todas
  ```

---

## 📋 FASE 5: Setup Frontend Estrutura

### Pastas e Arquivos

- [ ] **Criar estrutura de pastas**

  ```bash
  mkdir -p src/lib/{components/{ui,layout,blog},services,stores,utils}
  ```

- [ ] **Criar arquivos vazios**

  ```bash
  touch src/lib/utils/cn.ts
  touch src/lib/services/api.ts
  touch src/lib/stores/posts.ts
  touch src/lib/stores/projects.ts
  touch src/lib/components/ui/button.svelte
  touch src/lib/components/ui/card.svelte
  touch src/lib/components/ui/index.ts
  touch src/lib/components/blog/PostCard.svelte
  touch src/lib/components/blog/ProjectCard.svelte
  touch tailwind.config.js
  touch src/app.css
  touch .env.local
  ```

---

## 📋 FASE 6: Implementar Frontend Arquivos

### Utilities

- [ ] **`src/lib/utils/cn.ts`**

  ```typescript
  import { clsx, type ClassValue } from 'clsx';
  import { twMerge } from 'tailwind-merge';
  
  export function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
  }
  ```

### Tailwind

- [ ] **`tailwind.config.js`**
  - [ ] Copiar completo da documentação
  - [ ] Verificar cores primária (#208090)
  - [ ] Verificar extensões de tema

- [ ] **`src/app.css`**
  - [ ] Copiar @tailwind directives
  - [ ] Copiar @layer components
  - [ ] Verificar imports

### Componentes UI

- [ ] **`src/lib/components/ui/button.svelte`**
  - [ ] Copiar da documentação
  - [ ] Verificar props
  - [ ] Testar variantes

- [ ] **`src/lib/components/ui/card.svelte`**
  - [ ] Copiar da documentação
  - [ ] Verificar classes Tailwind

- [ ] **`src/lib/components/ui/index.ts`**

  ```typescript
  export { default as Button } from './button.svelte';
  export { default as Card } from './card.svelte';
  ```

### Components Blog

- [ ] **`src/lib/components/blog/PostCard.svelte`**
  - [ ] Copiar da documentação frontend-docs.md
  - [ ] Verificar imports (Button, Card, lucide-svelte)

- [ ] **`src/lib/components/blog/ProjectCard.svelte`**
  - [ ] Copiar da documentação frontend-docs.md
  - [ ] Verificar imports

### Services & Stores

- [ ] **`src/lib/services/api.ts`**
  - [ ] Copiar da documentação
  - [ ] Verificar interfaces Post e Project
  - [ ] Verificar VITE_API_URL

- [ ] **`src/lib/stores/posts.ts`**
  - [ ] Copiar da documentação
  - [ ] Verificar imports

- [ ] **`src/lib/stores/projects.ts`**
  - [ ] Copiar da documentação
  - [ ] Verificar imports

### Routes

- [ ] **`src/routes/+layout.svelte`**

  ```svelte
  <script>
    import '../app.css';
  </script>
  
  <slot />
  ```

- [ ] **`src/routes/+page.svelte`** (Home)
  - [ ] Copiar da documentação frontend-docs.md
  - [ ] Verificar imports
  - [ ] Testar renderização

### Configuração

- [ ] **`.env.local`**

  ```env
  VITE_API_URL=http://localhost:3000
  ```

---

## 📋 FASE 7: Testar Frontend

### Dev Server

- [ ] **Iniciar dev server**

  ```bash
  cd ~/proj/portfolio/frontend
  bun run dev
  
  # Deve ver:
  # ROLLDOWN-VITE v7.2.5  ready in ...
  # ➜  Local:   http://localhost:5173/
  ```

- [ ] **Acessar no navegador**
  - [ ] `http://localhost:5173/`
  - [ ] Ver home page
  - [ ] Sem erros no console (F12)

- [ ] **Verificar dados**
  - [ ] F12 → Network
  - [ ] Fazer requisição para `http://localhost:3000/api/posts`
  - [ ] Deve retornar JSON com posts

- [ ] **Testar HMR**
  - [ ] Editar arquivo `.svelte`
  - [ ] Page deve atualizar automaticamente
  - [ ] Sem perder estado

---

## 📋 FASE 8: Criar Páginas Dinâmicas

### Blog

- [ ] **`src/routes/blog/+page.svelte`** (Lista)
  - [ ] Criar página listando posts
  - [ ] Usar PostCard component
  - [ ] Testar paginação (se aplicável)

- [ ] **`src/routes/blog/[slug]/+page.svelte`** (Detalhe)
  - [ ] Criar página individual de post
  - [ ] Carregar por slug
  - [ ] Renderizar markdown (conteúdo)

### Portfolio

- [ ] **`src/routes/portfolio/+page.svelte`** (Lista)
  - [ ] Criar página listando projetos
  - [ ] Usar ProjectCard component
  - [ ] Filtrar por categoria (opcional)

- [ ] **`src/routes/portfolio/[slug]/+page.svelte`** (Detalhe)
  - [ ] Criar página individual de projeto
  - [ ] Mostrar detalhes completos
  - [ ] Links para site e GitHub

---

## 📋 FASE 9: Layout Components

### Header e Footer

- [ ] **`src/lib/components/layout/Header.svelte`**
  - [ ] Logo
  - [ ] Navegação
  - [ ] Theme toggle (dark mode)

- [ ] **`src/lib/components/layout/Footer.svelte`**
  - [ ] Copyright
  - [ ] Links sociais
  - [ ] Contato

- [ ] **Integrar em `src/routes/+layout.svelte`**

  ```svelte
  <script>
    import Header from '$lib/components/layout/Header.svelte';
    import Footer from '$lib/components/layout/Footer.svelte';
    import '../app.css';
  </script>
  
  <Header />
  <main>
    <slot />
  </main>
  <Footer />
  ```

---

## 📋 FASE 10: Build & Deploy

### Frontend Build

- [ ] **Testar build**

  ```bash
  cd ~/proj/portfolio/frontend
  bun run build
  
  # Deve gerar pasta `.svelte-kit/`
  ```

- [ ] **Preview build**

  ```bash
  bun run preview
  # Acessar http://localhost:4173
  ```

### Backend Build

- [ ] **Testar build backend**

  ```bash
  cd ~/proj/portfolio/backend
  bun run build
  ```

### Preparar Deploy

- [ ] **Frontend → Vercel**
  - [ ] Fazer push para GitHub
  - [ ] Conectar repo no Vercel
  - [ ] Configurar env vars: `VITE_API_URL`
  - [ ] Deploy automático

- [ ] **Backend → Cloudflare Workers**
  - [ ] Instalar `wrangler`
  - [ ] Configurar `wrangler.toml`
  - [ ] Adicionar secrets via CLI
  - [ ] Deploy com `bunx wrangler deploy`

---

## 📋 FASE 11: Pós-Deploy

### Testes Finais

- [ ] **Testar Frontend em Produção**
  - [ ] Verificar carregamento
  - [ ] Verificar dados vindos da API
  - [ ] Testar navegação

- [ ] **Testar Backend em Produção**
  - [ ] Verificar `/api/posts` funcionando
  - [ ] Verificar `/api/projects` funcionando
  - [ ] Verificar `/api/sync` (se público)

- [ ] **Testar Notion Sync**
  - [ ] Criar novo post no Notion
  - [ ] Marcar como "Published"
  - [ ] Aguardar sync automático
  - [ ] Verificar no site

### Monitoramento

- [ ] **Configurar Logs**
  - [ ] Backend: Pino logger
  - [ ] Frontend: Sentry (opcional)

- [ ] **Backup Dados**
  - [ ] PostgreSQL backup automático
  - [ ] GitHub commits regulares

---

## 🎯 Summary: Seu Stack Está Pronto

```
Frontend:
├─ Svelte 5 ✅
├─ Vite 7 + Rolldown ✅ (16× mais rápido!)
├─ Tailwind 4 ✅
├─ bits-ui ✅
└─ Deploy: Vercel ✅

Backend:
├─ Hono + Bun ✅
├─ PostgreSQL 17 ✅
├─ Prisma ORM ✅
├─ Notion Integration ✅
└─ Deploy: Cloudflare Workers ✅

Total: ~1.5-2 horas de setup! 🚀
```

---

**Checklist v1.0 | Complete Portfolio Setup**  
**Last Updated**: Dezembro 05, 2025, 23:33 -03
