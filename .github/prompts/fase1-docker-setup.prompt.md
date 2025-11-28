---
description: Phase 1 - Docker setup with Chainguard images (zero CVE)
---

# FASE 1: Docker Setup (Dev & Prod)

## Status: ✅ COMPLETO

Esta fase foi concluída. Todos os Dockerfiles e docker-compose foram criados e otimizados.

---

## ✅ Tarefas Completadas

### 1.1 Backend Docker
- [x] `backend/docker/Dockerfile` - Multi-stage Chainguard Python
- [x] `backend/docker/docker-compose.yml` - Base configuration
- [x] `backend/docker/docker-compose.dev.yml` - Dev com hot reload
- [x] `backend/docker/docker-compose.prod.yml` - Prod com resource limits

### 1.2 Frontend Docker
- [x] `frontend/docker/Dockerfile` - Multi-stage Chainguard Node + Nginx
- [x] `frontend/docker/docker-compose.yml` - Base configuration
- [x] `frontend/docker/docker-compose.dev.yml` - Dev com hot reload
- [x] `frontend/docker/docker-compose.prod.yml` - Prod com resource limits
- [x] `frontend/docker/nginx.chainguard.conf` - Nginx config para Chainguard

### 1.3 Full Stack Compose (Root)
- [x] `docker-compose.dev.yml` - Full stack development
- [x] `docker-compose.prod.yml` - Full stack production

---

## 🔒 Segurança Implementada

- **Chainguard Images** - Zero CVE base images
- **Non-root containers** - Nginx runs on port 8080
- **Resource limits** - CPU/Memory limits em produção
- **Health checks** - Python-based (sem curl/wget)
- **Trusted hosts** - Configurado no FastAPI

---

## 📋 Comandos de Uso

### Desenvolvimento Local
```bash
# Backend apenas
cd backend && docker compose -f docker/docker-compose.dev.yml up --build

# Frontend apenas
cd frontend && docker compose -f docker/docker-compose.dev.yml up --build

# Full Stack
docker compose -f docker-compose.dev.yml up --build
```

### Produção
```bash
# Full Stack Production
docker compose -f docker-compose.prod.yml up -d --build
```

---

## 📁 Estrutura de Arquivos

```
portfolio/
├── docker-compose.dev.yml      # Full stack dev
├── docker-compose.prod.yml     # Full stack prod
├── backend/
│   └── docker/
│       ├── Dockerfile
│       ├── docker-compose.yml
│       ├── docker-compose.dev.yml
│       └── docker-compose.prod.yml
└── frontend/
    └── docker/
        ├── Dockerfile
        ├── docker-compose.yml
        ├── docker-compose.dev.yml
        ├── docker-compose.prod.yml
        └── nginx.chainguard.conf
```

---

## 🔗 Próxima Fase

→ [FASE 2: Page Restructuring](./fase2-page-restructuring.prompt.md)
