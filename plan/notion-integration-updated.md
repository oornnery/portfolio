# 📋 Integração Notion + Svelte + Hono | Guia Completo

**Baseado em**: [eneskutlay/next-notion-blog](https://github.com/eneskutlay/next-notion-blog)  
**Data**: Dezembro 2025  
**Stack**: Svelte 5 + Vite 7 (Rolldown) + Tailwind 4 + bits-ui + Hono + Bun + PostgreSQL + Notion

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Arquitetura Notion Integration](#arquitetura)
3. [Setup Notion API](#setup-notion-api)
4. [Backend - Notion Client](#backend---notion-client)
5. [Sincronização de Dados](#sincronização-de-dados)
6. [Frontend - Exibição](#frontend---exibição)
7. [Tailwind Configuration](#tailwind-configuration)
8. [Boas Práticas](#boas-práticas)
9. [Deploy](#deploy)
10. [Troubleshooting](#troubleshooting)

---

## 📱 Visão Geral

### O que vamos fazer?

Criar um sistema onde:

1. **Notion é a fonte de verdade** - Você escreve posts/projetos no Notion
2. **Backend sincroniza** - Hono busca dados da Notion API e salva no PostgreSQL
3. **Frontend exibe** - Svelte mostra os dados do banco (rápido, sem chamar Notion)
4. **Fallback automático** - Se Notion cair, site continua funcionando

### Fluxo de Dados

```
┌─────────────────────────────────────────────────────────────┐
│                      NOTION                                 │
│    (Fonte de Verdade - Posts & Projects como Database)      │
└──────────────────────┬──────────────────────────────────────┘
                       │ (Notion API)
                       ↓
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND (Hono)                           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ • Sync Notion → PostgreSQL (automático)             │   │
│  │ • GET /api/sync (webhook do Notion)                 │   │
│  │ • Cache em Redis (opcional)                         │   │
│  │ • Transformação de dados                            │   │
│  └─────────────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────────────────────────┘
                       │ (REST API)
                       ↓
┌─────────────────────────────────────────────────────────────┐
│               FRONTEND (Svelte + Vite + Rolldown)           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ • GET /api/posts (dados do PostgreSQL)              │   │
│  │ • GET /api/projects (dados do PostgreSQL)           │   │
│  │ • Rápido e confiável                                │   │
│  │ • Sem dependência direta do Notion                  │   │
│  │ • Tailwind + bits-ui para UI moderna                │   │
│  └─────────────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────────┐
│              PostgreSQL Database                            │
│    (Cache sincronizado do Notion)                           │
└─────────────────────────────────────────────────────────────┘
```

### Vantagens dessa Abordagem

✅ **Performance** - Frontend não chama Notion API (lenta)
✅ **Confiabilidade** - Site funciona mesmo se Notion cair
✅ **SEO** - Dados já no banco, fácil fazer sitemap dinâmico
✅ **Escalabilidade** - Múltiplos usuários acessam cache
✅ **Flexibilidade** - Pode escrever em Notion E editar no painel admin
✅ **Transformação** - Você controla o formato dos dados
✅ **UI Moderna** - Tailwind + bits-ui para componentes acessíveis

---

## 🏗️ Arquitetura Notion Integration

### Estrutura de Dados Notion

**Database: Posts**

```
Columns:
- Title (Text) - Nome do post
- Slug (Text) - URL amigável, ÚNICO
- Excerpt (Text) - Descrição curta
- Content (Rich Text) - Corpo completo em Markdown
- CoverImage (URL) - Imagem de capa
- Tags (Multi-select) - Categorias
- Published (Checkbox) - Publicado ou draft
- Featured (Checkbox) - Destaque na home
- PublishedAt (Date) - Data de publicação
- Views (Number) - Contador de views
```

**Database: Projects**

```
Columns:
- Title (Text) - Nome do projeto
- Slug (Text) - URL amigável, ÚNICO
- Description (Text) - Descrição curta
- Content (Rich Text) - Detalhes completos
- CoverImage (URL) - Imagem principal
- Images (Multi-select → relacionada com Files) - Múltiplas imagens
- Category (Select) - web/mobile/design/fullstack
- Tags (Multi-select) - Tecnologias usadas
- Link (URL) - URL do projeto
- Repository (URL) - Link GitHub
- Featured (Checkbox) - Destaque na home
- Views (Number) - Contador
```

### Por que Notion é ideal?

| Aspecto | Vantagem |
|---------|----------|
| **Sem DB Setup** | Notion é o CMS, você só sincroniza |
| **Interface bonita** | Melhor que admin painel customizado |
| **Versionamento** | Notion guarda histórico automático |
| **Colaborativo** | Você e assistentes podem editar juntos |
| **Flexible** | Adicione colunas quando precisar |
| **Mobile-friendly** | Edit posts pelo celular no app Notion |

---

## 🔑 Setup Notion API

### Passo 1: Criar Integração no Notion

1. Acesse <https://www.notion.com/my-integrations>
2. Clique em **"+ New integration"**
3. Preencha:
   - **Name**: "Portfolio Blog"
   - **Logo**: (opcional)
   - **Associated workspace**: Seu workspace
   - **Capabilities**:
     - ✅ Read content
     - ✅ Update content
     - ✅ Insert content
     - ✅ Delete content
4. Clique **"Submit"**
5. Copie o **Internal Integration Token** (começa com `secret_...`)

### Passo 2: Criar Databases no Notion

**Para Posts:**

1. Novo página no Notion
2. Digite `/database` e escolha **"Database - Full page"**
3. Nomeie como **"Posts"**
4. Clique em `•••` → **"Add connections"** → Encontre sua integração
5. Copie a URL: `https://www.notion.so/workspace/123abc...?v=...`
   - Extract ID: `123abc...` (tudo antes de `?`)

**Para Projects:**

1. Repita o processo, nomeie como **"Projects"**
2. Copie o ID da database

### Passo 3: Adicionar Colunas

**Posts Database:**

```
1. Title (Text) ← Notion o cria automaticamente
2. Slug (Text, propriedade: Unique)
3. Excerpt (Text)
4. Content (Rich text)
5. CoverImage (URL)
6. Tags (Multi-select)
7. Published (Checkbox)
8. Featured (Checkbox)
9. PublishedAt (Date)
10. Views (Number, default: 0)
```

**Projects Database:**

```
1. Title (Text)
2. Slug (Text, propriedade: Unique)
3. Description (Text)
4. Content (Rich text)
5. CoverImage (URL)
6. Images (Multi-select)
7. Category (Select: web, mobile, design, fullstack)
8. Tags (Multi-select)
9. Link (URL)
10. Repository (URL)
11. Featured (Checkbox)
12. Views (Number, default: 0)
```

### Passo 4: Configurar .env Backend

```bash
# backend/.env

# Notion API
NOTION_API_KEY="secret_sua_chave_aqui"
NOTION_POSTS_DB_ID="abc123def456..."
NOTION_PROJECTS_DB_ID="xyz789uvw012..."

# Sincronização
NOTION_SYNC_INTERVAL=3600  # segundos (1 hora)
NOTION_WEBHOOK_SECRET="seu-webhook-secret-aleatorio"

# Database
DATABASE_URL="postgresql://user:password@localhost:5432/portfolio?schema=public"

# Outros
PORT=3000
FRONTEND_URL="http://localhost:5173"
NODE_ENV="development"
```

---

## 💾 Backend - Notion Client

### Passo 1: Instalar Notion SDK

```bash
cd backend
bun add @notionhq/client
bun add -D @types/@notionhq/client
```

### Passo 2: Criar Notion Service

**src/services/NotionService.ts**

```typescript
import { Client } from '@notionhq/client';

const notion = new Client({
  auth: process.env.NOTION_API_KEY,
});

export interface NotionPost {
  id: string;
  title: string;
  slug: string;
  excerpt: string;
  content: string;
  coverImage?: string;
  tags: string[];
  published: boolean;
  featured: boolean;
  publishedAt?: string;
  views: number;
}

export interface NotionProject {
  id: string;
  title: string;
  slug: string;
  description: string;
  content?: string;
  coverImage: string;
  images: string[];
  category: string;
  tags: string[];
  link?: string;
  repository?: string;
  featured: boolean;
  views: number;
}

export async function getNotionPosts(): Promise<NotionPost[]> {
  const response = await notion.databases.query({
    database_id: process.env.NOTION_POSTS_DB_ID!,
    filter: {
      property: 'Published',
      checkbox: { equals: true },
    },
    sorts: [
      {
        property: 'PublishedAt',
        direction: 'descending',
      },
    ],
  });

  return response.results.map((page: any) => parseNotionPost(page));
}

export async function getNotionPostBySlug(slug: string): Promise<NotionPost | null> {
  const response = await notion.databases.query({
    database_id: process.env.NOTION_POSTS_DB_ID!,
    filter: {
      property: 'Slug',
      text: { equals: slug },
    },
  });

  if (response.results.length === 0) return null;
  return parseNotionPost(response.results[0]);
}

export async function getNotionProjects(): Promise<NotionProject[]> {
  const response = await notion.databases.query({
    database_id: process.env.NOTION_PROJECTS_DB_ID!,
    sorts: [
      {
        property: 'Title',
        direction: 'ascending',
      },
    ],
  });

  return response.results.map((page: any) => parseNotionProject(page));
}

export async function getNotionProjectBySlug(slug: string): Promise<NotionProject | null> {
  const response = await notion.databases.query({
    database_id: process.env.NOTION_PROJECTS_DB_ID!,
    filter: {
      property: 'Slug',
      text: { equals: slug },
    },
  });

  if (response.results.length === 0) return null;
  return parseNotionProject(response.results[0]);
}

export async function getBlockContent(blockId: string): Promise<string> {
  const blocks = await notion.blocks.children.list({
    block_id: blockId,
  });

  let markdown = '';

  for (const block of blocks.results as any[]) {
    if (block.type === 'paragraph') {
      markdown += block.paragraph.rich_text
        .map((text: any) => text.plain_text)
        .join('') + '\\n\\n';
    } else if (block.type === 'heading_1') {
      markdown += '# ' + block.heading_1.rich_text.map((t: any) => t.plain_text).join('') + '\\n\\n';
    } else if (block.type === 'heading_2') {
      markdown += '## ' + block.heading_2.rich_text.map((t: any) => t.plain_text).join('') + '\\n\\n';
    } else if (block.type === 'bulleted_list_item') {
      markdown += '- ' + block.bulleted_list_item.rich_text.map((t: any) => t.plain_text).join('') + '\\n';
    } else if (block.type === 'code') {
      markdown += '\\`\\`\\`' + (block.code.language || '') + '\\n' +
                  block.code.rich_text.map((t: any) => t.plain_text).join('') +
                  '\\n\\`\\`\\`\\n\\n';
    }
  }

  return markdown;
}

function parseNotionPost(page: any): NotionPost {
  const props = page.properties;

  return {
    id: page.id,
    title: extractText(props.Title),
    slug: extractText(props.Slug),
    excerpt: extractText(props.Excerpt),
    content: extractText(props.Content),
    coverImage: props.CoverImage?.url,
    tags: extractMultiSelect(props.Tags),
    published: props.Published?.checkbox ?? false,
    featured: props.Featured?.checkbox ?? false,
    publishedAt: props.PublishedAt?.date?.start,
    views: props.Views?.number ?? 0,
  };
}

function parseNotionProject(page: any): NotionProject {
  const props = page.properties;

  return {
    id: page.id,
    title: extractText(props.Title),
    slug: extractText(props.Slug),
    description: extractText(props.Description),
    content: extractText(props.Content),
    coverImage: props.CoverImage?.url || '',
    images: props.Images?.url ? [props.Images.url] : [],
    category: extractSelect(props.Category),
    tags: extractMultiSelect(props.Tags),
    link: props.Link?.url,
    repository: props.Repository?.url,
    featured: props.Featured?.checkbox ?? false,
    views: props.Views?.number ?? 0,
  };
}

function extractText(prop: any): string {
  if (!prop) return '';
  if (prop.type === 'title') {
    return prop.title.map((t: any) => t.plain_text).join('');
  }
  if (prop.type === 'rich_text') {
    return prop.rich_text.map((t: any) => t.plain_text).join('');
  }
  return '';
}

function extractSelect(prop: any): string {
  return prop?.select?.name || '';
}

function extractMultiSelect(prop: any): string[] {
  return prop?.multi_select?.map((item: any) => item.name) || [];
}

export default {
  getNotionPosts,
  getNotionPostBySlug,
  getNotionProjects,
  getNotionProjectBySlug,
  getBlockContent,
};
```

### Passo 3: Criar Sync Service

**src/services/SyncService.ts**

```typescript
import { prisma } from '$config/db';
import NotionService from './NotionService';
import { logger } from '$utils/logger';

export async function syncPostsFromNotion() {
  try {
    logger.info('🔄 Sincronizando posts do Notion...');
    const notionPosts = await NotionService.getNotionPosts();
    
    for (const post of notionPosts) {
      const existing = await prisma.post.findUnique({
        where: { slug: post.slug },
      });

      if (existing) {
        await prisma.post.update({
          where: { id: existing.id },
          data: {
            title: post.title,
            excerpt: post.excerpt,
            content: post.content,
            coverImage: post.coverImage,
            tags: post.tags,
            published: post.published,
            featured: post.featured,
            publishedAt: post.publishedAt ? new Date(post.publishedAt) : null,
            updatedAt: new Date(),
          },
        });
        logger.info(`✏️  Atualizado: ${post.title}`);
      } else {
        await prisma.post.create({
          data: {
            id: post.id,
            slug: post.slug,
            title: post.title,
            excerpt: post.excerpt,
            content: post.content,
            coverImage: post.coverImage,
            tags: post.tags,
            published: post.published,
            featured: post.featured,
            publishedAt: post.publishedAt ? new Date(post.publishedAt) : null,
            views: post.views,
            createdAt: new Date(),
            updatedAt: new Date(),
          },
        });
        logger.info(`✨ Criado: ${post.title}`);
      }
    }

    logger.info(`✅ Sync completo: ${notionPosts.length} posts`);
    return { success: true, count: notionPosts.length };
  } catch (error) {
    logger.error('❌ Erro ao sincronizar posts:', error);
    return { success: false, error };
  }
}

export async function syncProjectsFromNotion() {
  try {
    logger.info('🔄 Sincronizando projetos do Notion...');
    const notionProjects = await NotionService.getNotionProjects();
    
    for (const project of notionProjects) {
      const existing = await prisma.project.findUnique({
        where: { slug: project.slug },
      });

      if (existing) {
        await prisma.project.update({
          where: { id: existing.id },
          data: {
            title: project.title,
            description: project.description,
            content: project.content,
            coverImage: project.coverImage,
            images: project.images,
            category: project.category,
            tags: project.tags,
            link: project.link,
            repository: project.repository,
            featured: project.featured,
            updatedAt: new Date(),
          },
        });
        logger.info(`✏️  Atualizado: ${project.title}`);
      } else {
        await prisma.project.create({
          data: {
            id: project.id,
            slug: project.slug,
            title: project.title,
            description: project.description,
            content: project.content,
            coverImage: project.coverImage,
            images: project.images,
            category: project.category,
            tags: project.tags,
            link: project.link,
            repository: project.repository,
            featured: project.featured,
            views: project.views,
            createdAt: new Date(),
            updatedAt: new Date(),
          },
        });
        logger.info(`✨ Criado: ${project.title}`);
      }
    }

    logger.info(`✅ Sync completo: ${notionProjects.length} projetos`);
    return { success: true, count: notionProjects.length };
  } catch (error) {
    logger.error('❌ Erro ao sincronizar projetos:', error);
    return { success: false, error };
  }
}

export async function syncAllFromNotion() {
  const postsResult = await syncPostsFromNotion();
  const projectsResult = await syncProjectsFromNotion();

  return {
    posts: postsResult,
    projects: projectsResult,
  };
}
```

### Passo 4: Adicionar Rota de Sync

**src/routes/sync.ts**

```typescript
import { Hono } from 'hono';
import { syncAllFromNotion } from '$services/SyncService';
import { logger } from '$utils/logger';

const sync = new Hono();

sync.get('/', async (c) => {
  try {
    logger.info('🚀 Sync manual iniciado');
    const result = await syncAllFromNotion();
    return c.json({
      success: true,
      message: 'Sincronização completa',
      data: result,
    });
  } catch (error) {
    logger.error('Erro no sync:', error);
    return c.json({
      success: false,
      error: 'Falha ao sincronizar',
    }, 500);
  }
});

sync.post('/webhook', async (c) => {
  const secret = c.req.header('x-webhook-secret');
  
  if (secret !== process.env.NOTION_WEBHOOK_SECRET) {
    return c.json({ error: 'Unauthorized' }, 401);
  }

  syncAllFromNotion().catch(err => {
    logger.error('Erro ao processar webhook:', err);
  });

  return c.json({ received: true }, 202);
});

export default sync;
```

---

## 🔄 Sincronização de Dados

### Estratégia: Sync Automático + Webhook

```typescript
// Backend
// 1. Sync inicial na startup
// 2. Sync automático a cada X horas
// 3. Webhook do Notion avisa sobre mudanças
// 4. Frontend sempre busca dados atualizados do PostgreSQL
```

### Tabela de Transformação

| Origem (Notion) | Transformação | Destino (PostgreSQL) |
|-----------------|---------------|----------------------|
| `title` (Rich Text) | `extractText()` | `post.title` (VARCHAR) |
| `content` (Block Children) | `getBlockContent()` | `post.content` (TEXT) |
| `tags` (Multi-select) | `extractMultiSelect()` | `post.tags` (Array) |
| `publishedAt` (Date) | `new Date()` | `post.publishedAt` (DateTime) |
| `coverImage` (URL) | Direct | `post.coverImage` (URL) |

---

## 🎨 Frontend - Exibição

### Seu Frontend CONTINUA IGUAL ✅

Porque o frontend busca do PostgreSQL (via `/api/posts`), não do Notion!

---

## 🎨 Tailwind Configuration

### ✅ `tailwind.config.js`

```javascript
export default {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['Fira Code', 'monospace'],
      },
      colors: {
        // 🎨 Cor Principal (Teal #208090)
        primary: {
          DEFAULT: '#208090',
          50: '#f0fcfd',
          100: '#dcf9fb',
          200: '#bdf1f6',
          300: '#8ee3ee',
          400: '#56cbe0',
          500: '#2eaec4',
          600: '#208b9d',
          700: '#208090',      // ← SUA COR BASE
          800: '#1e5f6c',      // Hover (dark)
          900: '#1c4f5b',
          foreground: '#ffffff'
        },

        // 🌑 Cor Secundária (Slate)
        secondary: {
          DEFAULT: '#64748b',
          foreground: '#ffffff',
          light: '#f1f5f9',
          dark: '#1e293b',
        },

        // 🔥 Acento (Amber)
        accent: {
          DEFAULT: '#f59e0b',
          foreground: '#ffffff',
          hover: '#d97706',
        },

        // 🛑 Status
        success: '#10b981',
        warning: '#f59e0b',
        error: '#ef4444',
        info: '#3b82f6',

        // 🖥️ Backgrounds
        background: {
          DEFAULT: '#ffffff',
          dark: '#0f172a',
          alt: '#f8fafc',
        },

        // 🔤 Textos
        text: {
          primary: '#0f172a',
          secondary: '#475569',
          muted: '#94a3b8',
          inverted: '#ffffff',
        },

        // Bordas
        border: {
          DEFAULT: '#e2e8f0',
          dark: '#334155',
        }
      },
      borderRadius: {
        lg: '0.5rem',
        md: 'calc(0.5rem - 2px)',
        sm: 'calc(0.5rem - 4px)',
      },
    },
  },
  plugins: [],
}
```

---

## ✅ Boas Práticas

### 1. Versionamento do Notion Data

```typescript
model Post {
  id String @id @default(cuid())
  notionId String @unique
  notionPageUrl String
  syncedAt DateTime @default(now())
  lastSyncedAt DateTime
  
  @@index([notionId])
}
```

### 2. Tratamento de Erros

```typescript
async function getNotionPostsWithFallback() {
  try {
    return await NotionService.getNotionPosts();
  } catch (error) {
    logger.warn('Notion indisponível, usando cache PostgreSQL');
    return await prisma.post.findMany({
      where: { published: true },
      orderBy: { publishedAt: 'desc' },
    });
  }
}
```

### 3. Logging Detalhado

```typescript
import pino from 'pino';

export const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
});
```

---

## 🚀 Deploy

### Frontend - Vercel

```bash
cd ~/proj/portfolio/frontend
bun run build
# Configurar VITE_API_URL na dashboard
```

### Backend - Cloudflare Workers

```bash
cd ~/proj/portfolio/backend
bunx wrangler deploy
# Adicionar secrets
```

---

## 🐛 Troubleshooting

### "Invalid Notion API Key"

```bash
echo $NOTION_API_KEY  # Deve começar com "secret_"
```

### "Database not found"

```bash
# Confirme que a integração tem acesso
# No Notion: Database → ... → Add connections
```

### "Sync não está funcionando"

```bash
curl http://localhost:3000/api/sync
```

---

## 📞 Checklist de Implementação

- [ ] Criar integração no Notion
- [ ] Copiar API Key e IDs das databases
- [ ] Configurar .env backend
- [ ] Instalar `@notionhq/client`
- [ ] Criar `NotionService.ts`
- [ ] Criar `SyncService.ts`
- [ ] Adicionar rota `/api/sync`
- [ ] Testar sync manual
- [ ] Configurar sync automático
- [ ] Frontend setup completo
- [ ] Tailwind com cores do projeto
- [ ] Deploy backend
- [ ] Deploy frontend
- [ ] Testar frontend com dados Notion

---

**Documentação v2.0 | Notion Integration + Frontend Setup**  
**Stack**: Svelte 5 + Vite 7 (Rolldown) + Tailwind 4 + bits-ui + Hono + Bun + PostgreSQL + Notion
