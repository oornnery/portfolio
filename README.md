# 🚀 Fabio.dev Portfolio

Um portfolio pessoal moderno construído com SolidStart, focado em performance, acessibilidade e experiência de usuário refinada.

![SolidJS](https://img.shields.io/badge/SolidJS-1.9.5-blue?logo=solid)
![TypeScript](https://img.shields.io/badge/TypeScript-5.9-blue?logo=typescript)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4-blue?logo=tailwindcss)
![License](https://img.shields.io/badge/License-MIT-green)

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Tecnologias](#tecnologias)
- [Arquitetura](#arquitetura)
- [Estrutura de Pastas](#estrutura-de-pastas)
- [Funcionalidades Implementadas](#funcionalidades-implementadas)
- [Como Executar](#como-executar)
- [Scripts Disponíveis](#scripts-disponíveis)
- [O Que Falta Implementar](#o-que-falta-implementar)
- [Melhorias Sugeridas](#melhorias-sugeridas)
- [Considerações de Segurança](#considerações-de-segurança)
- [Contribuição](#contribuição)

---

## 🎯 Visão Geral

Este projeto é um portfolio profissional com suporte a:

- **Internacionalização (i18n)** - Inglês e Português
- **Tema Dark/Light** - Com preferência persistida
- **Skeleton Loading** - UX aprimorada durante carregamento
- **Rotas em Inglês** - URLs SEO-friendly
- **Design Responsivo** - Mobile-first approach

---

## 🛠 Tecnologias

### Core

| Tecnologia                                    | Versão | Descrição                                     |
| --------------------------------------------- | ------ | --------------------------------------------- |
| [SolidJS](https://www.solidjs.com/)           | 1.9.5  | Framework reativo com fine-grained reactivity |
| [SolidStart](https://start.solidjs.com/)      | 1.1.0  | Meta-framework para SSR/SSG                   |
| [Vinxi](https://vinxi.vercel.app/)            | 0.5.7  | Build tool universal                          |
| [TypeScript](https://www.typescriptlang.org/) | 5.9.3  | Tipagem estática                              |

### Estilização

| Tecnologia                                      | Versão  | Descrição                   |
| ----------------------------------------------- | ------- | --------------------------- |
| [TailwindCSS](https://tailwindcss.com/)         | 3.4.14  | Utility-first CSS framework |
| [PostCSS](https://postcss.org/)                 | 8.5.6   | Processador CSS             |
| [Autoprefixer](https://autoprefixer.github.io/) | 10.4.23 | Vendor prefixes automáticos |

### Ícones & UI

| Tecnologia                          | Versão  | Descrição            |
| ----------------------------------- | ------- | -------------------- |
| [Lucide Solid](https://lucide.dev/) | 0.562.0 | Biblioteca de ícones |

### Desenvolvimento

| Tecnologia                                                                      | Versão | Descrição                                         |
| ------------------------------------------------------------------------------- | ------ | ------------------------------------------------- |
| [ESLint](https://eslint.org/)                                                   | 9.39.2 | Linter JavaScript/TypeScript                      |
| [eslint-plugin-solid](https://github.com/solidjs-community/eslint-plugin-solid) | 0.14.5 | Regras ESLint para SolidJS                        |
| [Prettier](https://prettier.io/)                                                | -      | Formatação de código (via eslint-config-prettier) |

### Runtime

- **Node.js** >= 22
- **Bun** (recomendado) ou npm/yarn

---

## 🏗 Arquitetura

### Padrões Utilizados

#### Atomic Design

Os componentes seguem a metodologia Atomic Design:
```
atoms/       → Componentes básicos (Button, Input, Skeleton, Tag)
molecules/   → Combinações de atoms (ContentCard, ContactSection)
organisms/   → Seções completas (NavBar, ListView, DetailView)
layouts/     → Templates de página (SiteLayout)
```

#### State Management

```bash
stores/
├── content.tsx  → Provider de dados do portfolio (Context API)
├── i18n.ts      → Internacionalização (Signal global)
└── theme.ts     → Tema dark/light (Signal global)
```

#### Data Flow

```bash
┌─────────────────────────────────────────────────────────────┐
│                        App.tsx                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                  PortfolioProvider                       │ │
│  │   ┌──────────────────────────────────────────────────┐  │ │
│  │   │  createSignal + createEffect                      │  │ │
│  │   │  (fetches data based on lang signal)              │  │ │
│  │   └──────────────────────────────────────────────────┘  │ │
│  │                         │                               │ │
│  │   ┌─────────────────────▼──────────────────────────┐   │ │
│  │   │              Routes (pages)                     │   │ │
│  │   │   usePortfolio() → data, loading, refetch      │   │ │
│  │   └─────────────────────────────────────────────────┘   │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Estrutura de Pastas

```bash
src/
├── app.css                 # Estilos globais (Tailwind)
├── app.tsx                 # Componente raiz + GlobalSkeleton
├── entry-client.tsx        # Entry point client-side
├── entry-server.tsx        # Entry point SSR (dark mode default)
├── global.d.ts             # Declarações TypeScript globais
│
├── components/
│   ├── atoms/
│   │   ├── Button.tsx      # Botão com variantes
│   │   ├── Input.tsx       # Campo de input
│   │   ├── Skeleton.tsx    # Loading skeleton animado
│   │   ├── SocialLinks.tsx # Links sociais com ícones
│   │   ├── Tag.tsx         # Tag/badge
│   │   └── TextArea.tsx    # Campo textarea
│   │
│   ├── molecules/
│   │   ├── ContactSection.tsx   # Formulário de contato
│   │   ├── ContentCard.tsx      # Card de conteúdo genérico
│   │   └── TimelineItem.tsx     # Item de timeline
│   │
│   ├── organisms/
│   │   ├── DetailView.tsx  # Visualização detalhada
│   │   ├── ListView.tsx    # Lista de items
│   │   ├── NavBar.tsx      # Barra de navegação
│   │   └── Sidebar.tsx     # Sidebar
│   │
│   └── layouts/
│       └── SiteLayout.tsx  # Layout principal
│
├── data/
│   ├── mock-api.ts         # Dados mockados + fetch simulado
│   └── ui-config.ts        # Textos da UI (i18n)
│
├── routes/
│   ├── index.tsx           # Home (/)
│   ├── about.tsx           # Sobre (/about)
│   ├── contact.tsx         # Contato (/contact)
│   ├── [...404].tsx        # Página 404
│   │
│   ├── blog/
│   │   ├── index.tsx       # Lista de posts (/blog)
│   │   └── [slug].tsx      # Post individual (/blog/:slug)
│   │
│   ├── projects/
│   │   ├── index.tsx       # Lista de projetos (/projects)
│   │   └── [id].tsx        # Projeto individual (/projects/:id)
│   │
│   └── projetos/           # Rotas em português (redirect)
│       ├── index.tsx
│       └── [id].tsx
│
├── stores/
│   ├── content.tsx         # Context Provider de dados
│   ├── i18n.ts             # Signal de idioma
│   └── theme.ts            # Signal de tema
│
└── types/
    └── portfolio.ts        # Tipos TypeScript
```

---

## ✅ Funcionalidades Implementadas

### Core

- [x] **SolidStart com Vinxi** - Build e dev server
- [x] **SSR configurado** - Entry server/client separados
- [x] **Roteamento** - File-based routing com @solidjs/router
- [x] **TypeScript** - Tipagem completa dos dados

### UI/UX

- [x] **Skeleton Loading** - Feedback visual durante carregamento
- [x] **Dark Mode por padrão** - Classe `dark` no HTML inicial
- [x] **Toggle de tema** - Alternância dark/light
- [x] **Design responsivo** - Mobile-first com breakpoints
- [x] **Animações** - CSS transitions e Tailwind animate

### Internacionalização

- [x] **i18n EN/PT** - Troca de idioma em tempo real
- [x] **Rotas em inglês** - /projects, /blog, /about, /contact
- [x] **Textos da UI** - Botões, labels, navegação traduzidos
- [x] **Conteúdo traduzido** - Profile, posts, projetos

### Componentes

- [x] **NavBar** - Navegação com links ativos
- [x] **Footer** - Copyright e links sociais
- [x] **Hero Section** - Apresentação com avatar
- [x] **Cards de conteúdo** - Posts e projetos
- [x] **Formulário de contato** - Inputs estilizados
- [x] **Social Links** - GitHub, LinkedIn, Twitter, WhatsApp, Email

### Dados

- [x] **Mock API** - Dados simulados com delay
- [x] **Tipos TypeScript** - PortfolioData, Profile, Project, Post
- [x] **Context Provider** - Estado global reativo

---

## 🚀 Como Executar

### Pré-requisitos

- Node.js >= 22
- Bun (recomendado) ou npm

### Instalação

```bash
# Clone o repositório
git clone https://github.com/oornnery/portfolio.git
cd portfolio

# Instale as dependências
bun install
# ou
npm install

# Execute em desenvolvimento
bun run dev
# ou
npm run dev
```

### Acesse

```bash
http://localhost:3000
```

---

## 📜 Scripts Disponíveis

| Script  | Comando                      | Descrição                          |
| ------- | ---------------------------- | ---------------------------------- |
| `dev`   | `vinxi dev`                  | Inicia servidor de desenvolvimento |
| `build` | `vinxi build`                | Build para produção                |
| `start` | `vinxi start`                | Inicia servidor de produção        |
| `lint`  | `eslint "src/**/*.{ts,tsx}"` | Executa linting                    |

---

## 📝 O Que Falta Implementar

### Alta Prioridade

- [ ] **API Real** - Substituir mock-api por backend real
- [ ] **Formulário de contato funcional** - Integração com email service
- [ ] **SEO** - Meta tags dinâmicas por página
- [ ] **Sitemap.xml** - Geração automática
- [ ] **Analytics** - Google Analytics ou Plausible

### Média Prioridade

- [ ] **Blog com MDX** - Suporte a markdown para posts
- [ ] **CMS Integration** - Notion, Contentful ou Sanity
- [ ] **RSS Feed** - Para posts do blog
- [ ] **Busca** - Search nos posts e projetos
- [ ] **Paginação** - Para listas longas
- [ ] **Lazy loading de imagens** - Otimização de performance

### Baixa Prioridade

- [ ] **PWA** - Service worker e manifest
- [ ] **Testes** - Vitest + Testing Library
- [ ] **Storybook** - Documentação de componentes
- [ ] **CI/CD** - GitHub Actions
- [ ] **Docker** - Containerização

---

## 💡 Melhorias Sugeridas

### Performance

1. **Preload de rotas** - Usar `preload` do @solidjs/router
2. **Image optimization** - Implementar `<Picture>` component
3. **Font subsetting** - Carregar apenas caracteres usados
4. **Bundle analysis** - Identificar dependências pesadas
5. **Cache headers** - Configurar cache adequado no deploy

### UX/UI

1. **Animações de transição** - Entre rotas com View Transitions API
2. **Scroll progress** - Indicador de progresso em posts
3. **Table of contents** - Para posts longos
4. **Back to top** - Botão flutuante
5. **Breadcrumbs** - Navegação contextual
6. **404 personalizado** - Página de erro mais amigável

### Acessibilidade

1. **Skip links** - Pular para conteúdo principal
2. **Focus management** - Foco visível e lógico
3. **ARIA labels** - Em elementos interativos
4. **Reduced motion** - Respeitar preferência do usuário
5. **Color contrast** - Verificar WCAG AA/AAA

### Código

1. **Remover @ts-nocheck** - Resolver tipos corretamente
2. **Error boundaries** - Tratamento de erros React-like
3. **Loading states** - Estados de loading granulares por seção
4. **Refetch on focus** - Revalidar dados quando tab fica ativa
5. **Optimistic updates** - Para formulário de contato

---

## 🔒 Considerações de Segurança

### ⚠️ Vulnerabilidades Atuais

#### 1. Links Externos Inseguros

```tsx
// PROBLEMA: Links externos sem proteção
<a href={link.url} target="_blank">
  
// SOLUÇÃO: Adicionar rel="noopener noreferrer"
<a href={link.url} target="_blank" rel="noopener noreferrer">
```

#### 2. Dados Sensíveis no Código

```typescript
// PROBLEMA: Email e telefone expostos no mock-api.ts
email: 'fabio@example.com',
phone: '+55 11 99999-9999',

// SOLUÇÃO: Mover para variáveis de ambiente
email: import.meta.env.VITE_CONTACT_EMAIL,
```

#### 3. Formulário de Contato

```tsx
// TODO: Implementar
// - Validação server-side
// - Rate limiting
// - CAPTCHA (reCAPTCHA ou hCaptcha)
// - Sanitização de inputs
// - CSRF token
```

### ✅ Práticas Recomendadas

#### Headers de Segurança

Adicionar no servidor/CDN:
```
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), microphone=(), camera=()
```

#### Variáveis de Ambiente

```bash
# .env.example
VITE_API_URL=https://api.example.com
VITE_CONTACT_EMAIL=contact@example.com
VITE_GA_ID=G-XXXXXXXXXX
```

#### Sanitização de Dados

```typescript
// Usar biblioteca como DOMPurify para conteúdo dinâmico
import DOMPurify from 'dompurify';
const safeHTML = DOMPurify.sanitize(userContent);
```

#### Validação de Inputs

```typescript
// Usar Zod ou Valibot para validação
import { z } from 'zod';

const ContactSchema = z.object({
  name: z.string().min(2).max(100),
  email: z.string().email(),
  message: z.string().min(10).max(1000),
});
```

### 🛡️ Checklist de Segurança

- [ ] Adicionar `rel="noopener noreferrer"` em links externos
- [ ] Mover dados sensíveis para variáveis de ambiente
- [ ] Implementar validação de formulário (client + server)
- [ ] Adicionar rate limiting no formulário de contato
- [ ] Configurar CSP headers
- [ ] Implementar CAPTCHA
- [ ] Sanitizar conteúdo dinâmico
- [ ] Auditar dependências (`npm audit` / `bun audit`)
- [ ] Configurar HTTPS obrigatório
- [ ] Implementar logging de erros (Sentry)

---

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'feat: adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

<p align="center">
  Feito com 💜 por <a href="https://github.com/oornnery">Fabio Souza</a>
</p>
