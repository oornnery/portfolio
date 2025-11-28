---
description: Phase 7 - Security hardening and performance optimization
---

# FASE 7: Security & Performance

## Status: 🔄 EM PROGRESSO

Hardening de segurança e otimização de performance.

---

## ✅ Tarefas Completadas

### 7.1 Backend Security
- [x] Rate limiting global (slowapi) - 100 req/min
- [x] Rate limiting por endpoint (read: 60/min, write: 10/min)
- [x] SecurityHeadersMiddleware (X-Content-Type-Options, X-Frame-Options, etc.)
- [x] CORS configurado
- [x] TrustedHostMiddleware
- [x] Request logging

### 7.2 Docker Security
- [x] Chainguard images (zero CVE)
- [x] Non-root containers
- [x] Resource limits em produção
- [x] Health checks

---

## 🔲 Tarefas Pendentes

### 7.3 Backend Security Adicional
- [ ] Content Security Policy (CSP) header
- [ ] CSRF protection para forms
- [ ] Input sanitization com `bleach`
- [ ] SQL injection prevention (já coberto pelo SQLModel)
- [ ] XSS protection adicional
- [ ] Secure cookie settings
- [ ] API key authentication para admin endpoints

### 7.4 OSINT Prevention
- [ ] Remover metadados de imagens (EXIF)
- [ ] Ofuscar emails (usar formulário)
- [ ] Limitar informações de localização
- [ ] Logs sem dados sensíveis
- [ ] Rate limiting em formulários de contato
- [ ] CAPTCHA ou honeypot

### 7.5 Frontend Security
- [ ] Sanitização de markdown/HTML
- [ ] CSP meta tags
- [ ] Subresource Integrity (SRI)
- [ ] Secure referrer policy
- [ ] No sensitive data in localStorage

### 7.6 Performance - Backend
- [ ] Query optimization (indexes)
- [ ] Response caching (Redis)
- [ ] Database connection pooling
- [ ] Async background tasks (celery/arq)
- [ ] Compression middleware (gzip/brotli)

### 7.7 Performance - Frontend
- [ ] Code splitting (já nativo no Vite)
- [ ] Lazy loading de componentes
- [ ] Image optimization
- [ ] Service Worker / PWA básico
- [ ] Preload critical assets
- [ ] Bundle size analysis

### 7.8 Monitoring & Logging
- [ ] Structured logging (JSON)
- [ ] Error tracking (Sentry)
- [ ] Performance monitoring
- [ ] Uptime monitoring
- [ ] Log rotation

---

## 📋 Implementação

### Content Security Policy
```python
# backend/app/main.py - Adicionar ao SecurityHeadersMiddleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Existing headers...
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Content Security Policy
        csp = "; ".join([
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' https://giscus.app",
            "style-src 'self' 'unsafe-inline'",
            "img-src 'self' data: https: blob:",
            "font-src 'self' data:",
            "connect-src 'self' https://api.github.com",
            "frame-src https://giscus.app",
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'",
        ])
        response.headers["Content-Security-Policy"] = csp
        
        # HSTS (only in production with HTTPS)
        if settings.ENV == "production":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )
        
        return response
```

### Input Sanitization
```python
# backend/app/utils/sanitize.py
import bleach

ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'ul', 'ol', 'li', 'blockquote', 'code', 'pre', 'a', 'img',
]

ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'rel'],
    'img': ['src', 'alt', 'title'],
    'code': ['class'],
    'pre': ['class'],
}

def sanitize_html(content: str) -> str:
    """Sanitize HTML content to prevent XSS."""
    return bleach.clean(
        content,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True,
    )

def sanitize_markdown(content: str) -> str:
    """Sanitize markdown content (minimal sanitization)."""
    # Remove potentially dangerous patterns
    import re
    
    # Remove javascript: URLs
    content = re.sub(r'javascript:', '', content, flags=re.IGNORECASE)
    
    # Remove on* event handlers
    content = re.sub(r'\s+on\w+\s*=', ' ', content, flags=re.IGNORECASE)
    
    return content
```

### CSRF Protection
```python
# backend/app/core/csrf.py
import secrets
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

class CSRFMiddleware(BaseHTTPMiddleware):
    """CSRF protection for form submissions."""
    
    async def dispatch(self, request: Request, call_next):
        # Skip for safe methods
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return await call_next(request)
        
        # Skip for API calls with proper auth
        if request.headers.get("Authorization"):
            return await call_next(request)
        
        # Check CSRF token for form submissions
        csrf_cookie = request.cookies.get("csrf_token")
        csrf_header = request.headers.get("X-CSRF-Token")
        
        if not csrf_cookie or csrf_cookie != csrf_header:
            raise HTTPException(status_code=403, detail="CSRF validation failed")
        
        return await call_next(request)

def generate_csrf_token() -> str:
    """Generate a new CSRF token."""
    return secrets.token_urlsafe(32)
```

### Honeypot Anti-Spam
```typescript
// frontend/src/components/common/HoneypotField.tsx
import { Form, Input } from 'antd';

/**
 * Honeypot field for spam prevention.
 * This field should be hidden and left empty by real users.
 * Bots will typically fill it in.
 */
export default function HoneypotField() {
  return (
    <Form.Item
      name="website" // Attractive name for bots
      rules={[
        {
          validator: (_, value) => {
            if (value) {
              return Promise.reject('Spam detected');
            }
            return Promise.resolve();
          },
        },
      ]}
      style={{
        position: 'absolute',
        left: '-9999px',
        opacity: 0,
        height: 0,
        overflow: 'hidden',
      }}
      aria-hidden="true"
      tabIndex={-1}
    >
      <Input tabIndex={-1} autoComplete="off" />
    </Form.Item>
  );
}
```

### Image Optimization
```typescript
// frontend/src/components/common/OptimizedImage.tsx
import { useState } from 'react';
import { Skeleton } from 'antd';

interface OptimizedImageProps {
  src: string;
  alt: string;
  width?: number;
  height?: number;
  className?: string;
}

export default function OptimizedImage({
  src,
  alt,
  width,
  height,
  className,
}: OptimizedImageProps) {
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState(false);

  return (
    <div style={{ position: 'relative', width, height }}>
      {!loaded && !error && (
        <Skeleton.Image active style={{ width, height }} />
      )}
      <img
        src={src}
        alt={alt}
        width={width}
        height={height}
        className={className}
        loading="lazy"
        decoding="async"
        onLoad={() => setLoaded(true)}
        onError={() => setError(true)}
        style={{
          opacity: loaded ? 1 : 0,
          transition: 'opacity 0.3s',
        }}
      />
    </div>
  );
}
```

### Lazy Loading Routes
```typescript
// frontend/src/App.tsx - Com lazy loading
import { lazy, Suspense } from 'react';
import { Spin } from 'antd';

// Lazy load pages
const Home = lazy(() => import('./pages/Home'));
const Blog = lazy(() => import('./pages/Blog'));
const BlogPost = lazy(() => import('./pages/BlogPost'));
const Projects = lazy(() => import('./pages/Projects'));
const About = lazy(() => import('./pages/About'));
const Contact = lazy(() => import('./pages/Contact'));

function PageLoader() {
  return (
    <div style={{ display: 'flex', justifyContent: 'center', padding: 100 }}>
      <Spin size="large" />
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Suspense fallback={<PageLoader />}>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Home />} />
            <Route path="blog" element={<Blog />} />
            <Route path="blog/:slug" element={<BlogPost />} />
            {/* ... */}
          </Route>
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}
```

### Response Caching (Redis)
```python
# backend/app/core/cache.py
import json
from typing import Optional
import redis.asyncio as redis
from app.config import settings

class Cache:
    def __init__(self):
        self.redis: Optional[redis.Redis] = None
    
    async def connect(self):
        if settings.REDIS_URL:
            self.redis = redis.from_url(settings.REDIS_URL)
    
    async def disconnect(self):
        if self.redis:
            await self.redis.close()
    
    async def get(self, key: str) -> Optional[dict]:
        if not self.redis:
            return None
        value = await self.redis.get(key)
        return json.loads(value) if value else None
    
    async def set(self, key: str, value: dict, ttl: int = 300):
        if self.redis:
            await self.redis.setex(key, ttl, json.dumps(value))
    
    async def delete(self, key: str):
        if self.redis:
            await self.redis.delete(key)
    
    async def invalidate_pattern(self, pattern: str):
        if self.redis:
            async for key in self.redis.scan_iter(match=pattern):
                await self.redis.delete(key)

cache = Cache()
```

---

## 📦 Dependências Necessárias

### Backend
```bash
cd backend
uv add bleach redis
```

---

## 🎯 Critérios de Conclusão

- [x] Rate limiting implementado
- [x] Security headers básicos
- [x] Docker security (Chainguard)
- [ ] CSP header completo
- [ ] Input sanitization
- [ ] CSRF protection
- [ ] Honeypot anti-spam
- [ ] Image optimization
- [ ] Lazy loading
- [ ] Response caching
- [ ] Error tracking (Sentry)

---

## 🔗 Navegação entre Fases

← [FASE 6: Comments & Auth](./fase6-comments-auth.prompt.md)
→ [FASE 8: Deploy & CI/CD](./fase8-deploy-cicd.prompt.md)
