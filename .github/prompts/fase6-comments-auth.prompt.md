---
description: Phase 6 - OAuth authentication and comments system
---

# FASE 6: Comments & Authentication

## Status: 🔲 NÃO INICIADO

Sistema de comentários e autenticação social (OAuth).

---

## 🔲 Tarefas Pendentes

### 6.1 Backend - Authentication
- [ ] Instalar dependências OAuth (`authlib`, `python-jose`)
- [ ] Criar `backend/app/core/security.py` - JWT handling
- [ ] Criar `backend/app/core/oauth.py` - OAuth providers
- [ ] Criar `backend/app/models/user.py` - User model
- [ ] Criar `backend/app/api/auth.py` - Auth endpoints

### 6.2 OAuth Providers
- [ ] GitHub OAuth
- [ ] Google OAuth
- [ ] Discord OAuth (opcional)
- [ ] Callbacks e token handling
- [ ] Session management

### 6.3 Backend - Comments API
- [ ] Criar `backend/app/models/comment.py` - Comment schemas
- [ ] Criar `backend/app/api/comments.py` - CRUD endpoints
- [ ] Endpoints:
  - [ ] GET /posts/{slug}/comments - Listar comentários
  - [ ] POST /posts/{slug}/comments - Criar (auth required)
  - [ ] PUT /comments/{id} - Editar (owner only)
  - [ ] DELETE /comments/{id} - Deletar (owner/admin)
  - [ ] POST /comments/{id}/reply - Responder
- [ ] Moderação básica (flagging)
- [ ] Notificações por email (opcional)

### 6.4 Frontend - Auth
- [ ] Criar `contexts/AuthContext.tsx` - Auth state
- [ ] Criar `hooks/useAuth.ts` - Auth hook
- [ ] Criar `components/auth/LoginModal.tsx` - Login modal
- [ ] Criar `components/auth/UserMenu.tsx` - User dropdown
- [ ] OAuth redirect handling
- [ ] Protected routes

### 6.5 Frontend - Comments
- [ ] Criar `components/blog/CommentSection.tsx` - Container
- [ ] Criar `components/blog/CommentForm.tsx` - Form de comentário
- [ ] Criar `components/blog/CommentCard.tsx` - Card de comentário
- [ ] Criar `components/blog/CommentThread.tsx` - Thread de respostas
- [ ] Reply functionality
- [ ] Edit/Delete buttons
- [ ] Loading states

### 6.6 Alternative: Giscus Integration
- [ ] Configurar Giscus (GitHub Discussions)
- [ ] Criar `components/blog/GiscusComments.tsx`
- [ ] Dark mode sync
- [ ] Language configuration

---

## 📋 Implementação

### User Model (Backend)
```python
# backend/app/models/user.py
from datetime import datetime
from typing import Optional
import uuid
from sqlmodel import Field, SQLModel
from pydantic import ConfigDict

class UserBase(SQLModel):
    """Base user model."""
    email: str = Field(unique=True, index=True)
    name: str = Field(max_length=100)
    avatar_url: Optional[str] = Field(default=None)
    provider: str = Field(description="OAuth provider: github, google, discord")
    provider_id: str = Field(description="Provider user ID")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "name": "John Doe",
                "avatar_url": "https://avatars.githubusercontent.com/u/123",
                "provider": "github",
                "provider_id": "12345",
            }
        }
    )

class User(UserBase, table=True):
    """Database model for users."""
    __tablename__ = "users"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: datetime = Field(default_factory=datetime.utcnow)
    is_admin: bool = Field(default=False)
    is_banned: bool = Field(default=False)

class UserPublic(SQLModel):
    """Public user data (safe to expose)."""
    id: uuid.UUID
    name: str
    avatar_url: Optional[str]
    created_at: datetime
```

### Comment Model (Backend)
```python
# backend/app/models/comment.py
from datetime import datetime
from typing import Optional
import uuid
from sqlmodel import Field, SQLModel, Relationship
from pydantic import ConfigDict

class CommentBase(SQLModel):
    """Base comment model."""
    content: str = Field(min_length=1, max_length=2000)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "content": "Great article! Thanks for sharing.",
            }
        }
    )

class Comment(CommentBase, table=True):
    """Database model for comments."""
    __tablename__ = "comments"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    post_id: uuid.UUID = Field(foreign_key="posts.id", index=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    parent_id: Optional[uuid.UUID] = Field(default=None, foreign_key="comments.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_deleted: bool = Field(default=False)
    is_flagged: bool = Field(default=False)

class CommentCreate(CommentBase):
    parent_id: Optional[uuid.UUID] = None

class CommentUpdate(SQLModel):
    content: str = Field(min_length=1, max_length=2000)

class CommentPublic(CommentBase):
    id: uuid.UUID
    user_id: uuid.UUID
    parent_id: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime
    # Include user data
    user_name: str
    user_avatar: Optional[str]
    replies: list["CommentPublic"] = []
```

### Auth Context (Frontend)
```typescript
// frontend/src/contexts/AuthContext.tsx
import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User } from '../types';
import { getMe, logout as apiLogout } from '../services/api';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (provider: 'github' | 'google') => void;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check if user is authenticated on mount
    const checkAuth = async () => {
      try {
        const userData = await getMe();
        setUser(userData);
      } catch {
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    };
    checkAuth();
  }, []);

  const login = (provider: 'github' | 'google') => {
    // Redirect to OAuth provider
    window.location.href = `/api/auth/${provider}/login`;
  };

  const logout = async () => {
    await apiLogout();
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
```

### Login Modal (Frontend)
```typescript
// frontend/src/components/auth/LoginModal.tsx
import { Modal, Button, Space, Typography, Divider } from 'antd';
import { GithubOutlined, GoogleOutlined } from '@ant-design/icons';
import { useAuth } from '../../contexts/AuthContext';

interface LoginModalProps {
  open: boolean;
  onClose: () => void;
}

export default function LoginModal({ open, onClose }: LoginModalProps) {
  const { login } = useAuth();

  return (
    <Modal
      title="Sign in to comment"
      open={open}
      onCancel={onClose}
      footer={null}
      centered
    >
      <Typography.Paragraph>
        Sign in with your social account to leave comments and reactions.
      </Typography.Paragraph>
      
      <Space direction="vertical" style={{ width: '100%' }}>
        <Button
          icon={<GithubOutlined />}
          size="large"
          block
          onClick={() => login('github')}
        >
          Continue with GitHub
        </Button>
        
        <Button
          icon={<GoogleOutlined />}
          size="large"
          block
          onClick={() => login('google')}
        >
          Continue with Google
        </Button>
      </Space>
      
      <Divider />
      
      <Typography.Text type="secondary">
        We only use your public profile information. 
        You can delete your account at any time.
      </Typography.Text>
    </Modal>
  );
}
```

### Comment Section (Frontend)
```typescript
// frontend/src/components/blog/CommentSection.tsx
import { useState } from 'react';
import { Typography, Empty, Spin, Button } from 'antd';
import { useQuery } from '@tanstack/react-query';
import { useAuth } from '../../contexts/AuthContext';
import CommentForm from './CommentForm';
import CommentCard from './CommentCard';
import LoginModal from '../auth/LoginModal';
import { fetchComments } from '../../services/api';

interface CommentSectionProps {
  postSlug: string;
}

export default function CommentSection({ postSlug }: CommentSectionProps) {
  const { isAuthenticated } = useAuth();
  const [showLogin, setShowLogin] = useState(false);

  const { data: comments, isLoading } = useQuery({
    queryKey: ['comments', postSlug],
    queryFn: () => fetchComments(postSlug),
  });

  return (
    <div style={{ marginTop: 48 }}>
      <Typography.Title level={3}>
        Comments ({comments?.length || 0})
      </Typography.Title>

      {/* Comment Form */}
      {isAuthenticated ? (
        <CommentForm postSlug={postSlug} />
      ) : (
        <Button type="primary" onClick={() => setShowLogin(true)}>
          Sign in to comment
        </Button>
      )}

      {/* Comments List */}
      <div style={{ marginTop: 24 }}>
        {isLoading ? (
          <Spin />
        ) : comments?.length === 0 ? (
          <Empty description="No comments yet. Be the first!" />
        ) : (
          comments?.map((comment) => (
            <CommentCard
              key={comment.id}
              comment={comment}
              postSlug={postSlug}
            />
          ))
        )}
      </div>

      <LoginModal open={showLogin} onClose={() => setShowLogin(false)} />
    </div>
  );
}
```

### Giscus Alternative
```typescript
// frontend/src/components/blog/GiscusComments.tsx
import { useEffect, useRef } from 'react';
import { useTheme } from '../../contexts/ThemeContext';

interface GiscusCommentsProps {
  postSlug: string;
}

export default function GiscusComments({ postSlug }: GiscusCommentsProps) {
  const { isDark } = useTheme();
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const script = document.createElement('script');
    script.src = 'https://giscus.app/client.js';
    script.setAttribute('data-repo', 'oornnery/portfolio');
    script.setAttribute('data-repo-id', 'YOUR_REPO_ID');
    script.setAttribute('data-category', 'Comments');
    script.setAttribute('data-category-id', 'YOUR_CATEGORY_ID');
    script.setAttribute('data-mapping', 'specific');
    script.setAttribute('data-term', postSlug);
    script.setAttribute('data-strict', '0');
    script.setAttribute('data-reactions-enabled', '1');
    script.setAttribute('data-emit-metadata', '0');
    script.setAttribute('data-input-position', 'top');
    script.setAttribute('data-theme', isDark ? 'dark' : 'light');
    script.setAttribute('data-lang', 'en');
    script.setAttribute('crossorigin', 'anonymous');
    script.async = true;

    containerRef.current?.appendChild(script);

    return () => {
      const iframe = containerRef.current?.querySelector('iframe');
      iframe?.remove();
    };
  }, [postSlug, isDark]);

  return <div ref={containerRef} />;
}
```

---

## 📦 Dependências Necessárias

### Backend
```bash
cd backend
uv add authlib python-jose[cryptography] httpx
```

### Frontend
```bash
# Já incluído no TanStack Query e Ant Design
```

---

## 🎯 Critérios de Conclusão

- [ ] OAuth com GitHub funcionando
- [ ] OAuth com Google funcionando
- [ ] User model e sessões
- [ ] Comments API completo
- [ ] Comment form funcional
- [ ] Reply threads
- [ ] Edit/Delete próprios comentários
- [ ] Login modal
- [ ] User dropdown menu
- [ ] Protected routes

---

## 🔗 Navegação entre Fases

← [FASE 5: Blog System](./fase5-blog-system.prompt.md)
→ [FASE 7: Security & Performance](./fase7-security-performance.prompt.md)
