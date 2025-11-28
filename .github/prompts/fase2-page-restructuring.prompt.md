---
description: Phase 2 - React Router setup and page structure
---

# FASE 2: Page Restructuring & Routing

## Status: 🔄 EM PROGRESSO

Configuração de React Router, estrutura de páginas e layout base.

---

## ✅ Tarefas Completadas

### 2.1 React Router Setup
- [x] Instalar `react-router-dom`
- [x] Configurar `BrowserRouter` no `main.tsx`
- [x] Criar estrutura de rotas básica

### 2.2 Páginas Criadas
- [x] `pages/Home.tsx` - Landing page principal
- [x] `pages/Status.tsx` - Página de status do sistema
- [x] `pages/Blog.tsx` - Listagem de posts
- [x] `pages/BlogPost.tsx` - Página individual de post

### 2.3 Componentes de Layout
- [x] `components/ThemeToggle.tsx` - Toggle dark/light mode
- [x] `components/HealthModal.tsx` - Modal de saúde do sistema

---

## 🔲 Tarefas Pendentes

### 2.4 Layout Principal
- [ ] Criar `components/layout/Layout.tsx` - Layout wrapper
- [ ] Criar `components/layout/Navbar.tsx` - Navegação principal
- [ ] Criar `components/layout/Footer.tsx` - Footer com links
- [ ] Criar `components/layout/Sidebar.tsx` - Sidebar para mobile

### 2.5 Rotas Adicionais
- [ ] `/about` - Página About/Me detalhada
- [ ] `/projects` - Página de projetos
- [ ] `/contact` - Página de contato
- [ ] `/blog/category/:category` - Filtro por categoria
- [ ] `/blog/tag/:tag` - Filtro por tag

### 2.6 Navegação
- [ ] Smooth scroll para seções na Home
- [ ] Active link highlighting
- [ ] Mobile hamburger menu
- [ ] Breadcrumbs para páginas internas

---

## 📋 Implementação

### Layout.tsx
```typescript
// frontend/src/components/layout/Layout.tsx
import { Layout as AntLayout } from 'antd';
import { Outlet } from 'react-router-dom';
import Navbar from './Navbar';
import Footer from './Footer';

const { Header, Content, Footer: AntFooter } = AntLayout;

export default function Layout() {
  return (
    <AntLayout style={{ minHeight: '100vh' }}>
      <Header>
        <Navbar />
      </Header>
      <Content style={{ padding: '24px 50px' }}>
        <Outlet />
      </Content>
      <AntFooter>
        <Footer />
      </AntFooter>
    </AntLayout>
  );
}
```

### Navbar.tsx
```typescript
// frontend/src/components/layout/Navbar.tsx
import { Menu } from 'antd';
import { Link, useLocation } from 'react-router-dom';
import { HomeOutlined, UserOutlined, ProjectOutlined, 
         ReadOutlined, MailOutlined } from '@ant-design/icons';
import ThemeToggle from '../ThemeToggle';

const menuItems = [
  { key: '/', icon: <HomeOutlined />, label: <Link to="/">Home</Link> },
  { key: '/about', icon: <UserOutlined />, label: <Link to="/about">About</Link> },
  { key: '/projects', icon: <ProjectOutlined />, label: <Link to="/projects">Projects</Link> },
  { key: '/blog', icon: <ReadOutlined />, label: <Link to="/blog">Blog</Link> },
  { key: '/contact', icon: <MailOutlined />, label: <Link to="/contact">Contact</Link> },
];

export default function Navbar() {
  const location = useLocation();
  
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
      <Menu
        mode="horizontal"
        selectedKeys={[location.pathname]}
        items={menuItems}
      />
      <ThemeToggle />
    </div>
  );
}
```

### Estrutura de Rotas Atualizada
```typescript
// frontend/src/App.tsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/layout/Layout';
import Home from './pages/Home';
import About from './pages/About';
import Projects from './pages/Projects';
import Blog from './pages/Blog';
import BlogPost from './pages/BlogPost';
import Contact from './pages/Contact';
import Status from './pages/Status';
import NotFound from './pages/NotFound';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="about" element={<About />} />
          <Route path="projects" element={<Projects />} />
          <Route path="blog" element={<Blog />} />
          <Route path="blog/:slug" element={<BlogPost />} />
          <Route path="contact" element={<Contact />} />
          <Route path="status" element={<Status />} />
          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
```

---

## 🎯 Critérios de Conclusão

- [ ] Todas as rotas funcionando
- [ ] Layout responsivo (mobile/desktop)
- [ ] Navbar com active states
- [ ] Footer com links sociais
- [ ] 404 page customizada
- [ ] Transições de página suaves

---

## 🔗 Navegação entre Fases

← [FASE 1: Docker Setup](./fase1-docker-setup.prompt.md)
→ [FASE 3: Home Page](./fase3-home-page.prompt.md)
