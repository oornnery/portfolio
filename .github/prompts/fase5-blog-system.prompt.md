---
description: Phase 5 - Full blog system with FastAPI backend and React frontend
---

# FASE 5: Blog System

## Status: 🔄 EM PROGRESSO

Sistema de blog completo com backend API e frontend.

---

## ✅ Tarefas Completadas

### 5.1 Backend - Blog API
- [x] `backend/app/models/blog.py` - SQLModel schemas completos
  - [x] Post, PostCreate, PostUpdate, PostPublic, PostDetail
  - [x] Reaction, ReactionCreate, ReactionPublic
  - [x] CategoryCount, TagCount
  - [x] ErrorResponse, SuccessResponse
- [x] `backend/app/api/blog.py` - Endpoints CRUD completos
  - [x] GET /posts - Listagem com filtros
  - [x] GET /posts/{slug} - Post por slug (incrementa views)
  - [x] POST /posts - Criar post
  - [x] PUT /posts/{slug} - Atualizar post
  - [x] DELETE /posts/{slug} - Deletar post
  - [x] GET /posts/{slug}/reactions - Obter reações
  - [x] POST /posts/{slug}/react - Adicionar reação
  - [x] GET /categories - Listar categorias
  - [x] GET /tags - Listar tags
  - [x] GET /stats - Estatísticas do blog
- [x] Rate limiting configurado (slowapi)

### 5.2 Frontend - Blog Pages
- [x] `pages/Blog.tsx` - Página de listagem
- [x] `pages/BlogPost.tsx` - Página individual

### 5.3 Frontend - Blog Components
- [x] `components/blog/PostCard.tsx` - Card de post
- [x] `components/blog/CodeBlock.tsx` - Syntax highlighting
- [x] `components/blog/Callout.tsx` - Callouts estilizados
- [x] `components/blog/ReadingProgress.tsx` - Barra de progresso

---

## 🔲 Tarefas Pendentes

### 5.4 Blog Frontend Melhorias
- [ ] Criar `components/blog/PostFilters.tsx` - Filtros avançados
- [ ] Criar `components/blog/PostMeta.tsx` - Metadados do post
- [ ] Criar `components/blog/TableOfContents.tsx` - TOC lateral
- [ ] Criar `components/blog/ShareButtons.tsx` - Compartilhamento
- [ ] Criar `components/blog/RelatedPosts.tsx` - Posts relacionados
- [ ] Criar `components/blog/AuthorCard.tsx` - Card do autor

### 5.5 Blog Listing Page Melhorias
- [ ] Search com debounce
- [ ] Filtro por categoria
- [ ] Filtro por tag
- [ ] Filtro por idioma
- [ ] Infinite scroll ou paginação
- [ ] View toggle (grid/list)
- [ ] Skeleton loading

### 5.6 Blog Post Page Melhorias
- [ ] Table of Contents lateral
- [ ] Reading progress bar (já existe)
- [ ] Estimated reading time
- [ ] Copy code button
- [ ] Anchor links para headings
- [ ] Print-friendly styles
- [ ] Social share buttons

### 5.7 Markdown Rendering Melhorias
- [ ] Syntax highlighting com tema Tokyo Night
- [ ] Copy button em code blocks
- [ ] Imagens com zoom
- [ ] Tables responsivos
- [ ] Footnotes support
- [ ] Math/LaTeX support (opcional)

### 5.8 Reactions System (Frontend)
- [ ] Criar `components/blog/ReactionBar.tsx`
- [ ] UI de reações estilo GitHub/Discord
- [ ] Animação ao reagir
- [ ] Contador em tempo real
- [ ] Persistência local (evitar spam)

### 5.9 Backend - Markdown Service
- [ ] Criar `backend/app/services/markdown_service.py`
- [ ] Parse de frontmatter
- [ ] Cálculo de reading time
- [ ] Extração de headings para TOC
- [ ] Sanitização de HTML

---

## 📋 Implementação

### TableOfContents Component
```typescript
// frontend/src/components/blog/TableOfContents.tsx
import { Anchor, Typography } from 'antd';
import { useEffect, useState } from 'react';

interface Heading {
  id: string;
  text: string;
  level: number;
}

interface TableOfContentsProps {
  content: string;
}

export default function TableOfContents({ content }: TableOfContentsProps) {
  const [headings, setHeadings] = useState<Heading[]>([]);

  useEffect(() => {
    // Parse headings from markdown
    const regex = /^(#{1,3})\s+(.+)$/gm;
    const matches: Heading[] = [];
    let match;

    while ((match = regex.exec(content)) !== null) {
      const level = match[1].length;
      const text = match[2];
      const id = text.toLowerCase().replace(/[^a-z0-9]+/g, '-');
      matches.push({ id, text, level });
    }

    setHeadings(matches);
  }, [content]);

  if (headings.length === 0) return null;

  return (
    <div style={{ position: 'sticky', top: 80 }}>
      <Typography.Title level={5}>Table of Contents</Typography.Title>
      <Anchor
        items={headings.map((h) => ({
          key: h.id,
          href: `#${h.id}`,
          title: h.text,
          // Indent based on level
          style: { paddingLeft: (h.level - 1) * 16 },
        }))}
      />
    </div>
  );
}
```

### ReactionBar Component
```typescript
// frontend/src/components/blog/ReactionBar.tsx
import { Button, Space, Tooltip, message } from 'antd';
import { motion, AnimatePresence } from 'framer-motion';
import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { addReaction } from '../../services/api';

const REACTIONS = [
  { type: 'like', emoji: '👍', label: 'Like' },
  { type: 'love', emoji: '❤️', label: 'Love' },
  { type: 'fire', emoji: '🔥', label: 'Fire' },
  { type: 'clap', emoji: '👏', label: 'Clap' },
  { type: 'thinking', emoji: '🤔', label: 'Thinking' },
  { type: 'rocket', emoji: '🚀', label: 'Rocket' },
];

interface ReactionBarProps {
  postSlug: string;
  reactions: Record<string, number>;
}

export default function ReactionBar({ postSlug, reactions }: ReactionBarProps) {
  const [reacted, setReacted] = useState<Set<string>>(new Set());
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: (type: string) => addReaction(postSlug, type),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['post', postSlug] });
    },
  });

  const handleReact = (type: string) => {
    if (reacted.has(type)) {
      message.info('You already reacted with this!');
      return;
    }
    
    setReacted((prev) => new Set([...prev, type]));
    mutation.mutate(type);
  };

  return (
    <Space wrap>
      {REACTIONS.map((reaction) => (
        <Tooltip key={reaction.type} title={reaction.label}>
          <motion.div whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.95 }}>
            <Button
              shape="round"
              onClick={() => handleReact(reaction.type)}
              disabled={reacted.has(reaction.type)}
              style={{
                opacity: reacted.has(reaction.type) ? 0.7 : 1,
              }}
            >
              <AnimatePresence mode="wait">
                <motion.span
                  key={reactions[reaction.type] || 0}
                  initial={{ y: -10, opacity: 0 }}
                  animate={{ y: 0, opacity: 1 }}
                  exit={{ y: 10, opacity: 0 }}
                >
                  {reaction.emoji} {reactions[reaction.type] || 0}
                </motion.span>
              </AnimatePresence>
            </Button>
          </motion.div>
        </Tooltip>
      ))}
    </Space>
  );
}
```

### ShareButtons Component
```typescript
// frontend/src/components/blog/ShareButtons.tsx
import { Button, Space, Tooltip, message } from 'antd';
import { TwitterOutlined, LinkedinOutlined, LinkOutlined } from '@ant-design/icons';

interface ShareButtonsProps {
  title: string;
  url: string;
}

export default function ShareButtons({ title, url }: ShareButtonsProps) {
  const encodedTitle = encodeURIComponent(title);
  const encodedUrl = encodeURIComponent(url);

  const copyLink = async () => {
    await navigator.clipboard.writeText(url);
    message.success('Link copied to clipboard!');
  };

  return (
    <Space>
      <Tooltip title="Share on Twitter">
        <Button
          icon={<TwitterOutlined />}
          href={`https://twitter.com/intent/tweet?text=${encodedTitle}&url=${encodedUrl}`}
          target="_blank"
        />
      </Tooltip>
      <Tooltip title="Share on LinkedIn">
        <Button
          icon={<LinkedinOutlined />}
          href={`https://www.linkedin.com/sharing/share-offsite/?url=${encodedUrl}`}
          target="_blank"
        />
      </Tooltip>
      <Tooltip title="Copy link">
        <Button icon={<LinkOutlined />} onClick={copyLink} />
      </Tooltip>
    </Space>
  );
}
```

### Markdown Service (Backend)
```python
# backend/app/services/markdown_service.py
import re
from typing import Optional

def calculate_reading_time(content: str, wpm: int = 200) -> int:
    """Calculate estimated reading time in minutes."""
    words = len(content.split())
    return max(1, round(words / wpm))

def extract_headings(content: str) -> list[dict]:
    """Extract headings for table of contents."""
    pattern = r'^(#{1,6})\s+(.+)$'
    headings = []
    
    for match in re.finditer(pattern, content, re.MULTILINE):
        level = len(match.group(1))
        text = match.group(2)
        slug = re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')
        headings.append({
            'level': level,
            'text': text,
            'slug': slug,
        })
    
    return headings

def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Parse YAML frontmatter from markdown content."""
    if not content.startswith('---'):
        return {}, content
    
    try:
        _, frontmatter, body = content.split('---', 2)
        import yaml
        metadata = yaml.safe_load(frontmatter)
        return metadata or {}, body.strip()
    except Exception:
        return {}, content

def add_heading_ids(content: str) -> str:
    """Add IDs to headings for anchor links."""
    def replace_heading(match):
        hashes = match.group(1)
        text = match.group(2)
        slug = re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')
        return f'{hashes} <a id="{slug}"></a>{text}'
    
    pattern = r'^(#{1,6})\s+(.+)$'
    return re.sub(pattern, replace_heading, content, flags=re.MULTILINE)
```

---

## 🎯 Critérios de Conclusão

- [x] Backend API de blog completo
- [x] Blog listing page funcional
- [x] Blog post page com markdown
- [x] Syntax highlighting
- [ ] Table of Contents lateral
- [ ] Reactions funcionando
- [ ] Share buttons
- [ ] Filtros avançados
- [ ] Skeleton loading
- [ ] Related posts

---

## 🔗 Navegação entre Fases

← [FASE 4: Projects Page](./fase4-projects-page.prompt.md)
→ [FASE 6: Comments & Auth](./fase6-comments-auth.prompt.md)
