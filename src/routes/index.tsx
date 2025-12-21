// @ts-nocheck
import { createSignal, createEffect, createMemo, createResource, Show, For, Switch, Match } from 'solid-js';
import {
  ArrowRight, Github, Twitter, Linkedin, Mail, MapPin,
  Calendar, Clock, ArrowLeft, User, ExternalLink, Code2,
  Search, X, Moon, Sun, Globe, Phone, Loader2, GraduationCap, Award, List, Menu
} from 'lucide-solid';

// --- ICONES PERSONALIZADOS ---
const WhatsappIcon = (props) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width={props.size || 20}
    height={props.size || 20}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    class={props.class || ''}
  >
    <path d="M3 21l1.65-3.8a9 9 0 1 1 3.4 2.9L3 21" />
    <path d="M9 10a1 1 0 0 0 1 1" stroke="none" />
  </svg>
);

// --- 1. CONFIG E DADOS ---
const UI_CONFIG = {
  en: {
    nav: { home: 'Home', about: 'About', blog: 'Blog', projects: 'Projects', contact: 'Contact' },
    buttons: {
      about: 'About me', projects: 'View Projects', blog: 'Read Blog', readMore: 'Read article', viewDetails: 'View details',
      liveDemo: 'Live Demo', viewCode: 'View Code', send: 'Send Message', backBlog: 'Back to blog', backProjects: 'Back to projects',
      seeMore: 'See more', clearFilter: 'Clear filter', filteringBy: 'Filtering by:', viewAll: 'View all', loading: 'Loading content...',
      openMenu: 'Open menu', closeMenu: 'Close menu', openSidebar: 'Open sidebar', closeSidebar: 'Close sidebar'
    },
    sections: {
      latestBlog: 'Latest Posts', latestProjects: 'Latest Projects', blog: 'Blog', projects: 'Projects', aboutProject: 'About the Project',
      technologies: 'Technologies', screenshot: 'Project Screenshot', skills: 'Skills & Technologies', experience: 'Work Experience',
      education: 'Education', certificates: 'Certificates', social: 'Social', location: 'Location', direct: 'Direct Contact'
    },
    placeholders: {
      search: 'Search posts...', emptyBlog: 'No posts found.', emptyProjects: 'No projects found.',
      name: 'Name', email: 'Email', phone: 'Phone', message: 'Message'
    },
    contact: { title: 'Get in Touch', subtitle: 'Have a project in mind or just want to say hi?' }
  },
  pt: {
    nav: { home: 'Início', about: 'Sobre', blog: 'Blog', projects: 'Projetos', contact: 'Contato' },
    buttons: {
      about: 'Sobre mim', projects: 'Ver Projetos', blog: 'Ler o Blog', readMore: 'Ler artigo', viewDetails: 'Ver detalhes',
      liveDemo: 'Demo Ao Vivo', viewCode: 'Ver Código', send: 'Enviar Mensagem', backBlog: 'Voltar para o blog', backProjects: 'Voltar para projetos',
      seeMore: 'Ver mais', clearFilter: 'Limpar filtro', filteringBy: 'Filtrando por:', viewAll: 'Ver todos', loading: 'Carregando conteúdo...',
      openMenu: 'Abrir menu', closeMenu: 'Fechar menu', openSidebar: 'Abrir barra lateral', closeSidebar: 'Fechar barra lateral'
    },
    sections: {
      latestBlog: 'Últimos Posts', latestProjects: 'Últimos Projetos', blog: 'Blog', projects: 'Projetos', aboutProject: 'Sobre o Projeto',
      technologies: 'Tecnologias', screenshot: 'Screenshot do Projeto', skills: 'Habilidades & Tecnologias', experience: 'Experiência Profissional',
      education: 'Educação', certificates: 'Certificados', social: 'Redes Sociais', location: 'Localização', direct: 'Contato Direto'
    },
    placeholders: {
      search: 'Buscar posts...', emptyBlog: 'Nenhum post encontrado.', emptyProjects: 'Nenhum projeto encontrado.',
      name: 'Nome', email: 'Email', phone: 'Telefone', message: 'Mensagem'
    },
    contact: { title: 'Entre em Contato', subtitle: 'Tem um projeto em mente ou apenas quer dar um oi?' }
  }
};

const mockApiCall = (lang) => new Promise((resolve) => {
  setTimeout(() => {
    resolve({
      profile: {
        name: 'Fabio Souza',
        greeting: lang === 'en' ? "Hi, I'm dev Fabio." : 'Olá, Eu sou o dev Fabio.',
        role: lang === 'en' ? 'VoIP Engineer & DevOps' : 'Engenheiro VoIP & DevOps',
        shortBio: lang === 'en'
          ? 'Specializing in SIP, networking, and automation. Enhancing reliability in telecom environments.'
          : 'Especializado em SIP, redes e automação. Aumentando a confiabilidade em ambientes de telecomunicações.',
        longBio: lang === 'en'
          ? 'Experienced telecommunications engineer with a strong focus on voice and data services. Specialized in technical support for SIP Trunk, SIP Link, PBX, and Call Center services. Proficient in service monitoring, log analysis, and automation using tools like Zabbix, Grafana, Splunk, and Python 3.'
          : 'Engenheiro de telecomunicações experiente com forte foco em serviços de voz e dados. Especializado em suporte técnico para serviços SIP Trunk, SIP Link, PBX e Call Center. Proficiente em monitoramento de serviços, análise de logs e automação utilizando ferramentas como Zabbix, Grafana, Splunk e Python 3.',
        location: 'São Paulo, Brazil',
        email: 'fabio@example.com',
        phone: '+55 11 99999-9999',
        socialLinks: [
          { network: 'github', url: 'http://github.com/oornnery/' },
          { network: 'linkedin', url: '#' },
          { network: 'twitter', url: '#' },
          { network: 'whatsapp', url: 'https://wa.me/5511999999999' },
          { network: 'email', url: 'mailto:fabio@example.com' }
        ]
      },
      skills: ['Git', 'React.js', 'FastAPI', 'SIP', 'Networking', 'DevOps', 'Zabbix', 'Grafana', 'Python 3', 'Splunk'],
      experience: lang === 'en'
        ? [
          {
            id: 1,
            title: 'net2phone brasil',
            subtitle: 'Voice/VoIP Engineer I',
            date: 'Feb 2020 — Present',
            location: 'São Paulo, Brazil',
            description: 'Specialized in voice and data services, providing technical support for SIP Trunk, SIP Link, PBX, and Call Center services. Managed tickets using JIRA, Salesforce, and BA. Configured and maintained voice and data equipment.'
          },
          {
            id: 2,
            title: 'sipvoice telecom',
            subtitle: 'Junior Support Analyst',
            date: 'Aug 2018 — Oct 2019',
            location: 'São Paulo Area, Brazil',
            description: 'Responsible for opening and handling tickets, providing support and maintenance for machines, servers, and networks.'
          }
        ]
        : [
          {
            id: 1,
            title: 'net2phone brasil',
            subtitle: 'Voice/VoIP Engineer I',
            date: 'Fev 2020 — Presente',
            location: 'São Paulo, Brasil',
            description: 'Especializado em serviços de voz e dados, prestando suporte técnico para SIP Trunk, SIP Link, PBX e Call Center. Gerenciamento de tickets via JIRA, Salesforce e BA.'
          },
          {
            id: 2,
            title: 'sipvoice telecom',
            subtitle: 'Analista de suporte júnior',
            date: 'Ago 2018 — Out 2019',
            location: 'São Paulo e Região, Brasil',
            description: 'Responsável pela abertura e tratamento de chamados, suporte e manutenção de máquinas, servidores e redes.'
          }
        ],
      education: lang === 'en'
        ? [
          { id: 1, title: 'Universidade Anhembi Morumbi', subtitle: "Bachelor's, Information Security", date: '2021 — 2023' },
          { id: 2, title: 'UNINOVE', subtitle: 'IT Management, Information Technology', date: '2018 — 2020' }
        ]
        : [
          { id: 1, title: 'Universidade Anhembi Morumbi', subtitle: 'Graduação, Segurança da informação', date: '2021 — 2023' },
          { id: 2, title: 'UNINOVE', subtitle: 'Gestão Tecnologia da Informação, Tecnologia da Informação', date: '2018 — 2020' }
        ],
      certificates: lang === 'en'
        ? [
          { id: 1, title: 'LPIC-1: Linux Administrator', subtitle: 'Linux Professional Institute', date: '2023' },
          { id: 2, title: 'Zabbix Certified Specialist', subtitle: 'Zabbix LLC', date: '2022' }
        ]
        : [
          { id: 1, title: 'LPIC-1: Linux Administrator', subtitle: 'Linux Professional Institute', date: '2023' },
          { id: 2, title: 'Zabbix Certified Specialist', subtitle: 'Zabbix LLC', date: '2022' }
        ],
      projects: lang === 'en'
        ? [
          {
            id: 1,
            title: 'Vercel Analytics Clone',
            desc: 'An analytics dashboard rebuilt with SolidJS and Tailwind.',
            details: 'This project replicates the Vercel Analytics dashboard functionality using SolidJS signals for fine-grained reactivity. Focused on performance and real-time data visualization.',
            tags: ['SolidJS', 'Tremor', 'Serverless'],
            year: '2024',
            link: '#',
            repo: '#',
            type: 'project'
          },
          {
            id: 2,
            title: 'SaaS Starter Kit',
            desc: 'Complete SaaS boilerplate with authentication, Stripe payments, and configured database.',
            details: 'A production-ready starter kit for building SaaS applications. It features a complete authentication flow using NextAuth, subscription management with Stripe Webhooks, and a Prisma ORM setup.',
            tags: ['Next.js', 'Stripe', 'Prisma'],
            year: '2023',
            link: '#',
            repo: '#',
            type: 'project'
          }
        ]
        : [
          {
            id: 1,
            title: 'Vercel Analytics Clone',
            desc: 'Um dashboard de analytics reconstruído com SolidJS e Tailwind.',
            details: 'Este projeto replica a funcionalidade do dashboard da Vercel Analytics usando signals do SolidJS. Focado em performance e visualização de dados em tempo real.',
            tags: ['SolidJS', 'Tremor', 'Serverless'],
            year: '2024',
            link: '#',
            repo: '#',
            type: 'project'
          },
          {
            id: 2,
            title: 'SaaS Starter Kit',
            desc: 'Boilerplate completo para SaaS com autenticação e Stripe.',
            details: 'Um kit inicial pronto para produção para construir aplicações SaaS. Possui um fluxo de autenticação completo usando NextAuth, gerenciamento de assinaturas com Stripe Webhooks e configuração Prisma ORM.',
            tags: ['Next.js', 'Stripe', 'Prisma'],
            year: '2023',
            link: '#',
            repo: '#',
            type: 'project'
          }
        ],
      posts: lang === 'en'
        ? [
          {
            id: 1,
            slug: 'solid-vs-react',
            title: 'Why I Migrated from React to SolidJS',
            desc: 'A deep dive into fine-grained reactivity and performance.',
            content: 'This is an example of how the post content would be rendered. The visual structure keeps the reader focused with a clean layout. SolidJS offers a unique approach to reactivity that differs significantly from React\'s Virtual DOM.',
            date: 'Oct 21, 2024',
            readTime: '8 min',
            tags: ['Frontend', 'Performance'],
            type: 'post'
          },
          {
            id: 2,
            slug: 'fastapi-typescript',
            title: 'FastAPI for TypeScript Developers',
            desc: 'Leveraging static typing in the Python backend.',
            content: 'FastAPI brings the joy of type hints to Python web development. For TypeScript developers accustomed to strong typing, this feels like home. This article explores how to bridge the gap between these two ecosystems.',
            date: 'Sep 15, 2024',
            readTime: '12 min',
            tags: ['Backend', 'Python', 'TypeScript'],
            type: 'post'
          }
        ]
        : [
          {
            id: 1,
            slug: 'solid-vs-react',
            title: 'Por que migrei de React para SolidJS',
            desc: 'Uma análise profunda sobre reatividade fina e performance.',
            content: 'Este é um exemplo de como o conteúdo do post seria renderizado. A estrutura visual mantém o leitor focado com um layout limpo. SolidJS oferece uma abordagem única para reatividade que difere significativamente do Virtual DOM do React.',
            date: '21 Out, 2024',
            readTime: '8 min',
            tags: ['Frontend', 'Performance'],
            type: 'post'
          },
          {
            id: 2,
            slug: 'fastapi-typescript',
            title: 'FastAPI para Desenvolvedores TypeScript',
            desc: 'Aproveitando a tipagem estática no backend Python.',
            content: 'FastAPI traz a alegria das dicas de tipo para o desenvolvimento web em Python. Para desenvolvedores TypeScript acostumados com tipagem forte, isso parece familiar. Este artigo explora como unir esses dois ecossistemas.',
            date: '15 Set, 2024',
            readTime: '12 min',
            tags: ['Backend', 'Python', 'TypeScript'],
            type: 'post'
          }
        ]
    });
  }, 400);
});

const fetchPortfolioData = async (lang) => mockApiCall(lang);

// --- 2. COMPONENTES ATÔMICOS ---
const Button = (props) => {
  const base = 'inline-flex items-center gap-2 rounded-lg font-medium text-sm transition-all focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed';
  const variants = {
    primary: 'bg-zinc-900 dark:bg-zinc-100 text-white dark:text-zinc-950 hover:bg-zinc-700 dark:hover:bg-zinc-300 focus:ring-zinc-900 dark:focus:ring-zinc-100 px-5 py-2.5',
    secondary: 'text-zinc-700 dark:text-zinc-300 border border-zinc-300 dark:border-zinc-700 hover:bg-zinc-100 dark:hover:bg-zinc-800 focus:ring-zinc-500 px-5 py-2.5',
    ghost: 'text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-white hover:bg-zinc-100 dark:hover:bg-zinc-800/50 px-4 py-2',
    link: 'text-blue-600 dark:text-blue-400 hover:underline p-0 h-auto font-normal',
    icon: 'p-2 hover:bg-zinc-100 dark:hover:bg-zinc-800 rounded-full text-zinc-500 hover:text-zinc-900 dark:hover:text-zinc-100'
  };

  return (
    <button
      class={`${base} ${variants[props.variant || 'primary']} ${props.class || ''}`}
      onClick={props.onClick}
      aria-label={props['aria-label']}
    >
      {props.children}
    </button>
  );
};

const Tag = (props) => {
  const sizes = {
    small: "text-[9px] px-1.5 py-0.5",
    normal: "text-[10px] px-2 py-1"
  };
  
  const baseClasses = `font-mono uppercase tracking-wider rounded border transition-colors ${sizes[props.size || 'normal']}`;
  const interactiveClasses = props.onClick ? "cursor-pointer hover:bg-zinc-200 dark:hover:bg-zinc-800 hover:text-zinc-900 dark:hover:text-zinc-300" : "";
  const activeClasses = props.active 
    ? "bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-500/20" 
    : "text-zinc-500 dark:text-zinc-400 bg-zinc-100 dark:bg-zinc-900 border-zinc-200 dark:border-zinc-800";

  return (
    <span 
      onClick={(e) => {
        if(props.onClick) { e.stopPropagation(); props.onClick(); }
      }}
      class={`${baseClasses} ${activeClasses} ${interactiveClasses}`}
    >
      {props.children}
    </span>
  );
};

const Input = (props) => (
  <div>
    <Show when={props.label}>
      <label for={props.id} class="block text-xs font-bold text-zinc-500 dark:text-zinc-400 uppercase tracking-wider mb-2">
        {props.label}
      </label>
    </Show>
    <input 
      id={props.id}
      type={props.type || "text"}
      placeholder={props.placeholder}
      value={props.value || ""}
      onInput={props.onInput}
      class="w-full bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-zinc-400 dark:focus:border-zinc-600 transition-colors text-zinc-900 dark:text-zinc-100 placeholder:text-zinc-400 dark:placeholder:text-zinc-600" 
    />
  </div>
);

const TextArea = (props) => (
  <div>
     <Show when={props.label}>
      <label for={props.id} class="block text-xs font-bold text-zinc-500 dark:text-zinc-400 uppercase tracking-wider mb-2">
        {props.label}
      </label>
    </Show>
    <textarea 
      id={props.id}
      rows={props.rows || 4}
      placeholder={props.placeholder}
      class="w-full bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-zinc-400 dark:focus:border-zinc-600 transition-colors text-zinc-900 dark:text-zinc-100 placeholder:text-zinc-400 dark:placeholder:text-zinc-600 resize-y" 
    />
  </div>
);

const SocialLinks = (props) => {
  const IconMap = { 
    github: Github, 
    twitter: Twitter, 
    linkedin: Linkedin, 
    mail: Mail, 
    email: Mail,
    whatsapp: WhatsappIcon
  };
  
  return (
    <Show when={props.links}>
      <div class={`flex gap-4 ${props.class || ""}`} onClick={(e) => e.stopPropagation()}>
      <For each={props.links}>
        {(link) => {
          const Icon = IconMap[link.network.toLowerCase()] || ExternalLink;
          return (
            <a 
              href={link.url} 
              target="_blank" 
              rel="noreferrer" 
              class="text-zinc-500 hover:text-zinc-900 dark:hover:text-zinc-300 transition-colors" 
              aria-label={link.network}
            >
              <Icon size={20} />
            </a>
          );
        }}
      </For>
      </div>
    </Show>
  );
};

// --- COMPONENTES MOLECULARES ---

const ContentCard = (props) => (
  <div 
    onClick={props.onClick}
    class="group cursor-pointer bg-white dark:bg-zinc-900/30 rounded-lg p-6 hover:bg-zinc-50 dark:hover:bg-zinc-900/50 transition-all border border-zinc-100 dark:border-transparent shadow-sm dark:shadow-none"
  >
    <div class="flex items-center gap-3 text-xs text-zinc-500 mb-3 font-mono">
      {props.meta1}
      <Show when={props.meta2}>
        <span>•</span>
        {props.meta2}
      </Show>
    </div>
    
    <h3 class="text-xl font-bold text-zinc-900 dark:text-zinc-100 mb-2 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
      {props.title}
    </h3>
    
    <Show when={props.tags}>
      <div class="mb-3">
        <div class="flex flex-wrap gap-2">
          <For each={props.tags}>
            {(tag) => <Tag onClick={() => props.onTagClick && props.onTagClick(tag)}>{tag}</Tag>}
          </For>
        </div>
      </div>
    </Show>

    <p class="text-zinc-600 dark:text-zinc-400 leading-relaxed text-sm mb-4 line-clamp-3">
      {props.desc}
    </p>

    <Show when={props.actionText}>
      <div class="flex items-center text-sm text-blue-600 dark:text-blue-400 font-medium opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all duration-300">
        {props.actionText} <ArrowRight size={14} class="ml-1" />
      </div>
    </Show>
  </div>
);

const TimelineItem = (props) => (
  <div class="relative pl-8 pb-12 group">
    <Show when={!props.isLast}>
      <div class="absolute left-0 top-2 h-full w-px bg-zinc-200 dark:bg-zinc-800"></div>
    </Show>
    <div class="absolute left-[-4px] top-2 w-2 h-2 rounded-full bg-zinc-300 dark:bg-zinc-700 border border-white dark:border-zinc-900 group-hover:bg-blue-500 transition-colors"></div>
    
    <div class="flex flex-col sm:flex-row sm:items-baseline justify-between mb-1">
      <h3 class="text-zinc-900 dark:text-zinc-100 font-medium text-lg">{props.title}</h3>
      <span class="text-xs font-mono text-zinc-500 shrink-0">{props.date}</span>
    </div>
    <div class="flex flex-wrap items-center gap-2 text-sm text-zinc-500 mb-3">
      <span class="font-medium text-zinc-700 dark:text-zinc-300">{props.subtitle}</span>
      <Show when={props.location}>
         <span class="text-zinc-400">•</span>
         <span>{props.location}</span>
      </Show>
    </div>
    <Show when={props.description}>
      <p class="text-sm text-zinc-600 dark:text-zinc-400 leading-relaxed text-justify">
        {props.description}
      </p>
    </Show>
  </div>
);

const ContactSection = (props) => (
  <section class="animate-in fade-in duration-500 max-w-4xl mx-auto w-full">
    <div class="bg-zinc-50 dark:bg-zinc-900/30 rounded-2xl p-8 border border-zinc-100 dark:border-transparent">
      <h2 class="text-2xl font-bold text-zinc-900 dark:text-zinc-100 mb-2">{props.uiText.contact.title}</h2>
      <p class="text-zinc-500 dark:text-zinc-400 mb-8">{props.uiText.contact.subtitle}</p>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-12">
        {/* Form */}
        <form class="space-y-4" onSubmit={(e) => e.preventDefault()}>
          <Input id="name" label={props.uiText.placeholders.name} placeholder={props.uiText.placeholders.name} />
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input id="email" type="email" label={props.uiText.placeholders.email} placeholder={props.uiText.placeholders.email} />
            <Input id="phone" type="tel" label={props.uiText.placeholders.phone} placeholder={props.uiText.placeholders.phone} />
          </div>
          <TextArea id="message" label={props.uiText.placeholders.message} placeholder={props.uiText.placeholders.message} />
          <Button class="w-full sm:w-auto">{props.uiText.buttons.send}</Button>
        </form>

        {/* Contact Info */}
        <div class="flex flex-col justify-center space-y-8 pl-0 md:pl-8 border-t md:border-t-0 md:border-l border-zinc-200 dark:border-zinc-800 pt-8 md:pt-0">
           <div>
             <h3 class="text-sm font-bold text-zinc-900 dark:text-zinc-100 mb-4">{props.uiText.sections.social}</h3>
             <SocialLinks links={props.profile.socialLinks} />
           </div>
           
           <div>
              <h3 class="text-sm font-bold text-zinc-900 dark:text-zinc-100 mb-4">{props.uiText.sections.location}</h3>
              <div class="flex items-center gap-2 text-zinc-500 dark:text-zinc-400 text-sm">
                <MapPin size={18} />
                <a 
                  href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(props.profile.location)}`} 
                  target="_blank" 
                  rel="noreferrer" 
                  class="hover:text-zinc-900 dark:hover:text-zinc-100 transition-colors"
                >
                  {props.profile.location}
                </a>
              </div>
           </div>

           <div>
              <h3 class="text-sm font-bold text-zinc-900 dark:text-zinc-100 mb-4">{props.uiText.sections.direct}</h3>
              <div class="flex flex-col gap-2 text-zinc-500 dark:text-zinc-400 text-sm">
                <a href={`mailto:${props.profile.email}`} class="flex items-center gap-2 hover:text-zinc-900 dark:hover:text-zinc-200 transition-colors">
                  <Mail size={18} /> {props.profile.email}
                </a>
                <a href={`tel:${props.profile.phone.replace(/\D/g, '')}`} class="flex items-center gap-2 hover:text-zinc-900 dark:hover:text-zinc-200 transition-colors">
                  <Phone size={18} /> {props.profile.phone}
                </a>
              </div>
           </div>
        </div>
      </div>
    </div>
  </section>
);

// --- ORGANISMOS ---

const Sidebar = (props) => (
  <aside class="space-y-8 animate-in fade-in slide-in-from-left-4 duration-700 delay-150">
    <div 
      onClick={props.onGoToAbout}
      class="group cursor-pointer transition-all bg-white dark:bg-zinc-900/30 rounded-xl p-6 border border-zinc-100 dark:border-transparent shadow-sm dark:shadow-none"
    >
      <div class="w-16 h-16 bg-zinc-200 dark:bg-zinc-800 rounded-full mb-4 flex items-center justify-center text-zinc-400 dark:text-zinc-500 overflow-hidden">
        <User size={32} />
      </div>
      <h3 class="font-bold text-zinc-900 dark:text-zinc-100 mb-1">{props.profile.greeting}</h3>
      <p class="text-xs text-zinc-500 font-mono mb-3">{props.profile.role}</p>
      <p class="text-sm text-zinc-600 dark:text-zinc-400 leading-relaxed mb-4">
        {props.profile.shortBio}
      </p>

      <SocialLinks links={props.profile.socialLinks} class="mb-4" />
      
      <div class="flex items-center text-sm text-blue-600 dark:text-blue-400 font-medium opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all duration-300">
        {props.uiText.buttons.seeMore} <ArrowRight size={14} class="ml-1" />
      </div>
    </div>

    {/* Dynamic List */}
    <Show when={props.items && props.items.length > 0}>
      <div>
        <h4 class="text-xs font-bold text-zinc-500 uppercase tracking-wider mb-6">
          {props.title}
        </h4>
        <div class="space-y-4">
          <For each={props.items}>
            {(item) => (
              <div 
                onClick={() => props.onItemClick(item)}
                class="group cursor-pointer bg-white dark:bg-zinc-900/30 p-4 rounded-xl border border-zinc-100 dark:border-transparent shadow-sm dark:shadow-none hover:bg-zinc-50 dark:hover:bg-zinc-900/50 transition-all"
              >
                <h5 class="text-sm text-zinc-700 dark:text-zinc-300 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors line-clamp-2 leading-snug mb-2 font-medium">
                  {item.title}
                </h5>
                <div class="flex justify-between items-center mb-2">
                   <span class="text-xs text-zinc-500 dark:text-zinc-600 font-mono">{props.isProject ? item.year : item.date}</span>
                </div>
                 <Show when={item.tags}>
                    <div class="flex flex-wrap gap-1.5">
                      <For each={item.tags.slice(0, 3)}>
                        {(tag) => <Tag size="small" onClick={() => props.onTagClick(tag)}>{tag}</Tag>}
                      </For>
                    </div>
                 </Show>
              </div>
            )}
          </For>
        </div>
      </div>
    </Show>
  </aside>
);

const NavBar = (props) => {
  const [isMenuOpen, setIsMenuOpen] = createSignal(false);

  const handleNavClick = (key) => {
    props.setActiveTab(key);
    props.onClearFilters();
    setIsMenuOpen(false);
  };

  return (
    <div>
      <header class="flex justify-between items-center py-8 mb-12 sm:mb-20">
        <div 
          class="text-xl font-bold tracking-tight cursor-pointer select-none z-50 relative"
          onClick={() => handleNavClick('home')}
        >
          fabio<span class="text-zinc-400 dark:text-zinc-600">.dev</span>
        </div>
        
        {/* Desktop Navigation */}
        <div class="hidden md:flex items-center gap-6">
          <nav class="flex gap-6 text-sm font-medium text-zinc-500 dark:text-zinc-400">
            <For each={['home', 'about', 'blog', 'projects', 'contact']}>
              {(key) => {
                const tabName = key === 'about' ? 'sobre' : key === 'projects' ? 'projetos' : key === 'contact' ? 'contato' : key;
                return (
                  <button
                    onClick={() => handleNavClick(tabName)}
                    class={`transition-colors hover:text-zinc-900 dark:hover:text-zinc-100 ${props.activeTab === tabName ? 'text-zinc-900 dark:text-zinc-100 font-semibold' : ''}`}
                  >
                    {props.navLabels[key]}
                  </button>
                );
              }}
            </For>
          </nav>

          <div class="w-px h-4 bg-zinc-300 dark:bg-zinc-800"></div>

          <div class="flex items-center gap-4">
            <Button variant="icon" onClick={props.toggleLang} class="text-xs font-mono font-bold flex gap-1 w-auto px-2">
              <Globe size={16} /> {props.lang.toUpperCase()}
            </Button>
            <Button variant="icon" onClick={props.toggleTheme}>
              {props.isDark ? <Sun size={18} /> : <Moon size={18} />}
            </Button>
            <a href="http://github.com/oornnery/" target="_blank" rel="noreferrer" class="text-zinc-500 hover:text-zinc-900 dark:hover:text-zinc-100 transition-colors">
              <Github size={18} />
            </a>
          </div>
        </div>

        {/* Mobile Menu Button */}
        <div class="md:hidden flex items-center gap-4">
           <Button variant="icon" onClick={() => setIsMenuOpen(true)} aria-label={props.uiText.buttons.openMenu}>
             <Menu size={24} />
           </Button>
        </div>
      </header>

      {/* Mobile Drawer */}
      <Show when={isMenuOpen()}>
        <div class="fixed inset-0 z-[100] md:hidden flex justify-end">
          <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={() => setIsMenuOpen(false)}></div>
          
          <div class="relative w-64 bg-white dark:bg-zinc-900 h-full shadow-2xl p-6 flex flex-col animate-in slide-in-from-right duration-300">
            <div class="flex justify-end mb-8">
              <Button variant="icon" onClick={() => setIsMenuOpen(false)} aria-label={props.uiText.buttons.closeMenu}>
                <X size={24} />
              </Button>
            </div>

            <nav class="flex flex-col gap-6 text-lg font-medium text-zinc-600 dark:text-zinc-400">
              <For each={['home', 'about', 'blog', 'projects', 'contact']}>
                {(key) => {
                  const tabName = key === 'about' ? 'sobre' : key === 'projects' ? 'projetos' : key === 'contact' ? 'contato' : key;
                  return (
                    <button
                      onClick={() => handleNavClick(tabName)}
                      class={`text-left transition-colors hover:text-zinc-900 dark:hover:text-zinc-100 ${props.activeTab === tabName ? 'text-zinc-900 dark:text-zinc-100 font-bold' : ''}`}
                    >
                      {props.navLabels[key]}
                    </button>
                  );
                }}
              </For>
            </nav>

            <div class="mt-auto pt-8 border-t border-zinc-200 dark:border-zinc-800 flex flex-col gap-6">
               <div class="flex items-center justify-between">
                  <span class="text-sm text-zinc-500">Theme</span>
                  <Button variant="icon" onClick={props.toggleTheme}>
                    {props.isDark ? <Sun size={18} /> : <Moon size={18} />}
                  </Button>
               </div>
               <div class="flex items-center justify-between">
                  <span class="text-sm text-zinc-500">Language</span>
                  <Button variant="icon" onClick={props.toggleLang} class="text-xs font-mono font-bold">
                    <Globe size={16} /> {props.lang.toUpperCase()}
                  </Button>
               </div>
               <div class="flex items-center justify-between">
                  <span class="text-sm text-zinc-500">Github</span>
                  <a href="http://github.com/oornnery/" target="_blank" rel="noreferrer" class="p-2 text-zinc-500 hover:text-zinc-900 dark:hover:text-zinc-100 transition-colors">
                    <Github size={18} />
                  </a>
               </div>
            </div>
          </div>
        </div>
      </Show>
    </div>
  );
};

// --- DETAIL VIEW COMPONENT ---
const DetailView = (props) => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = createSignal(false);
  
  const item = () => props.selectedType === 'post' 
    ? props.data.posts.find(p => p.id === props.selectedItemId) 
    : props.data.projects.find(p => p.id === props.selectedItemId);
  
  const isPost = () => props.selectedType === 'post';
  
  const relatedItems = () => isPost()
    ? props.data.posts.filter(p => p.id !== item()?.id).slice(0, 3)
    : props.data.projects.filter(p => p.id !== item()?.id).slice(0, 3);

  return (
    <Show when={item()}>
      <div class="animate-in fade-in duration-500 relative">
        <div class="flex justify-between items-center mb-8">
          <Button variant="ghost" onClick={props.onBack} class="pl-0 hover:bg-transparent">
            <ArrowLeft size={16} /> {isPost() ? props.ui.buttons.backBlog : props.ui.buttons.backProjects}
          </Button>
          <div class="lg:hidden">
            <Button variant="icon" onClick={() => setIsMobileMenuOpen(true)} aria-label={props.ui.buttons.openSidebar}>
              <List size={20} />
            </Button>
          </div>
        </div>
        
        <div class="grid grid-cols-1 lg:grid-cols-[280px_1fr] gap-12 items-start">
          <div class="hidden lg:block sticky top-8">
            <Sidebar 
              profile={props.data.profile} 
              uiText={props.ui} 
              onGoToAbout={props.onGoToAbout}
              title={isPost() ? props.ui.sections.latestBlog : props.ui.sections.latestProjects}
              items={relatedItems()}
              onItemClick={(i) => props.onItemClick(i, props.selectedType)}
              onTagClick={(t) => props.onTagClick(t, props.selectedType)}
              isProject={!isPost()}
            />
          </div>

          <Show when={isMobileMenuOpen()}>
            <div class="fixed inset-0 z-50 lg:hidden flex justify-end">
              <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={() => setIsMobileMenuOpen(false)}></div>
              <div class="relative w-80 bg-white dark:bg-zinc-900 h-full shadow-xl p-6 overflow-y-auto animate-in slide-in-from-right duration-300">
                <div class="flex justify-end mb-4">
                  <Button variant="icon" onClick={() => setIsMobileMenuOpen(false)} aria-label={props.ui.buttons.closeSidebar}>
                    <X size={20} />
                  </Button>
                </div>
                <Sidebar 
                  profile={props.data.profile} 
                  uiText={props.ui} 
                  onGoToAbout={() => { props.onGoToAbout(); setIsMobileMenuOpen(false); }}
                  title={isPost() ? props.ui.sections.latestBlog : props.ui.sections.latestProjects}
                  items={relatedItems()}
                  onItemClick={(i) => { props.onItemClick(i, props.selectedType); setIsMobileMenuOpen(false); }}
                  onTagClick={(t) => { props.onTagClick(t, props.selectedType); setIsMobileMenuOpen(false); }}
                  isProject={!isPost()}
                />
              </div>
            </div>
          </Show>

          <article class="min-w-0">
            <header class="mb-10 border-b border-zinc-200 dark:border-zinc-800 pb-10">
              <div class="flex flex-wrap gap-3 text-xs font-mono text-zinc-500 mb-6">
                <Show when={isPost()} fallback={
                  <span class="bg-zinc-100 dark:bg-zinc-800 px-2 py-0.5 rounded text-zinc-600 dark:text-zinc-400">{item()?.year}</span>
                }>
                  <span class="flex items-center gap-1"><Calendar size={12}/> {item()?.date}</span>
                  <span>•</span>
                  <span class="flex items-center gap-1"><Clock size={12}/> {item()?.readTime}</span>
                </Show>
              </div>
              <h1 class="text-3xl sm:text-4xl font-extrabold text-zinc-900 dark:text-zinc-100 mb-6 tracking-tight leading-tight">{item()?.title}</h1>
              <Show when={item()?.tags}>
                <div class="flex flex-wrap gap-2 mb-6">
                  <For each={item()?.tags}>
                    {(tag) => <Tag onClick={() => props.onTagClick(tag, props.selectedType)}>{tag}</Tag>}
                  </For>
                </div>
              </Show>
              <p class="text-xl text-zinc-600 dark:text-zinc-400 leading-relaxed">{item()?.desc}</p>
              <Show when={!isPost()}>
                <div class="flex gap-4 mt-8">
                  <a href={item()?.link} class="inline-flex items-center gap-2 px-4 py-2 bg-zinc-900 dark:bg-zinc-100 text-white dark:text-zinc-900 rounded-lg font-medium text-sm hover:opacity-90 transition-opacity">
                    <ExternalLink size={16} /> {props.ui.buttons.liveDemo}
                  </a>
                  <a href={item()?.repo} class="inline-flex items-center gap-2 px-4 py-2 border border-zinc-300 dark:border-zinc-700 text-zinc-700 dark:text-zinc-300 rounded-lg font-medium text-sm hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors">
                    <Code2 size={16} /> {props.ui.buttons.viewCode}
                  </a>
                </div>
              </Show>
            </header>

            <div class="prose prose-zinc dark:prose-invert max-w-none">
              <Show when={isPost()} fallback={
                <div>
                  <h3 class="text-xl font-bold text-zinc-900 dark:text-zinc-100 mb-4">{props.ui.sections.aboutProject}</h3>
                  <p class="text-zinc-700 dark:text-zinc-300 leading-7 mb-6">{item()?.details}</p>
                  <h3 class="text-xl font-bold text-zinc-900 dark:text-zinc-100 mb-4">{props.ui.sections.technologies}</h3>
                  <ul class="list-disc list-inside text-zinc-700 dark:text-zinc-300 space-y-2 mb-8">
                    <li>Framework: {item()?.tags?.[0]}</li>
                    <li>Styling: Tailwind CSS</li>
                  </ul>
                  <div class="bg-zinc-50 dark:bg-zinc-900/50 border border-zinc-200 dark:border-zinc-800 rounded-xl p-12 flex items-center justify-center text-zinc-500 mb-8">
                    <span class="text-sm italic">{props.ui.sections.screenshot}</span>
                  </div>
                </div>
              }>
                <p class="text-zinc-700 dark:text-zinc-300 leading-7 mb-6 whitespace-pre-line">{item()?.content}</p>
                <div class="bg-zinc-50 dark:bg-[#161618] border border-zinc-200 dark:border-zinc-800 rounded-lg p-4 my-8 overflow-x-auto">
                  <pre class="font-mono text-sm text-blue-600 dark:text-blue-300">{'// Code example placeholder'}</pre>
                </div>
              </Show>
            </div>
          </article>
        </div>
      </div>
    </Show>
  );
};

// --- LIST VIEW COMPONENT ---
const ListView = (props) => {
  const isPost = () => props.type === 'blog';
  const title = () => isPost() ? props.ui.sections.blog : props.ui.sections.projects;
  const items = () => isPost() ? props.filteredPosts : props.filteredProjects;
  const itemType = () => isPost() ? 'post' : 'project';

  return (
    <section class="animate-in fade-in duration-500">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between mb-8 gap-4">
        <h1 class="text-3xl font-bold text-zinc-900 dark:text-zinc-100">{title()}</h1>
        <div class="relative">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500" size={16} />
          <input 
            type="text" 
            placeholder={props.ui.placeholders.search}
            value={props.searchText}
            onInput={(e) => props.setSearchText(e.target.value)}
            class="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 text-zinc-900 dark:text-zinc-200 text-sm rounded-full pl-10 pr-4 py-2 focus:outline-none focus:border-zinc-400 dark:focus:border-zinc-600 w-full sm:w-64 placeholder:text-zinc-400 dark:placeholder:text-zinc-600 transition-colors"
          />
        </div>
      </div>

      <Show when={props.selectedTag}>
        <div class="flex items-center gap-2 mb-6 animate-in fade-in">
          <span class="text-sm text-zinc-500 dark:text-zinc-400">{props.ui.buttons.filteringBy}</span>
          <Tag active onClick={props.clearFilters}>
            <span class="flex items-center gap-1">{props.selectedTag} <X size={12} /></span>
          </Tag>
          <Button variant="link" onClick={props.clearFilters} class="text-xs">{props.ui.buttons.clearFilter}</Button>
        </div>
      </Show>

      <div class="grid gap-6">
        <Show when={items().length > 0} fallback={
          <div class="text-center py-20 border border-dashed border-zinc-200 dark:border-zinc-800 rounded-lg">
            <p class="text-zinc-500">{isPost() ? props.ui.placeholders.emptyBlog : props.ui.placeholders.emptyProjects}</p>
            <Button variant="link" onClick={props.clearFilters}>{props.ui.buttons.clearFilter}</Button>
          </div>
        }>
          <For each={items()}>
            {(item) => (
              <ContentCard 
                title={item.title}
                desc={item.desc}
                meta1={itemType() === 'post' ? <span class="flex items-center gap-1"><Calendar size={12}/>{item.date}</span> : <span class="bg-zinc-100 dark:bg-zinc-800 px-2 py-0.5 rounded text-zinc-600 dark:text-zinc-400">{item.year}</span>}
                meta2={itemType() === 'post' ? <span class="flex items-center gap-1"><Clock size={12}/>{item.readTime}</span> : null}
                tags={item.tags}
                onClick={() => props.onItemClick(item, itemType())}
                onTagClick={(tag) => props.onTagClick(tag, itemType())}
                actionText={itemType() === 'post' ? props.ui.buttons.readMore : props.ui.buttons.viewDetails}
              />
            )}
          </For>
        </Show>
      </div>
    </section>
  );
};

// --- APLICAÇÃO PRINCIPAL ---

export default function App() {
  const [activeTab, setActiveTab] = createSignal('home');
  const [selectedItemId, setSelectedItemId] = createSignal(null);
  const [selectedType, setSelectedType] = createSignal(null);
  
  const [isDark, setIsDark] = createSignal(true);
  const [lang, setLang] = createSignal('en');

  // Resource para carregar dados
  const [data] = createResource(lang, fetchPortfolioData);

  const [selectedTag, setSelectedTag] = createSignal(null);
  const [searchText, setSearchText] = createSignal('');

  createEffect(() => {
    if (isDark()) document.documentElement.classList.add('dark');
    else document.documentElement.classList.remove('dark');
  });

  const toggleTheme = () => setIsDark(!isDark());
  const toggleLang = () => setLang(prev => prev === 'en' ? 'pt' : 'en');

  const clearFilters = () => {
    setSelectedTag(null);
    setSearchText('');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleNavigate = (tab) => {
    setActiveTab(tab);
    setSelectedItemId(null);
    setSelectedType(null);
    clearFilters();
  };

  const handleItemClick = (item, type) => {
    setSelectedItemId(item.id);
    setSelectedType(type);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleTagClick = (tag, type) => {
    if (selectedItemId()) {
      setSelectedItemId(null);
      setSelectedType(null);
    }
    setActiveTab(type === 'post' ? 'blog' : 'projects');
    setSelectedTag(tag);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // Views Derivadas
  const filteredPosts = createMemo(() => {
    if (!data()) return [];
    return data().posts.filter(post => {
      const matchesTag = selectedTag() ? post.tags.includes(selectedTag()) : true;
      const matchesSearch = searchText() 
        ? post.title.toLowerCase().includes(searchText().toLowerCase()) || 
          post.desc.toLowerCase().includes(searchText().toLowerCase())
        : true;
      return matchesTag && matchesSearch;
    });
  });

  const filteredProjects = createMemo(() => {
    if (!data()) return [];
    return data().projects.filter(project => {
      const matchesTag = selectedTag() ? project.tags.includes(selectedTag()) : true;
      return matchesTag;
    });
  });

  const ui = () => UI_CONFIG[lang()];

  return (
    <div class={`min-h-screen font-sans selection:bg-blue-500/30 transition-colors duration-300 ${isDark() ? 'bg-[#111111] text-[#EDEDED]' : 'bg-white text-zinc-900'}`}>
      <div class="max-w-[900px] mx-auto px-6 border-x border-zinc-100 dark:border-zinc-900/50 min-h-screen flex flex-col">
        
        {/* HEADER */}
        <NavBar 
          activeTab={activeTab()} 
          setActiveTab={handleNavigate}
          onClearFilters={clearFilters} 
          isDark={isDark()} 
          toggleTheme={toggleTheme} 
          lang={lang()} 
          toggleLang={toggleLang} 
          navLabels={ui().nav}
          uiText={ui()}
        />
        
        {/* MAIN CONTENT */}
        <main class="pb-20 flex-1">
          <Show when={!data.loading} fallback={
            <div class="flex flex-col items-center justify-center py-20 gap-4">
              <Loader2 class="animate-spin" size={32} />
              <span class="text-sm font-mono animate-pulse">{ui().buttons.loading}</span>
            </div>
          }>
            <Switch>
              {/* DETAIL VIEW */}
              <Match when={selectedItemId()}>
                <DetailView 
                  selectedItemId={selectedItemId()}
                  selectedType={selectedType()}
                  data={data()}
                  ui={ui()}
                  onBack={() => { setSelectedItemId(null); setSelectedType(null); }}
                  onGoToAbout={() => handleNavigate('sobre')}
                  onItemClick={handleItemClick}
                  onTagClick={handleTagClick}
                />
              </Match>

              {/* HOME VIEW */}
              <Match when={activeTab() === 'home'}>
                 <section class="mb-16 animate-in fade-in duration-500">
                    <div class="bg-zinc-50 dark:bg-zinc-900/30 rounded-2xl p-8 flex flex-col md:flex-row gap-8 items-start border border-zinc-100 dark:border-transparent">
                      <div class="shrink-0">
                        <div class="w-24 h-24 sm:w-32 sm:h-32 bg-zinc-200 dark:bg-zinc-800 rounded-full flex items-center justify-center text-zinc-400 dark:text-zinc-500 overflow-hidden border-2 border-white dark:border-zinc-700/50">
                          <User size={48} />
                        </div>
                      </div>
                      <div class="flex-1">
                        <h1 class="text-3xl sm:text-4xl font-extrabold tracking-tight text-zinc-900 dark:text-zinc-100 mb-2">{data().profile.greeting}</h1>
                        <p class="text-sm text-zinc-500 font-mono mb-4">{data().profile.role}</p>
                        <p class="text-lg text-zinc-600 dark:text-zinc-400 leading-relaxed mb-6 max-w-2xl">{data().profile.shortBio}</p>
                        <SocialLinks links={data().profile.socialLinks} class="mb-8" />
                        <div class="flex flex-wrap gap-3 items-center">
                          <Button onClick={() => handleNavigate('sobre')}><User size={16} /> {ui().buttons.about}</Button>
                          <Button variant="secondary" onClick={() => handleNavigate('projetos')}>{ui().buttons.projects}</Button>
                          <Button variant="ghost" onClick={() => handleNavigate('blog')}>{ui().buttons.blog} <ArrowRight size={16} /></Button>
                        </div>
                      </div>
                    </div>
                 </section>

                 <section class="mb-16 animate-in slide-in-from-bottom-4 duration-500">
                    <h2 class="text-xs font-bold text-zinc-500 uppercase tracking-wider mb-6">{ui().sections.latestBlog}</h2>
                    <div class="space-y-4">
                      <For each={data().posts.slice(0, 2)}>
                        {(post) => (
                          <ContentCard 
                            title={post.title}
                            desc={post.desc}
                            meta1={<span class="flex items-center gap-1"><Calendar size={12}/>{post.date}</span>}
                            meta2={<span class="flex items-center gap-1"><Clock size={12}/>{post.readTime}</span>}
                            tags={post.tags}
                            onClick={() => handleItemClick(post, 'post')}
                            onTagClick={(tag) => handleTagClick(tag, 'post')}
                            actionText={ui().buttons.readMore}
                          />
                        )}
                      </For>
                    </div>
                 </section>

                 <section class="mb-16 animate-in slide-in-from-bottom-8 duration-500 delay-75">
                    <h2 class="text-xs font-bold text-zinc-500 uppercase tracking-wider mb-6">{ui().sections.latestProjects}</h2>
                    <div class="space-y-4">
                      <For each={data().projects.slice(0, 2)}>
                        {(project) => (
                          <ContentCard 
                            title={project.title}
                            desc={project.desc}
                            meta1={<span class="bg-zinc-100 dark:bg-zinc-800 px-2 py-0.5 rounded text-zinc-600 dark:text-zinc-400">{project.year}</span>}
                            tags={project.tags}
                            onClick={() => handleItemClick(project, 'project')}
                            onTagClick={(tag) => handleTagClick(tag, 'project')}
                            actionText={ui().buttons.viewDetails}
                          />
                        )}
                      </For>
                    </div>
                 </section>
                 
                 <ContactSection uiText={ui()} profile={data().profile} />
              </Match>

              {/* ABOUT VIEW */}
              <Match when={activeTab() === 'sobre'}>
                 <section class="animate-in fade-in duration-500 max-w-2xl mx-auto">
                    <div class="flex flex-col gap-6 mb-12">
                      <div>
                        <h1 class="text-3xl font-bold text-zinc-900 dark:text-zinc-100 mb-2">{data().profile.name}</h1>
                        <p class="text-lg text-zinc-600 dark:text-zinc-400">{data().profile.role}</p>
                        <div class="flex items-center gap-2 text-zinc-500 text-sm mt-2">
                          <MapPin size={14} />
                          <a href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(data().profile.location)}`} target="_blank" rel="noreferrer" class="hover:text-zinc-900 dark:hover:text-zinc-100 transition-colors">{data().profile.location}</a>
                        </div>
                      </div>
                      <div class="prose prose-zinc dark:prose-invert">
                        <p class="text-zinc-600 dark:text-zinc-300 leading-relaxed">{data().profile.longBio}</p>
                      </div>
                      <SocialLinks links={data().profile.socialLinks} />
                    </div>

                    <div class="space-y-16">
                       <div>
                         <h2 class="text-xs font-bold text-zinc-500 uppercase tracking-wider mb-6">{ui().sections.skills}</h2>
                         <div class="flex flex-wrap gap-2">
                           <For each={data().skills}>{(skill) => <Tag>{skill}</Tag>}</For>
                         </div>
                       </div>
                       <div>
                         <h2 class="text-xs font-bold text-zinc-500 uppercase tracking-wider mb-8">{ui().sections.experience}</h2>
                         <div class="space-y-2">
                           <For each={data().experience}>
                             {(job, i) => <TimelineItem {...job} isLast={i() === data().experience.length - 1} />}
                           </For>
                         </div>
                       </div>
                       <div>
                         <h2 class="text-xs font-bold text-zinc-500 uppercase tracking-wider mb-6 flex items-center gap-2"><GraduationCap size={16} /> {ui().sections.education}</h2>
                         <div class="space-y-2">
                            <For each={data().education}>
                             {(edu, i) => <TimelineItem {...edu} isLast={i() === data().education.length - 1} />}
                           </For>
                         </div>
                       </div>
                       <div>
                         <h2 class="text-xs font-bold text-zinc-500 uppercase tracking-wider mb-6 flex items-center gap-2"><Award size={16} /> {ui().sections.certificates}</h2>
                         <div class="space-y-2">
                            <For each={data().certificates}>
                             {(cert, i) => <TimelineItem {...cert} isLast={i() === data().certificates.length - 1} />}
                           </For>
                         </div>
                       </div>
                    </div>
                 </section>
              </Match>

              {/* BLOG VIEW */}
              <Match when={activeTab() === 'blog'}>
                <ListView 
                  type="blog"
                  ui={ui()}
                  filteredPosts={filteredPosts()}
                  filteredProjects={filteredProjects()}
                  searchText={searchText()}
                  setSearchText={setSearchText}
                  selectedTag={selectedTag()}
                  clearFilters={clearFilters}
                  onItemClick={handleItemClick}
                  onTagClick={handleTagClick}
                />
              </Match>

              {/* PROJECTS VIEW */}
              <Match when={activeTab() === 'projetos'}>
                <ListView 
                  type="projetos"
                  ui={ui()}
                  filteredPosts={filteredPosts()}
                  filteredProjects={filteredProjects()}
                  searchText={searchText()}
                  setSearchText={setSearchText}
                  selectedTag={selectedTag()}
                  clearFilters={clearFilters}
                  onItemClick={handleItemClick}
                  onTagClick={handleTagClick}
                />
              </Match>

              {/* CONTACT VIEW */}
              <Match when={activeTab() === 'contato'}>
                <ContactSection uiText={ui()} profile={data().profile} />
              </Match>

            </Switch>
          </Show>
        </main>
        
        {/* FOOTER */}
        <footer class="mt-auto py-10 border-t border-zinc-200 dark:border-zinc-900 flex flex-col sm:flex-row justify-between items-center text-zinc-500 text-sm gap-4">
          <Show when={!data.loading}>
             <div>&copy; {new Date().getFullYear()} {data().profile.name}.</div>
             <SocialLinks links={data().profile.socialLinks} />
          </Show>
        </footer>

      </div>
    </div>
  );
}
