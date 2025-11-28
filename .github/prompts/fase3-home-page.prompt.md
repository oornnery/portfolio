---
description: Phase 3 - Home page components (Hero, About, Skills, Experience)
---

# FASE 3: Home Page (Portfolio Landing)

## Status: 🔄 EM PROGRESSO

Página inicial do portfolio com Hero, About, Experience e Contact sections.

---

## ✅ Tarefas Completadas

### 3.1 Componentes Home Criados
- [x] `components/home/Hero.tsx` - Hero section
- [x] `components/home/About.tsx` - About section
- [x] `components/home/Experience.tsx` - Experience timeline
- [x] `components/home/Contact.tsx` - Contact section
- [x] `pages/Home.tsx` - Página principal

---

## 🔲 Tarefas Pendentes

### 3.2 Hero Section Melhorias
- [ ] Animação de typing effect (nome/título)
- [ ] Background animado (partículas ou gradiente)
- [ ] CTA buttons com hover effects
- [ ] Avatar/foto com efeito de hover
- [ ] Social links animados

### 3.3 About Section Melhorias
- [ ] Skills com progress bars animadas
- [ ] Tech stack icons grid
- [ ] Fun facts carousel/slider
- [ ] Download CV button
- [ ] GitHub stats integration

### 3.4 Experience Section Melhorias
- [ ] Timeline vertical com animações scroll reveal
- [ ] Cards de experiência com expand/collapse
- [ ] Filtros por tipo (trabalho, freelance, estudos)
- [ ] Modal com detalhes completos
- [ ] Ícones de empresas/logos

### 3.5 Skills Section (Nova)
- [ ] Criar `components/home/Skills.tsx`
- [ ] Grid de skills com ícones
- [ ] Categorias (Frontend, Backend, DevOps, Tools)
- [ ] Animação de entrada
- [ ] Hover effects nos cards

### 3.6 Education Section (Nova)
- [ ] Criar `components/home/Education.tsx`
- [ ] Cards de formação acadêmica
- [ ] Certificações com badges
- [ ] Links para verificação
- [ ] Timeline ou grid layout

### 3.7 Contact Section Melhorias
- [ ] Formulário com validação
- [ ] Integração com backend (endpoint de email)
- [ ] Honeypot para anti-spam
- [ ] Rate limiting visual
- [ ] Social links grid
- [ ] Calendly/Cal.com integration

### 3.8 Animações Globais
- [ ] Scroll reveal (elementos aparecem ao scrollar)
- [ ] Parallax backgrounds
- [ ] Smooth scroll navigation
- [ ] Page transitions

---

## 📋 Implementação

### Hero com Typing Effect
```typescript
// components/home/Hero.tsx - Adicionar typing
import { TypeAnimation } from 'react-type-animation';

const Hero = () => {
  return (
    <section className="hero">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Avatar size={120} src="/avatar.jpg" />
        <h1>
          <TypeAnimation
            sequence={[
              'Full Stack Developer',
              2000,
              'Python Enthusiast',
              2000,
              'DevOps Engineer',
              2000,
            ]}
            repeat={Infinity}
          />
        </h1>
        <Space>
          <Button type="primary" size="large">
            View Projects
          </Button>
          <Button size="large">
            Download CV
          </Button>
        </Space>
      </motion.div>
    </section>
  );
};
```

### Skills Grid
```typescript
// components/home/Skills.tsx
import { Card, Row, Col, Progress, Tag } from 'antd';
import { motion } from 'framer-motion';

const skillCategories = [
  {
    title: 'Frontend',
    skills: [
      { name: 'React', level: 90, icon: '⚛️' },
      { name: 'TypeScript', level: 85, icon: '📘' },
      { name: 'Ant Design', level: 80, icon: '🐜' },
    ],
  },
  {
    title: 'Backend',
    skills: [
      { name: 'Python', level: 95, icon: '🐍' },
      { name: 'FastAPI', level: 90, icon: '⚡' },
      { name: 'PostgreSQL', level: 80, icon: '🐘' },
    ],
  },
  {
    title: 'DevOps',
    skills: [
      { name: 'Docker', level: 85, icon: '🐳' },
      { name: 'GitHub Actions', level: 75, icon: '🔄' },
      { name: 'Linux', level: 80, icon: '🐧' },
    ],
  },
];

export default function Skills() {
  return (
    <section id="skills">
      <Typography.Title level={2}>Skills & Technologies</Typography.Title>
      <Row gutter={[24, 24]}>
        {skillCategories.map((category, index) => (
          <Col xs={24} md={8} key={category.title}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <Card title={category.title}>
                {category.skills.map((skill) => (
                  <div key={skill.name} style={{ marginBottom: 16 }}>
                    <span>{skill.icon} {skill.name}</span>
                    <Progress percent={skill.level} strokeColor="#7aa2f7" />
                  </div>
                ))}
              </Card>
            </motion.div>
          </Col>
        ))}
      </Row>
    </section>
  );
}
```

### Scroll-based Navigation
```typescript
// hooks/useScrollSpy.ts
import { useState, useEffect } from 'react';

export function useScrollSpy(sectionIds: string[]) {
  const [activeSection, setActiveSection] = useState('');

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setActiveSection(entry.target.id);
          }
        });
      },
      { threshold: 0.5 }
    );

    sectionIds.forEach((id) => {
      const element = document.getElementById(id);
      if (element) observer.observe(element);
    });

    return () => observer.disconnect();
  }, [sectionIds]);

  return activeSection;
}
```

---

## 📦 Dependências Necessárias

```bash
# Adicionar typing effect
bun add react-type-animation

# Já instalados
# - framer-motion (animações)
# - antd (componentes UI)
# - @ant-design/icons (ícones)
```

---

## 🎯 Critérios de Conclusão

- [ ] Hero com typing effect funcionando
- [ ] About section com GitHub stats
- [ ] Skills grid com animações
- [ ] Experience timeline animada
- [ ] Education section completa
- [ ] Contact form funcional
- [ ] Todas as animações implementadas
- [ ] Responsivo em todas as resoluções

---

## 🔗 Navegação entre Fases

← [FASE 2: Page Restructuring](./fase2-page-restructuring.prompt.md)
→ [FASE 4: Projects Page](./fase4-projects-page.prompt.md)
