---
description: Phase 4 - Projects showcase with filters and GitHub integration
---

# FASE 4: Projects/Portfolio Page

## Status: 🔲 NÃO INICIADO

Showcase de projetos com grid, filtros e página de detalhes.

---

## 🔲 Tarefas Pendentes

### 4.1 Backend - Projects API
- [ ] Criar `backend/app/models/project.py` - SQLModel schemas
- [ ] Criar `backend/app/api/projects.py` - CRUD endpoints
- [ ] Modelo com campos: title, description, image, tech_stack, github_url, demo_url, featured
- [ ] Endpoints: GET /projects, GET /projects/:slug, POST/PUT/DELETE (admin)

### 4.2 Frontend - Projects Page
- [ ] Criar `pages/Projects.tsx` - Página de listagem
- [ ] Criar `pages/ProjectDetail.tsx` - Página de detalhes
- [ ] Criar `components/projects/ProjectCard.tsx` - Card de projeto
- [ ] Criar `components/projects/ProjectGrid.tsx` - Grid responsivo
- [ ] Criar `components/projects/ProjectFilters.tsx` - Filtros por tech

### 4.3 Projects Grid
- [ ] Grid responsivo (1/2/3 colunas)
- [ ] Hover effects com preview
- [ ] Skeleton loading
- [ ] Infinite scroll ou paginação
- [ ] Featured projects destacados

### 4.4 Project Card
- [ ] Imagem de capa com lazy loading
- [ ] Tags de tecnologias
- [ ] Links GitHub e Demo
- [ ] Estatísticas (stars, forks)
- [ ] Hover effect com descrição

### 4.5 Project Detail Page
- [ ] Galeria de imagens/screenshots
- [ ] Stack tecnológica visual
- [ ] Descrição completa (markdown)
- [ ] Links para repositório e demo
- [ ] Métricas do GitHub
- [ ] Seção de challenges/learnings
- [ ] Projetos relacionados

### 4.6 Filtros e Busca
- [ ] Filtro por tecnologia
- [ ] Filtro por categoria
- [ ] Search bar funcional
- [ ] Ordenação (recentes, populares)
- [ ] Clear filters button

---

## 📋 Implementação

### Project Model (Backend)
```python
# backend/app/models/project.py
from datetime import datetime
from typing import Optional
import uuid
from sqlmodel import Field, SQLModel, Column, JSON
from pydantic import ConfigDict

class ProjectBase(SQLModel):
    """Base model for projects."""
    title: str = Field(min_length=1, max_length=200)
    slug: str = Field(unique=True, index=True, min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=500)
    content: str = Field(default="", description="Full markdown content")
    image: Optional[str] = Field(default=None)
    tech_stack: list[str] = Field(default=[], sa_column=Column(JSON))
    category: str = Field(default="other")
    github_url: Optional[str] = Field(default=None)
    demo_url: Optional[str] = Field(default=None)
    featured: bool = Field(default=False)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Portfolio Website",
                "slug": "portfolio-website",
                "description": "Full-stack portfolio with FastAPI and React",
                "tech_stack": ["FastAPI", "React", "TypeScript", "PostgreSQL"],
                "category": "web",
                "github_url": "https://github.com/user/portfolio",
                "demo_url": "https://portfolio.example.com",
                "featured": True,
            }
        }
    )

class Project(ProjectBase, table=True):
    """Database model for projects."""
    __tablename__ = "projects"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    github_stars: int = Field(default=0, ge=0)
    github_forks: int = Field(default=0, ge=0)

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    image: Optional[str] = None
    tech_stack: Optional[list[str]] = None
    category: Optional[str] = None
    github_url: Optional[str] = None
    demo_url: Optional[str] = None
    featured: Optional[bool] = None

class ProjectPublic(ProjectBase):
    id: uuid.UUID
    created_at: datetime
    github_stars: int
    github_forks: int
```

### Projects API (Backend)
```python
# backend/app/api/projects.py
from fastapi import APIRouter, HTTPException, Query, Request
from sqlmodel import select
from app.db import get_session
from app.models.project import (
    Project, ProjectCreate, ProjectUpdate, ProjectPublic
)

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.get("", response_model=list[ProjectPublic])
async def list_projects(
    request: Request,
    category: str | None = None,
    tech: str | None = None,
    featured: bool | None = None,
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
):
    """List all projects with optional filters."""
    async for session in get_session():
        query = select(Project)
        
        if category:
            query = query.where(Project.category == category)
        if featured is not None:
            query = query.where(Project.featured == featured)
        if tech:
            query = query.where(Project.tech_stack.contains([tech]))
        
        query = query.offset(offset).limit(limit)
        result = await session.execute(query)
        return result.scalars().all()

@router.get("/{slug}", response_model=ProjectPublic)
async def get_project(slug: str):
    """Get a single project by slug."""
    async for session in get_session():
        query = select(Project).where(Project.slug == slug)
        result = await session.execute(query)
        project = result.scalar_one_or_none()
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return project
```

### ProjectCard Component
```typescript
// frontend/src/components/projects/ProjectCard.tsx
import { Card, Tag, Space, Button, Typography } from 'antd';
import { GithubOutlined, LinkOutlined, StarOutlined, ForkOutlined } from '@ant-design/icons';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';

interface ProjectCardProps {
  project: {
    slug: string;
    title: string;
    description: string;
    image?: string;
    tech_stack: string[];
    github_url?: string;
    demo_url?: string;
    github_stars: number;
    github_forks: number;
    featured: boolean;
  };
}

export default function ProjectCard({ project }: ProjectCardProps) {
  return (
    <motion.div
      whileHover={{ y: -5 }}
      transition={{ duration: 0.2 }}
    >
      <Card
        hoverable
        cover={
          project.image && (
            <img
              alt={project.title}
              src={project.image}
              style={{ height: 200, objectFit: 'cover' }}
            />
          )
        }
        actions={[
          project.github_url && (
            <a href={project.github_url} target="_blank" rel="noopener">
              <GithubOutlined /> GitHub
            </a>
          ),
          project.demo_url && (
            <a href={project.demo_url} target="_blank" rel="noopener">
              <LinkOutlined /> Demo
            </a>
          ),
        ].filter(Boolean)}
      >
        <Card.Meta
          title={
            <Link to={`/projects/${project.slug}`}>
              {project.title}
              {project.featured && <Tag color="gold" style={{ marginLeft: 8 }}>Featured</Tag>}
            </Link>
          }
          description={project.description}
        />
        <div style={{ marginTop: 16 }}>
          <Space wrap>
            {project.tech_stack.slice(0, 4).map((tech) => (
              <Tag key={tech} color="blue">{tech}</Tag>
            ))}
            {project.tech_stack.length > 4 && (
              <Tag>+{project.tech_stack.length - 4}</Tag>
            )}
          </Space>
        </div>
        <div style={{ marginTop: 12, color: '#888' }}>
          <Space>
            <span><StarOutlined /> {project.github_stars}</span>
            <span><ForkOutlined /> {project.github_forks}</span>
          </Space>
        </div>
      </Card>
    </motion.div>
  );
}
```

### Projects Page
```typescript
// frontend/src/pages/Projects.tsx
import { useState } from 'react';
import { Row, Col, Input, Select, Typography, Spin, Empty } from 'antd';
import { useQuery } from '@tanstack/react-query';
import ProjectCard from '../components/projects/ProjectCard';
import { fetchProjects } from '../services/api';

const { Search } = Input;
const { Title } = Typography;

const techOptions = [
  'React', 'TypeScript', 'Python', 'FastAPI', 'PostgreSQL', 
  'Docker', 'Node.js', 'Next.js'
];

const categoryOptions = [
  { value: 'web', label: 'Web App' },
  { value: 'api', label: 'API/Backend' },
  { value: 'cli', label: 'CLI Tool' },
  { value: 'other', label: 'Other' },
];

export default function Projects() {
  const [filters, setFilters] = useState({
    search: '',
    category: null,
    tech: null,
  });

  const { data: projects, isLoading } = useQuery({
    queryKey: ['projects', filters],
    queryFn: () => fetchProjects(filters),
  });

  return (
    <div style={{ padding: '24px 0' }}>
      <Title level={2}>Projects</Title>
      
      {/* Filters */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col xs={24} md={8}>
          <Search
            placeholder="Search projects..."
            onSearch={(value) => setFilters(f => ({ ...f, search: value }))}
          />
        </Col>
        <Col xs={12} md={4}>
          <Select
            placeholder="Category"
            allowClear
            style={{ width: '100%' }}
            options={categoryOptions}
            onChange={(value) => setFilters(f => ({ ...f, category: value }))}
          />
        </Col>
        <Col xs={12} md={4}>
          <Select
            placeholder="Technology"
            allowClear
            style={{ width: '100%' }}
            options={techOptions.map(t => ({ value: t, label: t }))}
            onChange={(value) => setFilters(f => ({ ...f, tech: value }))}
          />
        </Col>
      </Row>

      {/* Projects Grid */}
      {isLoading ? (
        <Spin size="large" />
      ) : projects?.length === 0 ? (
        <Empty description="No projects found" />
      ) : (
        <Row gutter={[24, 24]}>
          {projects?.map((project) => (
            <Col xs={24} sm={12} lg={8} key={project.slug}>
              <ProjectCard project={project} />
            </Col>
          ))}
        </Row>
      )}
    </div>
  );
}
```

---

## 🎯 Critérios de Conclusão

- [ ] Backend API de projetos funcionando
- [ ] Grid de projetos responsivo
- [ ] Filtros e busca funcionando
- [ ] Cards com hover effects
- [ ] Página de detalhes completa
- [ ] Integração com GitHub API (stars/forks)
- [ ] Skeleton loading implementado
- [ ] Featured projects destacados

---

## 🔗 Navegação entre Fases

← [FASE 3: Home Page](./fase3-home-page.prompt.md)
→ [FASE 5: Blog System](./fase5-blog-system.prompt.md)
