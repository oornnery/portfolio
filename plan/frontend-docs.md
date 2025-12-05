# 📚 Documentação Completa: Frontend + Notion Integration

**Data**: Dezembro 2025  
**Stack**: Svelte 5 + Vite 7 (Rolldown) + Tailwind 4 + bits-ui + Hono + PostgreSQL + Notion  
**Status**: ✅ Pronto para Produção

---

## 📋 Índice

1. [Setup Completo](#setup-completo)
2. [Tailwind Configuration](#tailwind-configuration)
3. [Componentes UI](#componentes-ui)
4. [Estrutura de Pastas](#estrutura-de-pastas)
5. [Services & Stores](#services--stores)
6. [Páginas Dinâmicas](#páginas-dinâmicas)
7. [Integração Backend](#integração-backend)
8. [Notion Sync](#notion-sync)
9. [Deploy](#deploy)
10. [Troubleshooting](#troubleshooting)

---

## 🚀 Setup Completo

### Passo 1: Dependências

```bash
cd ~/proj/portfolio/frontend

# Instalar bits-ui e utilitários
bun add bits-ui clsx tailwind-merge

# Verificar instaladas
bun ls | grep -E "vite|svelte|tailwindcss|lucide"
```

### Passo 2: Estrutura de Pastas

```bash
mkdir -p src/lib/{components/{ui,layout,blog},services,stores,utils}
touch src/lib/utils/cn.ts
touch src/lib/services/api.ts
touch src/lib/stores/posts.ts
touch src/lib/stores/projects.ts
touch tailwind.config.js
touch src/app.css
touch .env.local
```

### Passo 3: Arquivos Essenciais

#### ✅ `src/lib/utils/cn.ts`

```typescript
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

---

## 🎨 Tailwind Configuration

### ✅ `tailwind.config.js`

```javascript
/** @type {import('tailwindcss').Config} */
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
        // 🎨 Cor Principal (Teal)
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

### ✅ `src/app.css`

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    color-scheme: light;
  }

  html.dark {
    color-scheme: dark;
  }

  body {
    @apply bg-background text-text-primary;
  }

  a {
    @apply text-primary hover:underline;
  }

  button {
    @apply transition-all duration-200;
  }
}

@layer components {
  .btn {
    @apply inline-flex items-center justify-center px-4 py-2 rounded-md font-medium transition-colors;
  }

  .btn-primary {
    @apply bg-primary text-primary-foreground hover:bg-primary-800;
  }

  .btn-secondary {
    @apply bg-secondary text-secondary-foreground hover:bg-secondary-600;
  }

  .btn-outline {
    @apply border border-border text-text-primary hover:bg-background-alt;
  }

  .card {
    @apply bg-white dark:bg-secondary-dark border border-border dark:border-border-dark rounded-lg shadow-sm;
  }

  .badge {
    @apply inline-block px-2 py-1 text-xs rounded-full;
  }

  .badge-primary {
    @apply bg-primary-100 text-primary-900 dark:bg-primary-900 dark:text-primary-100;
  }
}

/* Smooth scrolling */
html {
  scroll-behavior: smooth;
}

/* Focus visible para acessibilidade */
:focus-visible {
  outline: 2px solid var(--primary-color);
  outline-offset: 2px;
}
```

---

## 🧩 Componentes UI

### ✅ `src/lib/components/ui/button.svelte`

```svelte
<script lang="ts">
  import { cn } from '$lib/utils/cn';

  interface Props {
    variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
    size?: 'sm' | 'md' | 'lg';
    disabled?: boolean;
    href?: string;
    class?: string;
  }

  let {
    variant = 'primary',
    size = 'md',
    disabled = false,
    href,
    class: customClass = '',
    ...props
  } = $props<Props>();

  const baseClasses = 'inline-flex items-center justify-center font-medium transition-colors rounded-md focus-visible:outline-2 focus-visible:outline-offset-2 disabled:opacity-50 disabled:cursor-not-allowed';

  const variantClasses = {
    primary: 'bg-primary text-primary-foreground hover:bg-primary-800',
    secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary-600',
    outline: 'border border-border text-text-primary hover:bg-background-alt',
    ghost: 'text-text-primary hover:bg-background-alt',
  };

  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  };

  const buttonClass = cn(
    baseClasses,
    variantClasses[variant],
    sizeClasses[size],
    customClass
  );
</script>

{#if href}
  <a {href} class={buttonClass} {...props}>
    <slot />
  </a>
{:else}
  <button {disabled} class={buttonClass} {...props}>
    <slot />
  </button>
{/if}

<style>
  :global(a) {
    text-decoration: none;
  }
</style>
```

### ✅ `src/lib/components/ui/card.svelte`

```svelte
<script lang="ts">
  import { cn } from '$lib/utils/cn';

  interface Props {
    class?: string;
  }

  let { class: customClass = '' } = $props<Props>();
</script>

<div
  class={cn(
    'bg-white dark:bg-secondary-dark border border-border dark:border-border-dark rounded-lg shadow-sm hover:shadow-md transition-shadow',
    customClass
  )}
  {...$$restProps}
>
  <slot />
</div>
```

### ✅ `src/lib/components/ui/index.ts`

```typescript
export { default as Button } from './button.svelte';
export { default as Card } from './card.svelte';
```

---

## 📁 Estrutura de Pastas

```
frontend/
├── src/
│   ├── lib/
│   │   ├── components/
│   │   │   ├── ui/
│   │   │   │   ├── button.svelte
│   │   │   │   ├── card.svelte
│   │   │   │   └── index.ts
│   │   │   ├── layout/
│   │   │   │   ├── Header.svelte
│   │   │   │   ├── Footer.svelte
│   │   │   │   └── Navigation.svelte
│   │   │   └── blog/
│   │   │       ├── PostCard.svelte
│   │   │       ├── PostGrid.svelte
│   │   │       └── ProjectCard.svelte
│   │   ├── services/
│   │   │   └── api.ts
│   │   ├── stores/
│   │   │   ├── posts.ts
│   │   │   └── projects.ts
│   │   └── utils/
│   │       └── cn.ts
│   ├── routes/
│   │   ├── +layout.svelte
│   │   ├── +page.svelte
│   │   ├── blog/
│   │   │   ├── +page.svelte
│   │   │   └── [slug]/
│   │   │       └── +page.svelte
│   │   └── portfolio/
│   │       ├── +page.svelte
│   │       └── [slug]/
│   │           └── +page.svelte
│   ├── app.css
│   ├── app.html
│   └── app.ts
├── vite.config.ts
├── tailwind.config.js
├── tsconfig.json
├── svelte.config.js
├── .env.local
├── package.json
└── bun.lockb
```

---

## 🔗 Services & Stores

### ✅ `src/lib/services/api.ts`

```typescript
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:3000';

export interface Post {
  id: string;
  slug: string;
  title: string;
  excerpt: string;
  content?: string;
  coverImage?: string;
  tags: string[];
  published: boolean;
  featured: boolean;
  publishedAt?: string;
  views: number;
}

export interface Project {
  id: string;
  slug: string;
  title: string;
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

async function fetchAPI<T>(endpoint: string): Promise<T> {
  try {
    const res = await fetch(`${API_URL}${endpoint}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  } catch (error) {
    console.error(`API Error: ${endpoint}`, error);
    throw error;
  }
}

export const postsAPI = {
  async getAll(params?: { page?: number; tag?: string }) {
    const query = new URLSearchParams();
    if (params?.page) query.append('page', String(params.page));
    if (params?.tag) query.append('tag', params.tag);
    return fetchAPI<Post[]>(`/api/posts${query.toString() ? '?' + query : ''}`);
  },

  async getBySlug(slug: string) {
    return fetchAPI<Post>(`/api/posts/${slug}`);
  },

  async getFeatured() {
    return fetchAPI<Post[]>('/api/posts/featured');
  },
};

export const projectsAPI = {
  async getAll(params?: { category?: string }) {
    const query = new URLSearchParams();
    if (params?.category) query.append('category', params.category);
    return fetchAPI<Project[]>(`/api/projects${query.toString() ? '?' + query : ''}`);
  },

  async getBySlug(slug: string) {
    return fetchAPI<Project>(`/api/projects/${slug}`);
  },

  async getFeatured() {
    return fetchAPI<Project[]>('/api/projects/featured');
  },
};
```

### ✅ `src/lib/stores/posts.ts`

```typescript
import { writable } from 'svelte/store';
import { postsAPI, type Post } from '$lib/services/api';

export const posts = writable<Post[]>([]);
export const loading = writable(false);
export const error = writable<string | null>(null);

export async function loadPosts() {
  loading.set(true);
  error.set(null);
  try {
    const data = await postsAPI.getAll();
    posts.set(data);
  } catch (err) {
    error.set(err instanceof Error ? err.message : 'Erro desconhecido');
  } finally {
    loading.set(false);
  }
}

export async function loadFeaturedPosts() {
  try {
    return await postsAPI.getFeatured();
  } catch (err) {
    console.error('Erro ao carregar posts em destaque:', err);
    return [];
  }
}
```

### ✅ `src/lib/stores/projects.ts`

```typescript
import { writable } from 'svelte/store';
import { projectsAPI, type Project } from '$lib/services/api';

export const projects = writable<Project[]>([]);
export const loading = writable(false);
export const error = writable<string | null>(null);

export async function loadProjects() {
  loading.set(true);
  error.set(null);
  try {
    const data = await projectsAPI.getAll();
    projects.set(data);
  } catch (err) {
    error.set(err instanceof Error ? err.message : 'Erro desconhecido');
  } finally {
    loading.set(false);
  }
}

export async function loadFeaturedProjects() {
  try {
    return await projectsAPI.getFeatured();
  } catch (err) {
    console.error('Erro ao carregar projetos:', err);
    return [];
  }
}
```

---

## 📄 Páginas Dinâmicas

### ✅ `src/routes/+layout.svelte`

```svelte
<script>
  import '../app.css';
</script>

<slot />
```

### ✅ `src/routes/+page.svelte` (Home)

```svelte
<script lang="ts">
  import { onMount } from 'svelte';
  import { loadFeaturedPosts } from '$lib/stores/posts';
  import { projectsAPI } from '$lib/services/api';
  import { Button, Card } from '$lib/components/ui';

  let featuredPosts: any[] = $state([]);
  let featuredProjects: any[] = $state([]);
  let loading = $state(true);

  onMount(async () => {
    try {
      [featuredPosts, featuredProjects] = await Promise.all([
        loadFeaturedPosts(),
        projectsAPI.getFeatured(),
      ]);
    } finally {
      loading = false;
    }
  });
</script>

<svelte:head>
  <title>Seu Portfolio</title>
  <meta name="description" content="Bem-vindo ao meu portfolio" />
</svelte:head>

<main class="min-h-screen">
  <!-- Hero Section -->
  <section class="py-20 px-4 bg-gradient-to-r from-primary to-primary-800 text-white">
    <div class="max-w-4xl mx-auto text-center">
      <h1 class="text-5xl font-bold mb-6">Bem-vindo!</h1>
      <p class="text-xl mb-8 opacity-90">
        Desenvolvedor full-stack apaixonado por criar experiências digitais incríveis.
      </p>
      <div class="flex gap-4 justify-center flex-wrap">
        <Button href="/blog" class="btn-primary">Ver Blog</Button>
        <Button href="/portfolio" variant="outline" class="border-white text-white hover:bg-white/10">
          Ver Projetos
        </Button>
      </div>
    </div>
  </section>

  <!-- Posts em Destaque -->
  <section class="py-16 px-4">
    <div class="max-w-6xl mx-auto">
      <h2 class="text-4xl font-bold mb-12">Posts Recentes</h2>

      {#if loading}
        <p class="text-center text-text-secondary">Carregando...</p>
      {:else if featuredPosts.length > 0}
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {#each featuredPosts.slice(0, 3) as post}
            <a href={`/blog/${post.slug}`} class="no-underline">
              <Card class="h-full flex flex-col">
                {#if post.coverImage}
                  <img src={post.coverImage} alt={post.title} class="w-full h-48 object-cover" />
                {/if}
                <div class="p-6 flex-1 flex flex-col">
                  <h3 class="font-bold text-xl mb-2">{post.title}</h3>
                  <p class="text-text-secondary text-sm mb-4 flex-1">{post.excerpt}</p>
                  <div class="text-xs text-text-muted">
                    {post.publishedAt ? new Date(post.publishedAt).toLocaleDateString('pt-BR') : ''}
                  </div>
                </div>
              </Card>
            </a>
          {/each}
        </div>
        <div class="text-center">
          <Button href="/blog" variant="ghost">Ver todos os posts →</Button>
        </div>
      {:else}
        <p class="text-center text-text-secondary">Nenhum post encontrado</p>
      {/if}
    </div>
  </section>

  <!-- Projetos em Destaque -->
  <section class="py-16 px-4 bg-background-alt">
    <div class="max-w-6xl mx-auto">
      <h2 class="text-4xl font-bold mb-12">Projetos em Destaque</h2>

      {#if loading}
        <p class="text-center text-text-secondary">Carregando...</p>
      {:else if featuredProjects.length > 0}
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          {#each featuredProjects.slice(0, 4) as project}
            <a href={`/portfolio/${project.slug}`} class="no-underline">
              <Card class="h-full">
                <img src={project.coverImage} alt={project.title} class="w-full h-48 object-cover" />
                <div class="p-6">
                  <span class="badge badge-primary">{project.category}</span>
                  <h3 class="font-bold text-xl mt-2 mb-2">{project.title}</h3>
                  <p class="text-text-secondary text-sm">{project.description}</p>
                </div>
              </Card>
            </a>
          {/each}
        </div>
        <div class="text-center">
          <Button href="/portfolio" variant="ghost">Ver todos os projetos →</Button>
        </div>
      {:else}
        <p class="text-center text-text-secondary">Nenhum projeto encontrado</p>
      {/if}
    </div>
  </section>
</main>

<style>
  :global(a.no-underline) {
    text-decoration: none;
    color: inherit;
  }
</style>
```

---

## 🔄 Integração Backend

### ✅ `.env.local` (Frontend)

```env
VITE_API_URL=http://localhost:3000
```

### ✅ Fluxo de Dados

```
┌─────────────────────┐
│   NOTION DATABASE   │
└──────────┬──────────┘
           │ (Sync automático)
           ↓
┌─────────────────────┐
│  Backend (Hono)     │
│  /api/posts         │
│  /api/projects      │
│  /api/sync          │
└──────────┬──────────┘
           │ (Fetch via VITE_API_URL)
           ↓
┌─────────────────────┐
│ Frontend (Svelte)   │
│ Renderiza com Dados │
└─────────────────────┘
```

---

## 📋 Notion Sync

### Backend: Rotas de Sync

```typescript
// src/routes/sync.ts
import { Hono } from 'hono';
import { syncAllFromNotion } from '$services/SyncService';

const sync = new Hono();

sync.get('/', async (c) => {
  const result = await syncAllFromNotion();
  return c.json({ success: true, data: result });
});

sync.post('/webhook', async (c) => {
  // Validar webhook secret
  syncAllFromNotion().catch(console.error);
  return c.json({ received: true }, 202);
});

export default sync;
```

### Manual Sync

```bash
# Terminal 1: Backend
cd ~/proj/portfolio/backend
bun --watch run src/index.ts

# Terminal 2: Trigger sync
curl http://localhost:3000/api/sync

# Resultado: Posts e Projetos importados do Notion
```

---

## 🚀 Deploy

### Frontend - Vercel

```bash
cd ~/proj/portfolio/frontend

# Build com Rolldown
bun run build

# Deploy automático no git push
# Configurar VITE_API_URL na dashboard Vercel
```

### Backend - Cloudflare Workers

```bash
cd ~/proj/portfolio/backend

# Configurar wrangler.toml
# Adicionar secrets: NOTION_API_KEY, DATABASE_URL

bunx wrangler deploy
```

---

## 🐛 Troubleshooting

### "Cannot connect to API"

**Solução:**

```bash
# 1. Verificar backend
curl http://localhost:3000/api/posts

# 2. Verificar VITE_API_URL
cat .env.local

# 3. Logs do frontend
# F12 → Console → Verificar erros de fetch
```

### "Posts não aparecem"

**Checklist:**

- [ ] Backend rodando (`http://localhost:3000`)
- [ ] `/api/sync` foi chamado?
- [ ] PostgreSQL com dados?
- [ ] VITE_API_URL correto?

### "Tailwind classes não funcionam"

**Solução:**

```bash
# 1. Verificar tailwind.config.js
# 2. Verificar src/app.css importado
# 3. Limpar node_modules
rm -rf node_modules
bun install
bun run dev
```

---

## ✅ Checklist Final

- [ ] Frontend setup completo
- [ ] Tailwind com cores do projeto
- [ ] Componentes UI funcionando
- [ ] Backend sync ativo
- [ ] Pages dinâmicas criadas
- [ ] API conectada
- [ ] Dev server rodando
- [ ] Deploy planejado

---

**Documentação v2.0 | Complete Setup**  
**Stack**: Svelte 5 + Vite 7 + Rolldown + Tailwind 4 + Hono + PostgreSQL + Notion
