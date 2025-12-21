import React, { useState, useMemo, useEffect } from 'react';
import {
    ArrowRight, Github, Twitter, Linkedin, Mail, MapPin,
    Calendar, Clock, ArrowLeft, User, ExternalLink, Code2,
    Search, X, Moon, Sun, Globe, Phone, Loader2, GraduationCap, Award, List, Menu
} from 'lucide-react';

// --- ICONS PERSONALIZADOS ---
const WhatsappIcon = ({ size = 20, className = "" }) => (
    <svg 
    xmlns= "http://www.w3.org/2000/svg"
width = { size }
height = { size }
viewBox = "0 0 24 24"
fill = "none"
stroke = "currentColor"
strokeWidth = "2"
strokeLinecap = "round"
strokeLinejoin = "round"
className = { className }
    >
    <path d="M3 21l1.65-3.8a9 9 0 1 1 3.4 2.9L3 21" />
        <path d="M9 10a0.5 .5 0 0 0 1 1l2.2 2.2a0.5 .5 0 0 0 1 1l6-6a0.5 .5 0 0 0 .5-.5" style = {{ display: 'none' }} />
            < path d = "M9 10a1 1 0 0 0 1 1" stroke = "none" />
                </svg>
);

// --- 1. CONFIGURATION & DATA LAYER ---

const UI_CONFIG = {
    en: {
        nav: { home: 'Home', about: 'About', blog: 'Blog', projects: 'Projects', contact: 'Contact' },
        buttons: {
            about: "About me",
            projects: "View Projects",
            blog: "Read Blog",
            readMore: "Read article",
            viewDetails: "View details",
            liveDemo: "Live Demo",
            viewCode: "View Code",
            send: "Send Message",
            backBlog: "Back to blog",
            backProjects: "Back to projects",
            seeMore: "See more",
            clearFilter: "Clear filter",
            filteringBy: "Filtering by:",
            viewAll: "View all",
            loading: "Loading content...",
            openMenu: "Open menu",
            closeMenu: "Close menu",
            openSidebar: "Open sidebar",
            closeSidebar: "Close sidebar"
        },
        sections: {
            latestBlog: "Latest Posts",
            latestProjects: "Latest Projects",
            blog: "Blog",
            projects: "Projects",
            aboutProject: "About the Project",
            technologies: "Technologies",
            screenshot: "Project Screenshot",
            skills: "Skills & Technologies",
            experience: "Work Experience",
            education: "Education",
            certificates: "Certificates",
            social: "Social",
            location: "Location",
            direct: "Direct Contact"
        },
        placeholders: {
            search: "Search posts...",
            emptyBlog: "No posts found.",
            emptyProjects: "No projects found.",
            name: "Name",
            email: "Email",
            phone: "Phone",
            message: "Message"
        },
        contact: {
            title: "Get in Touch",
            subtitle: "Have a project in mind or just want to say hi?"
        }
    },
    pt: {
        nav: { home: 'Início', about: 'Sobre', blog: 'Blog', projects: 'Projetos', contact: 'Contato' },
        buttons: {
            about: "Sobre mim",
            projects: "Ver Projetos",
            blog: "Ler o Blog",
            readMore: "Ler artigo",
            viewDetails: "Ver detalhes",
            liveDemo: "Demo Ao Vivo",
            viewCode: "Ver Código",
            send: "Enviar Mensagem",
            backBlog: "Voltar para o blog",
            backProjects: "Voltar para projetos",
            seeMore: "Ver mais",
            clearFilter: "Limpar filtro",
            filteringBy: "Filtrando por:",
            viewAll: "Ver todos",
            loading: "Carregando conteúdo...",
            openMenu: "Abrir menu",
            closeMenu: "Fechar menu",
            openSidebar: "Abrir barra lateral",
            closeSidebar: "Fechar barra lateral"
        },
        sections: {
            latestBlog: "Últimos Posts",
            latestProjects: "Últimos Projetos",
            blog: "Blog",
            projects: "Projetos",
            aboutProject: "Sobre o Projeto",
            technologies: "Tecnologias",
            screenshot: "Screenshot do Projeto",
            skills: "Habilidades & Tecnologias",
            experience: "Experiência Profissional",
            education: "Educação",
            certificates: "Certificados",
            social: "Redes Sociais",
            location: "Localização",
            direct: "Contato Direto"
        },
        placeholders: {
            search: "Buscar posts...",
            emptyBlog: "Nenhum post encontrado.",
            emptyProjects: "Nenhum projeto encontrado.",
            name: "Nome",
            email: "Email",
            phone: "Telefone",
            message: "Mensagem"
        },
        contact: {
            title: "Entre em Contato",
            subtitle: "Tem um projeto em mente ou apenas quer dar um oi?"
        }
    }
};

const mockApiCall = (lang) => {
    return new Promise((resolve) => {
        setTimeout(() => {
            resolve({
                profile: {
                    name: "Fabio Souza",
                    greeting: lang === 'en' ? "Hi, I'm dev Fabio." : "Olá, Eu sou o dev Fabio.",
                    role: lang === 'en' ? "VoIP Engineer & DevOps" : "Engenheiro VoIP & DevOps",
                    shortBio: lang === 'en'
                        ? "Specializing in SIP, networking, and automation. Enhancing reliability in telecom environments."
                        : "Especializado em SIP, redes e automação. Aumentando a confiabilidade em ambientes de telecomunicações.",
                    longBio: lang === 'en'
                        ? "Experienced telecommunications engineer with a strong focus on voice and data services. Specialized in technical support for SIP Trunk, SIP Link, PBX, and Call Center services. Proficient in service monitoring, log analysis, and automation using tools like Zabbix, Grafana, Splunk, and Python 3."
                        : "Engenheiro de telecomunicações experiente com forte foco em serviços de voz e dados. Especializado em suporte técnico para serviços SIP Trunk, SIP Link, PBX e Call Center. Proficiente em monitoramento de serviços, análise de logs e automação utilizando ferramentas como Zabbix, Grafana, Splunk e Python 3.",
                    location: "São Paulo, Brazil",
                    email: "fabio@example.com",
                    phone: "+55 11 99999-9999",
                    socialLinks: [
                        { network: 'github', url: 'http://github.com/oornnery/' },
                        { network: 'linkedin', url: '#' },
                        { network: 'twitter', url: '#' },
                        { network: 'whatsapp', url: 'https://wa.me/5511999999999' },
                        { network: 'email', url: 'mailto:fabio@example.com' }
                    ]
                },
                skills: ["Git", "React.js", "FastAPI", "SIP", "Networking", "DevOps", "Zabbix", "Grafana", "Python 3", "Splunk"],
                experience: lang === 'en' ? [
                    {
                        id: 1,
                        title: "net2phone brasil",
                        subtitle: "Voice/VoIP Engineer I",
                        date: "Feb 2020 — Present",
                        location: "São Paulo, Brazil",
                        description: "Specialized in voice and data services, providing technical support for SIP Trunk, SIP Link, PBX, and Call Center services. Managed tickets using JIRA, Salesforce, and BA. Configured and maintained voice and data equipment."
                    },
                    {
                        id: 2,
                        title: "sipvoice telecom",
                        subtitle: "Junior Support Analyst",
                        date: "Aug 2018 — Oct 2019",
                        location: "São Paulo Area, Brazil",
                        description: "Responsible for opening and handling tickets, providing support and maintenance for machines, servers, and networks."
                    }
                ] : [
                    {
                        id: 1,
                        title: "net2phone brasil",
                        subtitle: "Voice/VoIP Engineer I",
                        date: "Fev 2020 — Presente",
                        location: "São Paulo, Brasil",
                        description: "Especializado em serviços de voz e dados, prestando suporte técnico para SIP Trunk, SIP Link, PBX e Call Center. Gerenciamento de tickets via JIRA, Salesforce e BA."
                    },
                    {
                        id: 2,
                        title: "sipvoice telecom",
                        subtitle: "Analista de suporte júnior",
                        date: "Ago 2018 — Out 2019",
                        location: "São Paulo e Região, Brasil",
                        description: "Responsável pela abertura e tratamento de chamados, suporte e manutenção de máquinas, servidores e redes."
                    }
                ],
                education: lang === 'en' ? [
                    { id: 1, title: "Universidade Anhembi Morumbi", subtitle: "Bachelor's, Information Security", date: "2021 — 2023" },
                    { id: 2, title: "UNINOVE", subtitle: "IT Management, Information Technology", date: "2018 — 2020" }
                ] : [
                    { id: 1, title: "Universidade Anhembi Morumbi", subtitle: "Graduação, Segurança da informação", date: "2021 — 2023" },
                    { id: 2, title: "UNINOVE", subtitle: "Gestão Tecnologia da Informação, Tecnologia da Informação", date: "2018 — 2020" }
                ],
                certificates: lang === 'en' ? [
                    { id: 1, title: "LPIC-1: Linux Administrator", subtitle: "Linux Professional Institute", date: "2023" },
                    { id: 2, title: "Zabbix Certified Specialist", subtitle: "Zabbix LLC", date: "2022" }
                ] : [
                    { id: 1, title: "LPIC-1: Linux Administrator", subtitle: "Linux Professional Institute", date: "2023" },
                    { id: 2, title: "Zabbix Certified Specialist", subtitle: "Zabbix LLC", date: "2022" }
                ],
                projects: lang === 'en' ? [
                    {
                        id: 1,
                        title: "Vercel Analytics Clone",
                        desc: "An analytics dashboard rebuilt with SolidJS and Tailwind.",
                        details: "This project replicates the Vercel Analytics dashboard functionality using SolidJS signals for fine-grained reactivity. Focused on performance and real-time data visualization.",
                        tags: ["SolidJS", "Tremor", "Serverless"],
                        year: "2024",
                        link: "#",
                        repo: "#",
                        type: "project"
                    },
                    {
                        id: 2,
                        title: "SaaS Starter Kit",
                        desc: "Complete SaaS boilerplate with authentication, Stripe payments, and configured database.",
                        details: "A production-ready starter kit for building SaaS applications. It features a complete authentication flow using NextAuth, subscription management with Stripe Webhooks, and a Prisma ORM setup.",
                        tags: ["Next.js", "Stripe", "Prisma"],
                        year: "2023",
                        link: "#",
                        repo: "#",
                        type: "project"
                    }
                ] : [
                    {
                        id: 1,
                        title: "Vercel Analytics Clone",
                        desc: "Um dashboard de analytics reconstruído com SolidJS e Tailwind.",
                        details: "Este projeto replica a funcionalidade do dashboard da Vercel Analytics usando signals do SolidJS. Focado em performance e visualização de dados em tempo real.",
                        tags: ["SolidJS", "Tremor", "Serverless"],
                        year: "2024",
                        link: "#",
                        repo: "#",
                        type: "project"
                    },
                    {
                        id: 2,
                        title: "SaaS Starter Kit",
                        desc: "Boilerplate completo para SaaS com autenticação e Stripe.",
                        details: "Um kit inicial pronto para produção para construir aplicações SaaS. Possui um fluxo de autenticação completo usando NextAuth, gerenciamento de assinaturas com Stripe Webhooks e configuração Prisma ORM.",
                        tags: ["Next.js", "Stripe", "Prisma"],
                        year: "2023",
                        link: "#",
                        repo: "#",
                        type: "project"
                    }
                ],
                posts: lang === 'en' ? [
                    {
                        id: 1,
                        slug: "solid-vs-react",
                        title: "Why I Migrated from React to SolidJS",
                        desc: "A deep dive into fine-grained reactivity and performance.",
                        content: "This is an example of how the post content would be rendered. The visual structure keeps the reader focused with a clean layout. SolidJS offers a unique approach to reactivity that differs significantly from React's Virtual DOM.",
                        date: "Oct 21, 2024",
                        readTime: "8 min",
                        tags: ["Frontend", "Performance"],
                        type: "post"
                    },
                    {
                        id: 2,
                        slug: "fastapi-typescript",
                        title: "FastAPI for TypeScript Developers",
                        desc: "Leveraging static typing in the Python backend.",
                        content: "FastAPI brings the joy of type hints to Python web development. For TypeScript developers accustomed to strong typing, this feels like home. This article explores how to bridge the gap between these two ecosystems.",
                        date: "Sep 15, 2024",
                        readTime: "12 min",
                        tags: ["Backend", "Python", "TypeScript"],
                        type: "post"
                    }
                ] : [
                    {
                        id: 1,
                        slug: "solid-vs-react",
                        title: "Por que migrei de React para SolidJS",
                        desc: "Uma análise profunda sobre reatividade fina e performance.",
                        content: "Este é um exemplo de como o conteúdo do post seria renderizado. A estrutura visual mantém o leitor focado com um layout limpo. SolidJS oferece uma abordagem única para reatividade que difere significativamente do Virtual DOM do React.",
                        date: "21 Out, 2024",
                        readTime: "8 min",
                        tags: ["Frontend", "Performance"],
                        type: "post"
                    },
                    {
                        id: 2,
                        slug: "fastapi-typescript",
                        title: "FastAPI para Desenvolvedores TypeScript",
                        desc: "Aproveitando a tipagem estática no backend Python.",
                        content: "FastAPI traz a alegria das dicas de tipo para o desenvolvimento web em Python. Para desenvolvedores TypeScript acostumados com tipagem forte, isso parece familiar. Este artigo explora como unir esses dois ecossistemas.",
                        date: "15 Set, 2024",
                        readTime: "12 min",
                        tags: ["Backend", "Python", "TypeScript"],
                        type: "post"
                    }
                ]
            });
        }, 600);
    });
};

// --- 2. ATOMIC COMPONENTS ---

const Button = ({ children, variant = 'primary', className = '', onClick, ...props }) => {
    const baseStyles = "inline-flex items-center gap-2 rounded-lg font-medium text-sm transition-all focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed";

    const variants = {
        primary: "bg-zinc-900 dark:bg-zinc-100 text-white dark:text-zinc-950 hover:bg-zinc-700 dark:hover:bg-zinc-300 focus:ring-zinc-900 dark:focus:ring-zinc-100 px-5 py-2.5",
        secondary: "text-zinc-700 dark:text-zinc-300 border border-zinc-300 dark:border-zinc-700 hover:bg-zinc-100 dark:hover:bg-zinc-800 focus:ring-zinc-500 px-5 py-2.5",
        ghost: "text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-white hover:bg-zinc-100 dark:hover:bg-zinc-800/50 px-4 py-2",
        link: "text-blue-600 dark:text-blue-400 hover:underline p-0 h-auto font-normal",
        icon: "p-2 hover:bg-zinc-100 dark:hover:bg-zinc-800 rounded-full text-zinc-500 hover:text-zinc-900 dark:hover:text-zinc-100"
    };

    return (
        <button className= {`${baseStyles} ${variants[variant]} ${className}`
} onClick = { onClick } { ...props }>
    { children }
    </button>
  );
};

const Tag = ({ children, onClick, active = false, size = 'normal' }) => {
    const sizes = {
        small: "text-[9px] px-1.5 py-0.5",
        normal: "text-[10px] px-2 py-1"
    };

    const baseClasses = `font-mono uppercase tracking-wider rounded border transition-colors ${sizes[size]}`;
    const interactiveClasses = onClick ? "cursor-pointer hover:bg-zinc-200 dark:hover:bg-zinc-800 hover:text-zinc-900 dark:hover:text-zinc-300" : "";
    const activeClasses = active
        ? "bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-500/20"
        : "text-zinc-500 dark:text-zinc-400 bg-zinc-100 dark:bg-zinc-900 border-zinc-200 dark:border-zinc-800";

    return (
        <span 
      onClick= {(e) => {
    if (onClick) { e.stopPropagation(); onClick(); }
}}
className = {`${baseClasses} ${activeClasses} ${interactiveClasses}`}
    >
    { children }
    </span>
  );
};

const Input = ({ label, id, type = "text", ...props }) => (
    <div>
    { label && (
        <label htmlFor= { id } className = "block text-xs font-bold text-zinc-500 dark:text-zinc-400 uppercase tracking-wider mb-2" >
            { label }
            </label>
    )}
<input 
      id={ id }
type = { type }
className = "w-full bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-zinc-400 dark:focus:border-zinc-600 transition-colors text-zinc-900 dark:text-zinc-100 placeholder:text-zinc-400 dark:placeholder:text-zinc-600"
{...props }
    />
    </div>
);

const TextArea = ({ label, id, rows = 4, ...props }) => (
    <div>
    { label && (
        <label htmlFor= { id } className = "block text-xs font-bold text-zinc-500 dark:text-zinc-400 uppercase tracking-wider mb-2" >
            { label }
            </label>
    )}
<textarea 
      id={ id }
rows = { rows }
className = "w-full bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-zinc-400 dark:focus:border-zinc-600 transition-colors text-zinc-900 dark:text-zinc-100 placeholder:text-zinc-400 dark:placeholder:text-zinc-600 resize-y"
{...props }
    />
    </div>
);

const SocialLinks = ({ links, className = "" }) => {
    const IconMap = {
        github: Github,
        twitter: Twitter,
        linkedin: Linkedin,
        mail: Mail,
        email: Mail,
        whatsapp: WhatsappIcon
    };

    if (!links) return null;

    return (
        <div className= {`flex gap-4 ${className}`
} onClick = {(e) => e.stopPropagation()}>
{
    links.map((link, index) => {
        const Icon = IconMap[link.network.toLowerCase()] || ExternalLink;
        return (
            <a 
            key= { index }
        href = { link.url }
        target = "_blank"
        rel = "noreferrer"
        className = "text-zinc-500 hover:text-zinc-900 dark:hover:text-zinc-300 transition-colors"
        aria - label={ link.network }
          >
            <Icon size={ 20 } />
                </a>
        );
})}
</div>
  );
};

// --- 3. MOLECULAR COMPONENTS ---

const Card = ({ children, onClick, className = "" }) => (
    <div 
    onClick= { onClick }
className = {`group bg-white dark:bg-zinc-900/30 rounded-xl border border-zinc-100 dark:border-transparent shadow-sm dark:shadow-none transition-all ${onClick ? 'cursor-pointer hover:bg-zinc-50 dark:hover:bg-zinc-900/50' : ''} ${className}`}
  >
    { children }
    </div>
);

const ContentCard = ({ title, desc, meta1, meta2, tags, onClick, onTagClick, actionText }) => (
    <Card onClick= { onClick } className = "p-6" >
        <div className="flex items-center gap-3 text-xs text-zinc-500 mb-3 font-mono" >
            { meta1 }
{ meta2 && <><span>•</span>{meta2}</ >}
</div>

    < h3 className = "text-xl font-bold text-zinc-900 dark:text-zinc-100 mb-2 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors" >
        { title }
        </h3>

{
    tags && (
        <div className="mb-3" >
            <div className="flex flex-wrap gap-2" >
                { tags.map(tag => <Tag key={ tag } onClick = {() => onTagClick && onTagClick(tag)} > { tag } </Tag>)
}
</div>
    </div>
    )}

<p className="text-zinc-600 dark:text-zinc-400 leading-relaxed text-sm mb-4 line-clamp-3" >
    { desc }
    </p>

{
    actionText && (
        <div className="flex items-center text-sm text-blue-600 dark:text-blue-400 font-medium opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all duration-300" >
            { actionText } < ArrowRight size = { 14} className = "ml-1" />
                </div>
    )
}
</Card>
);

const TimelineItem = ({ title, subtitle, date, location, description, isLast }) => (
    <div className= "relative pl-8 pb-12 group" >
    {!isLast && <div className="absolute left-0 top-2 h-full w-px bg-zinc-200 dark:bg-zinc-800" > </div>}
<div className="absolute left-[-4px] top-2 w-2 h-2 rounded-full bg-zinc-300 dark:bg-zinc-700 border border-white dark:border-zinc-900 group-hover:bg-blue-500 transition-colors" > </div>

    < div className = "flex flex-col sm:flex-row sm:items-baseline justify-between mb-1" >
        <h3 className="text-zinc-900 dark:text-zinc-100 font-medium text-lg" > { title } </h3>
            < span className = "text-xs font-mono text-zinc-500 shrink-0" > { date } </span>
                </div>
                < div className = "flex flex-wrap items-center gap-2 text-sm text-zinc-500 mb-3" >
                    <span className="font-medium text-zinc-700 dark:text-zinc-300" > { subtitle } </span>
{ location && <><span className="text-zinc-400" >•</span><span>{location}</span > </> }
</div>
{
    description && (
        <p className="text-sm text-zinc-600 dark:text-zinc-400 leading-relaxed text-justify" >
            { description }
            </p>
    )
}
</div>
);

const SidebarProfile = ({ profile, uiText, onGoToAbout, compact = false }) => (
    <Card onClick= { onGoToAbout } className = {`p-6 ${compact ? 'bg-zinc-50 dark:bg-zinc-900/50' : ''}`}>
        <div className="flex items-start gap-4" >
            <div className="w-12 h-12 bg-zinc-200 dark:bg-zinc-800 rounded-full flex items-center justify-center text-zinc-400 dark:text-zinc-500 overflow-hidden shrink-0" >
                <User size={ 24 } />
                    </div>
                    < div >
                    <h3 className="font-bold text-zinc-900 dark:text-zinc-100 text-sm" > { profile.name } </h3>
                        < p className = "text-xs text-zinc-500 font-mono" > { profile.role } </p>
                            </div>
                            </div>

{
    !compact && (
        <>
        <p className="text-sm text-zinc-600 dark:text-zinc-400 leading-relaxed my-4" >
            { profile.shortBio }
            </p>
            < SocialLinks links = { profile.socialLinks } className = "mb-4" />
                </>
    )
}

<div className="mt-4 flex items-center text-sm text-blue-600 dark:text-blue-400 font-medium opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all duration-300" >
    { uiText.buttons.seeMore } < ArrowRight size = { 14} className = "ml-1" />
        </div>
        </Card>
);

const SidebarList = ({ title, items, onItemClick, onTagClick, isProject }) => (
    <div className= "mt-8" >
    <h4 className="text-xs font-bold text-zinc-500 uppercase tracking-wider mb-4" > { title } </h4>
        < div className = "space-y-3" >
        {
            items.map(item => (
                <div 
          key= { item.id } 
          onClick = {() => onItemClick(item)}
className = "group cursor-pointer hover:bg-zinc-100 dark:hover:bg-zinc-900/50 p-3 -mx-3 rounded-lg transition-colors"
    >
    <h5 className="text-sm text-zinc-700 dark:text-zinc-300 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors line-clamp-2 leading-snug mb-2 font-medium" >
        { item.title }
        </h5>
        < div className = "flex justify-between items-center mb-2" >
            <span className="text-xs text-zinc-500 dark:text-zinc-600 font-mono" > { isProject? item.year : item.date } </span>
                </div>
{
    item.tags && (
        <div className="flex flex-wrap gap-1.5" >
        {
            item.tags.slice(0, 2).map(tag => (
                <Tag key= { tag } size = "small" onClick = {() => onTagClick(tag)} > { tag } </Tag>
                ))
}
</div>
           )}
</div>
      ))}
</div>
    </div>
);

// --- 4. ORGANISMS ---

const NavBar = ({ activeTab, setActiveTab, onClearFilters, isDark, toggleTheme, lang, toggleLang, navLabels, uiText }) => {
    const [isMenuOpen, setIsMenuOpen] = useState(false);

    const handleNavClick = (key) => {
        setActiveTab(key);
        onClearFilters();
        setIsMenuOpen(false);
    };

    return (
        <>
        <header className= "flex justify-between items-center py-8 mb-12 sm:mb-20" >
        <div 
          className="text-xl font-bold tracking-tight cursor-pointer select-none z-50 relative"
    onClick = {() => handleNavClick('home')}
        >
    fabio < span className = "text-zinc-400 dark:text-zinc-600" >.dev </span>
        </div>

{/* Desktop Navigation */ }
<div className="hidden md:flex items-center gap-6" >
    <nav className="flex gap-6 text-sm font-medium text-zinc-500 dark:text-zinc-400" >
    {
        ['home', 'about', 'blog', 'projects', 'contact'].map((key) => {
            const tabName = key === 'about' ? 'sobre' : key === 'projects' ? 'projetos' : key === 'contact' ? 'contato' : key;
            const isActive = activeTab === tabName;
            return (
                <button
                  key= { key }
            onClick = {() => handleNavClick(tabName)
        }
                  className = {`transition-colors hover:text-zinc-900 dark:hover:text-zinc-100 ${isActive ? 'text-zinc-900 dark:text-zinc-100 font-semibold' : ''}`}
        >
        { navLabels[key]}
        </button>
              );
            })}
</nav>

    < div className = "w-px h-4 bg-zinc-300 dark:bg-zinc-800" > </div>

        < div className = "flex items-center gap-4" >
            <Button variant="icon" onClick = { toggleLang } className = "text-xs font-mono font-bold flex gap-1 w-auto px-2" >
                <Globe size={ 16 } /> {lang.toUpperCase()}
                    </Button>
                    < Button variant = "icon" onClick = { toggleTheme } >
                        { isDark?<Sun size = { 18 } /> : <Moon size={ 18 } />}
</Button>
    < a href = "http://github.com/oornnery/" target = "_blank" rel = "noreferrer" className = "text-zinc-500 hover:text-zinc-900 dark:hover:text-zinc-100 transition-colors" >
        <Github size={ 18 } />
            </a>
            </div>
            </div>

{/* Mobile Menu Button */ }
<div className="md:hidden flex items-center gap-4" >
    <Button variant="icon" onClick = {() => setIsMenuOpen(true)} aria - label={ uiText.buttons.openMenu }>
        <Menu size={ 24 } />
            </Button>
            </div>
            </header>

{/* Mobile Drawer */ }
{
    isMenuOpen && (
        <div className="fixed inset-0 z-[100] md:hidden flex justify-end" >
            <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick = {() => setIsMenuOpen(false)
}> </div>

    < div className = "relative w-64 bg-white dark:bg-zinc-900 h-full shadow-2xl p-6 flex flex-col animate-in slide-in-from-right duration-300" >
        <div className="flex justify-end mb-8" >
            <Button variant="icon" onClick = {() => setIsMenuOpen(false)} aria - label={ uiText.buttons.closeMenu }>
                <X size={ 24 } />
                    </Button>
                    </div>

                    < nav className = "flex flex-col gap-6 text-lg font-medium text-zinc-600 dark:text-zinc-400" >
                    {
                        ['home', 'about', 'blog', 'projects', 'contact'].map((key) => {
                            const tabName = key === 'about' ? 'sobre' : key === 'projects' ? 'projetos' : key === 'contact' ? 'contato' : key;
                            const isActive = activeTab === tabName;
                            return (
                                <button
                    key= { key }
                            onClick = {() => handleNavClick(tabName)
                        }
                    className = {`text-left transition-colors hover:text-zinc-900 dark:hover:text-zinc-100 ${isActive ? 'text-zinc-900 dark:text-zinc-100 font-bold' : ''}`}
                        >
                        { navLabels[key]}
                        </button>
                );
              })}
</nav>

    < div className = "mt-auto pt-8 border-t border-zinc-200 dark:border-zinc-800 flex flex-col gap-6" >
        <div className="flex items-center justify-between" >
            <span className="text-sm text-zinc-500" > Theme </span>
                < Button variant = "icon" onClick = { toggleTheme } >
                    { isDark?<Sun size = { 18 } /> : <Moon size={ 18 } />}
</Button>
    </div>
    < div className = "flex items-center justify-between" >
        <span className="text-sm text-zinc-500" > Language </span>
            < Button variant = "icon" onClick = { toggleLang } className = "text-xs font-mono font-bold" >
                <Globe size={ 16 } /> {lang.toUpperCase()}
                    </Button>
                    </div>
                    < div className = "flex items-center justify-between" >
                        <span className="text-sm text-zinc-500" > Github </span>
                            < a href = "http://github.com/oornnery/" target = "_blank" rel = "noreferrer" className = "p-2 text-zinc-500 hover:text-zinc-900 dark:hover:text-zinc-100 transition-colors" >
                                <Github size={ 18 } />
                                    </a>
                                    </div>
                                    </div>
                                    </div>
                                    </div>
      )}
</>
  );
};

// --- 5. VIEWS (TEMPLATES) ---

// UNIFIED CONTACT SECTION COMPONENT (Replaces previous ContactSection and ContactView)
const ContactSection = ({ uiText, profile }) => (
    <section className= "animate-in fade-in duration-500 max-w-4xl mx-auto w-full" >
    <div className="bg-zinc-50 dark:bg-zinc-900/30 rounded-2xl p-8 border border-zinc-100 dark:border-transparent" >
        <h2 className="text-2xl font-bold text-zinc-900 dark:text-zinc-100 mb-2" > { uiText.contact.title } </h2>
            < p className = "text-zinc-500 dark:text-zinc-400 mb-8" > { uiText.contact.subtitle } </p>

                < div className = "grid grid-cols-1 md:grid-cols-2 gap-12" >
                    <form className="space-y-4" onSubmit = {(e) => e.preventDefault()}>
                        <Input id="name" label = { uiText.placeholders.name } placeholder = { uiText.placeholders.name } />
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4" >
                                <Input id="email" type = "email" label = { uiText.placeholders.email } placeholder = { uiText.placeholders.email } />
                                    <Input id="phone" type = "tel" label = { uiText.placeholders.phone } placeholder = { uiText.placeholders.phone } />
                                        </div>
                                        < TextArea id = "message" label = { uiText.placeholders.message } placeholder = { uiText.placeholders.message } />
                                            <Button className="w-full sm:w-auto" > { uiText.buttons.send } </Button>
                                                </form>

                                                < div className = "flex flex-col justify-center space-y-8 pl-0 md:pl-8 border-t md:border-t-0 md:border-l border-zinc-200 dark:border-zinc-800 pt-8 md:pt-0" >
                                                    <div>
                                                    <h3 className="text-sm font-bold text-zinc-900 dark:text-zinc-100 mb-4" > { uiText.sections.social } </h3>
                                                        < SocialLinks links = { profile.socialLinks } />
                                                            </div>

                                                            < div >
                                                            <h3 className="text-sm font-bold text-zinc-900 dark:text-zinc-100 mb-4" > { uiText.sections.location } </h3>
                                                                < div className = "flex items-center gap-2 text-zinc-500 dark:text-zinc-400 text-sm" >
                                                                    <MapPin size={ 18 } />
                                                                        < a
href = {`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(profile.location)}`}
target = "_blank"
rel = "noreferrer"
className = "hover:text-zinc-900 dark:hover:text-zinc-100 transition-colors"
    >
    { profile.location }
    </a>
    </div>
    </div>

    < div >
    <h3 className="text-sm font-bold text-zinc-900 dark:text-zinc-100 mb-4" > { uiText.sections.direct } </h3>
        < div className = "flex flex-col gap-2 text-zinc-500 dark:text-zinc-400 text-sm" >
            <a href={ `mailto:${profile.email}` } className = "flex items-center gap-2 hover:text-zinc-900 dark:hover:text-zinc-200 transition-colors" >
                <Mail size={ 18 } /> {profile.email}
                    </a>
                    < a href = {`tel:${profile.phone.replace(/\D/g, '')}`} className = "flex items-center gap-2 hover:text-zinc-900 dark:hover:text-zinc-200 transition-colors" >
                        <Phone size={ 18 } /> {profile.phone}
                            </a>
                            </div>
                            </div>
                            </div>
                            </div>
                            </div>
                            </section>
);

const Hero = ({ profile, uiText, onNavigate }) => (
    <section className= "mb-16 animate-in fade-in duration-500" >
    <div className="bg-zinc-50 dark:bg-zinc-900/30 rounded-2xl p-8 flex flex-col md:flex-row gap-8 items-start border border-zinc-100 dark:border-transparent" >
        <div className="shrink-0" >
            <div className="w-24 h-24 sm:w-32 sm:h-32 bg-zinc-200 dark:bg-zinc-800 rounded-full flex items-center justify-center text-zinc-400 dark:text-zinc-500 overflow-hidden border-2 border-white dark:border-zinc-700/50" >
                <User size={ 48 } />
                    </div>
                    </div>

                    < div className = "flex-1" >
                        <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-zinc-900 dark:text-zinc-100 mb-2" >
                            { profile.greeting }
                            </h1>
                            < p className = "text-sm text-zinc-500 font-mono mb-4" > { profile.role } </p>
                                < p className = "text-lg text-zinc-600 dark:text-zinc-400 leading-relaxed mb-6 max-w-2xl" >
                                    { profile.shortBio }
                                    </p>

                                    < SocialLinks links = { profile.socialLinks } className = "mb-8" />

                                        <div className="flex flex-wrap gap-3 items-center" >
                                            <Button onClick={ () => onNavigate('sobre') }>
                                                <User size={ 16 } /> {uiText.buttons.about}
                                                    </Button>
                                                    < Button variant = "secondary" onClick = {() => onNavigate('projetos')}>
                                                        { uiText.buttons.projects }
                                                        </Button>
                                                        < Button variant = "ghost" onClick = {() => onNavigate('blog')}>
                                                            { uiText.buttons.blog } < ArrowRight size = { 16} />
                                                                </Button>
                                                                </div>
                                                                </div>
                                                                </div>
                                                                </section>
);

const About = ({ data, uiText }) => (
    <section className= "animate-in fade-in duration-500 max-w-2xl mx-auto" >
    <div className="flex flex-col gap-6 mb-12" >
        <div>
        <h1 className="text-3xl font-bold text-zinc-900 dark:text-zinc-100 mb-2" > { data.profile.name } </h1>
            < p className = "text-lg text-zinc-600 dark:text-zinc-400" > { data.profile.role } </p>
                < div className = "flex items-center gap-2 text-zinc-500 text-sm mt-2" >
                    <MapPin size={ 14 } />
                        < a
href = {`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(data.profile.location)}`}
target = "_blank"
rel = "noreferrer"
className = "hover:text-zinc-900 dark:hover:text-zinc-100 transition-colors"
    >
    { data.profile.location }
    </a>
    </div>
    </div>

    < div className = "prose prose-zinc dark:prose-invert" >
        <p className="text-zinc-600 dark:text-zinc-300 leading-relaxed" > { data.profile.longBio } </p>
            </div>
            < SocialLinks links = { data.profile.socialLinks } />
                </div>

                < div className = "space-y-16" >
                    <div>
                    <h2 className="text-xs font-bold text-zinc-500 uppercase tracking-wider mb-6" > { uiText.sections.skills } </h2>
                        < div className = "flex flex-wrap gap-2" >
                            { data.skills.map(skill => <Tag key={ skill } > { skill } </Tag>) }
                            </div>
                            </div>

                            < div >
                            <h2 className="text-xs font-bold text-zinc-500 uppercase tracking-wider mb-8" > { uiText.sections.experience } </h2>
                                < div className = "space-y-2" >
                                    {
                                        data.experience.map((job, i) => (
                                            <TimelineItem 
              key= { job.id } 
              title = { job.title } 
              subtitle = { job.subtitle } 
              date = { job.date } 
              location = { job.location } 
              description = { job.description } 
              isLast = { i === data.experience.length - 1}
                                    />
          ))}
</div>
    </div>

    < div >
    <h2 className="text-xs font-bold text-zinc-500 uppercase tracking-wider mb-6 flex items-center gap-2" >
        <GraduationCap size={ 16 } /> {uiText.sections.education}
            </h2>
            < div className = "space-y-2" >
                {
                    data.education.map((edu, i) => (
                        <TimelineItem key= { edu.id } title = { edu.title } subtitle = { edu.subtitle } date = { edu.date } isLast = { i === data.education.length - 1} />
          ))}
</div>
    </div>

    < div >
    <h2 className="text-xs font-bold text-zinc-500 uppercase tracking-wider mb-6 flex items-center gap-2" >
        <Award size={ 16 } /> {uiText.sections.certificates}
            </h2>
            < div className = "space-y-2" >
                {
                    data.certificates.map((cert, i) => (
                        <TimelineItem key= { cert.id } title = { cert.title } subtitle = { cert.subtitle } date = { cert.date } isLast = { i === data.certificates.length - 1} />
          ))}
</div>
    </div>
    </div>
    </section>
);

const ListView = ({ title, items, type, onNavigate, onTagClick, selectedTag, filterText, setFilterText, onClearFilters, uiText }) => {
    const filteredItems = useMemo(() => {
        if (!items) return [];
        return items.filter(item => {
            const matchesTag = selectedTag ? item.tags.includes(selectedTag) : true;
            const matchesSearch = filterText
                ? item.title.toLowerCase().includes(filterText.toLowerCase()) || item.desc.toLowerCase().includes(filterText.toLowerCase())
                : true;
            return matchesTag && matchesSearch;
        });
    }, [items, selectedTag, filterText]);

    return (
        <section className= "animate-in fade-in duration-500" >
        <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-8 gap-4" >
            <h1 className="text-3xl font-bold text-zinc-900 dark:text-zinc-100" > { title } </h1>

                < div className = "relative" >
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500" size = { 16} />
                        <input 
            type="text"
    placeholder = { uiText.placeholders.search }
    value = { filterText }
    onChange = {(e) => setFilterText(e.target.value)}
className = "bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 text-zinc-900 dark:text-zinc-200 text-sm rounded-full pl-10 pr-4 py-2 focus:outline-none focus:border-zinc-400 dark:focus:border-zinc-600 w-full sm:w-64 placeholder:text-zinc-400 dark:placeholder:text-zinc-600 transition-colors"
    />
    </div>
    </div>

{
    selectedTag && (
        <div className="flex items-center gap-2 mb-6 animate-in fade-in" >
            <span className="text-sm text-zinc-500 dark:text-zinc-400" > { uiText.buttons.filteringBy } </span>
                < Tag active onClick = { onClearFilters } >
                    <span className="flex items-center gap-1" > { selectedTag } < X size = { 12} /> </span>
                        </Tag>
                        < Button variant = "link" onClick = { onClearFilters } className = "text-xs" > { uiText.buttons.clearFilter } </Button>
                            </div>
      )
}

<div className="grid gap-6" >
{
    filteredItems.length > 0 ? (
        filteredItems.map(item => (
            <ContentCard 
              key= { item.id }
              title = { item.title }
              desc = { item.desc }
              meta1 = { type === 'post' ? <span className="flex items-center gap-1" > <Calendar size={ 12} /> { item.date } < /span> : <span className="bg-zinc-100 dark:bg-zinc-800 px-2 py-0.5 rounded text-zinc-600 dark:text-zinc-400">{item.year}</span >}
meta2 = { type === 'post' ? <span className="flex items-center gap-1" > <Clock size={ 12 } />{item.readTime}</span > : null}
tags = { item.tags }
onClick = {() => onNavigate(item)}
onTagClick = { onTagClick }
actionText = { type === 'post' ? uiText.buttons.readMore : uiText.buttons.viewDetails}
            />
          ))
        ) : (
    <div className= "text-center py-20 border border-dashed border-zinc-200 dark:border-zinc-800 rounded-lg" >
    <p className="text-zinc-500" > { type === 'post' ? uiText.placeholders.emptyBlog : uiText.placeholders.emptyProjects}</p>
        < Button variant = "link" onClick = { onClearFilters } > { uiText.buttons.clearFilter } </Button>
            </div>
        )}
</div>
    </section>
  );
};

const DetailView = ({ item, type, onBack, onNavigate, onGoToAbout, onTagClick, profile, uiText, relatedItems }) => {
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
    const isPost = type === 'post';

    return (
        <div className= "animate-in fade-in duration-500 relative" >
        <div className="flex justify-between items-center mb-8" >
            <Button variant="ghost" onClick = { onBack } className = "pl-0 hover:bg-transparent" >
                <ArrowLeft size={ 16 } /> {isPost ? uiText.buttons.backBlog : uiText.buttons.backProjects}
                    </Button>

                    < div className = "lg:hidden" >
                        <Button variant="icon" onClick = {() => setIsMobileMenuOpen(true)} aria - label={ uiText.buttons.openSidebar }>
                            <List size={ 20 } />
                                </Button>
                                </div>
                                </div>

                                < div className = "grid grid-cols-1 lg:grid-cols-[280px_1fr] gap-12 items-start" >
                                    <div className="hidden lg:block sticky top-8" >
                                        <SidebarProfile profile={ profile } uiText = { uiText } onGoToAbout = { onGoToAbout } />
                                            <SidebarList 
            title={ isPost ? uiText.sections.latestBlog : uiText.sections.latestProjects }
items = { relatedItems }
onItemClick = { onNavigate }
onTagClick = { onTagClick }
isProject = {!isPost} 
          />
    </div>

{
    isMobileMenuOpen && (
        <div className="fixed inset-0 z-50 lg:hidden flex justify-end" >
            <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick = {() => setIsMobileMenuOpen(false)
}> </div>
    < div className = "relative w-80 bg-white dark:bg-zinc-900 h-full shadow-xl p-6 overflow-y-auto animate-in slide-in-from-right duration-300" >
        <div className="flex justify-end mb-4" >
            <Button variant="icon" onClick = {() => setIsMobileMenuOpen(false)} aria - label={ uiText.buttons.closeSidebar }>
                <X size={ 20 } />
                    </Button>
                    </div>
                    < SidebarProfile profile = { profile } uiText = { uiText } onGoToAbout = {() => { onGoToAbout(); setIsMobileMenuOpen(false); }} compact />
                        <SidebarList 
                title={ isPost ? uiText.sections.latestBlog : uiText.sections.latestProjects }
items = { relatedItems }
onItemClick = {(i) => { onNavigate(i); setIsMobileMenuOpen(false); }}
onTagClick = {(t) => { onTagClick(t); setIsMobileMenuOpen(false); }}
isProject = {!isPost} 
              />
    </div>
    </div>
        )}

<article className="min-w-0" >
    <header className="mb-10 border-b border-zinc-200 dark:border-zinc-800 pb-10" >
        <div className="flex flex-wrap gap-3 text-xs font-mono text-zinc-500 mb-6" >
        {
            isPost?(
                <>
            <span className="flex items-center gap-1" > <Calendar size={ 12 } /> {item.date}</span >
                <span>•</span>
                    < span className = "flex items-center gap-1" > <Clock size={ 12 } /> {item.readTime}</span >
                        </>
              ) : (
    <span className= "bg-zinc-100 dark:bg-zinc-800 px-2 py-0.5 rounded text-zinc-600 dark:text-zinc-400" > { item.year } </span>
              )}
</div>

    < h1 className = "text-3xl sm:text-4xl font-extrabold text-zinc-900 dark:text-zinc-100 mb-6 tracking-tight leading-tight" >
        { item.title }
        </h1>

{
    item.tags && (
        <div className="flex flex-wrap gap-2 mb-6" >
            { item.tags.map(tag => <Tag key={ tag } onClick = {() => onTagClick(tag)} > { tag } </Tag>)
}
</div>
            )}

<p className="text-xl text-zinc-600 dark:text-zinc-400 leading-relaxed" >
    { item.desc }
    </p>

{
    !isPost && (
        <div className="flex gap-4 mt-8" >
            <a href={ item.link } className = "inline-flex items-center gap-2 px-4 py-2 bg-zinc-900 dark:bg-zinc-100 text-white dark:text-zinc-900 rounded-lg font-medium text-sm hover:opacity-90 transition-opacity" >
                <ExternalLink size={ 16 } /> {uiText.buttons.liveDemo}
                    </a>
                    < a href = { item.repo } className = "inline-flex items-center gap-2 px-4 py-2 border border-zinc-300 dark:border-zinc-700 text-zinc-700 dark:text-zinc-300 rounded-lg font-medium text-sm hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors" >
                        <Code2 size={ 16 } /> {uiText.buttons.viewCode}
                            </a>
                            </div>
            )
}
</header>

    < div className = "prose prose-zinc dark:prose-invert max-w-none" >
    {
        isPost?(
              <>
        <p className="text-zinc-700 dark:text-zinc-300 leading-7 mb-6 whitespace-pre-line" >
            { item.content }
            </p>
            < div className = "bg-zinc-50 dark:bg-[#161618] border border-zinc-200 dark:border-zinc-800 rounded-lg p-4 my-8 overflow-x-auto" >
                <pre className="font-mono text-sm text-blue-600 dark:text-blue-300" >
                    {`// Code example placeholder
function Hello() {
  return <div>Hello World</div>
}`}
</pre>
    </div>
    </>
            ) : (
    <>
    <h3 className= "text-xl font-bold text-zinc-900 dark:text-zinc-100 mb-4" > { uiText.sections.aboutProject } </h3>
    < p className = "text-zinc-700 dark:text-zinc-300 leading-7 mb-6" > { item.details } </p>

        < h3 className = "text-xl font-bold text-zinc-900 dark:text-zinc-100 mb-4" > { uiText.sections.technologies } </h3>
            < ul className = "list-disc list-inside text-zinc-700 dark:text-zinc-300 space-y-2 mb-8" >
                <li>Framework: { item.tags[0] } </li>
                    < li > Styling: Tailwind CSS </li>
                        < li > Deployment: Vercel / Netlify </li>
                            </ul>

                            < div className = "bg-zinc-50 dark:bg-zinc-900/50 border border-zinc-200 dark:border-zinc-800 rounded-xl p-12 flex items-center justify-center text-zinc-500 mb-8" >
                                <span className="text-sm italic" > { uiText.sections.screenshot } </span>
                                    </div>
                                    </>
            )}
</div>
    </article>
    </div>
    </div>
  );
};

// --- 6. MAIN APP COMPONENT ---

export default function App() {
    const [activeTab, setActiveTab] = useState('home');
    const [selectedItemId, setSelectedItemId] = useState(null);
    const [selectedType, setSelectedType] = useState(null);

    const [isDark, setIsDark] = useState(true);
    const [lang, setLang] = useState('en');

    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);

    const [selectedTag, setSelectedTag] = useState(null);
    const [searchText, setSearchText] = useState('');

    useEffect(() => {
        if (isDark) document.documentElement.classList.add('dark');
        else document.documentElement.classList.remove('dark');
    }, [isDark]);

    useEffect(() => {
        const loadData = async () => {
            setLoading(true);
            try {
                const response = await mockApiCall(lang);
                setData(response);
            } catch (error) {
                console.error("API Error", error);
            } finally {
                setLoading(false);
            }
        };
        loadData();
    }, [lang]);

    const handleNavigate = (tab) => {
        setActiveTab(tab);
        setSelectedItemId(null);
        setSelectedType(null);
        setSelectedTag(null);
        setSearchText('');
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    const handleItemClick = (item, type) => {
        setSelectedItemId(item.id);
        setSelectedType(type);
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    const handleTagClick = (tag, type) => {
        if (selectedItemId) {
            setSelectedItemId(null);
            setSelectedType(null);
        }
        setActiveTab(type === 'post' ? 'blog' : 'projects');
        setSelectedTag(tag);
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    const clearFilters = () => {
        setSelectedTag(null);
        setSearchText('');
    };

    const toggleTheme = () => setIsDark(!isDark);
    const toggleLang = () => setLang(prev => prev === 'en' ? 'pt' : 'en');

    if (loading || !data) {
        return (
            <div className= {`min-h-screen flex flex-col items-center justify-center gap-4 ${isDark ? 'bg-[#111111] text-[#EDEDED]' : 'bg-white text-zinc-900'}`
    }>
        <Loader2 className="animate-spin" size = { 32} />
            <span className="text-sm font-mono animate-pulse" > { UI_CONFIG[lang].buttons.loading } </span>
                </div>
    );
}

const ui = UI_CONFIG[lang];

const selectedItem = selectedItemId
    ? (selectedType === 'post'
        ? data.posts.find(p => p.id === selectedItemId)
        : data.projects.find(p => p.id === selectedItemId))
    : null;

const renderMainContent = () => {
    if (selectedItem) {
        const relatedItems = selectedType === 'post'
            ? data.posts.filter(p => p.id !== selectedItem.id).slice(0, 3)
            : data.projects.filter(p => p.id !== selectedItem.id).slice(0, 3);

        return (
            <DetailView 
          item= { selectedItem }
        type = { selectedType }
        onBack = {() => { setSelectedItemId(null); setSelectedType(null); }}
onNavigate = {(item) => handleItemClick(item, selectedType)}
onGoToAbout = {() => handleNavigate('sobre')}
onTagClick = {(tag) => handleTagClick(tag, selectedType)}
profile = { data.profile }
uiText = { ui }
relatedItems = { relatedItems }
    />
      );
    }

switch (activeTab) {
    case 'home':
        return (
            <>
            <Hero 
              profile= { data.profile }
        uiText = { ui }
        onNavigate = {(dest) => {
            if (dest === 'blog' || dest === 'projetos') handleNavigate(dest);
            else handleNavigate(dest);
        }
}
            />

    < section className = "mb-16 animate-in slide-in-from-bottom-4 duration-500" >
        <h2 className="text-xs font-bold text-zinc-500 uppercase tracking-wider mb-6" > { ui.sections.latestBlog } </h2>
            < div className = "space-y-4" >
            {
                data.posts.slice(0, 2).map(post => (
                    <ContentCard 
                    key= { post.id }
                    title = { post.title }
                    desc = { post.desc }
                    meta1 = {< span className = "flex items-center gap-1" > <Calendar size={ 12} /> { post.date } </span>}
meta2 = {< span className = "flex items-center gap-1" > <Clock size={ 12 } />{post.readTime}</span >}
tags = { post.tags }
onClick = {() => handleItemClick(post, 'post')}
onTagClick = {(tag) => handleTagClick(tag, 'post')}
actionText = { ui.buttons.readMore }
    />
                ))}
</div>
    </section>

    < section className = "mb-16 animate-in slide-in-from-bottom-8 duration-500 delay-75" >
        <h2 className="text-xs font-bold text-zinc-500 uppercase tracking-wider mb-6" > { ui.sections.latestProjects } </h2>
            < div className = "space-y-4" >
            {
                data.projects.map(project => (
                    <ContentCard 
                    key= { project.id }
                    title = { project.title }
                    desc = { project.desc }
                    meta1 = {< span className = "bg-zinc-100 dark:bg-zinc-800 px-2 py-0.5 rounded text-zinc-600 dark:text-zinc-400" > { project.year } </span>}
tags = { project.tags }
onClick = {() => handleItemClick(project, 'project')}
onTagClick = {(tag) => handleTagClick(tag, 'project')}
actionText = { ui.buttons.viewDetails }
    />
                ))}
</div>
    </section>

    < ContactSection uiText = { ui } profile = { data.profile } />
        </>
        );
      
      case 'sobre':
return <About data={ data } uiText = { ui } />;
      
      case 'blog':
return (
    <ListView 
            title= { ui.sections.blog }
items = { data.posts }
type = "post"
onNavigate = {(item) => handleItemClick(item, 'post')}
onTagClick = {(tag) => handleTagClick(tag, 'post')}
selectedTag = { selectedTag }
filterText = { searchText }
setFilterText = { setSearchText }
onClearFilters = { clearFilters }
uiText = { ui }
    />
        );

      case 'projetos':
return (
    <ListView 
            title= { ui.sections.projects }
items = { data.projects }
type = "project"
onNavigate = {(item) => handleItemClick(item, 'project')}
onTagClick = {(tag) => handleTagClick(tag, 'project')}
selectedTag = { selectedTag }
filterText = { searchText }
setFilterText = { setSearchText }
onClearFilters = { clearFilters }
uiText = { ui }
    />
        );

      case 'contato':
return <ContactSection uiText={ ui } profile = { data.profile } />;
        
      default:
return null;
    }
  };

return (
    <div className= {`min-h-screen font-sans selection:bg-blue-500/30 transition-colors duration-300 ${isDark ? 'bg-[#111111] text-[#EDEDED]' : 'bg-white text-zinc-900'}`}>
        <div className="max-w-[900px] mx-auto px-6 border-x border-zinc-100 dark:border-zinc-900/50 min-h-screen" >
            <NavBar 
          activeTab={ activeTab }
setActiveTab = { handleNavigate }
onClearFilters = { clearFilters }
isDark = { isDark }
toggleTheme = { toggleTheme }
lang = { lang }
toggleLang = { toggleLang }
navLabels = { ui.nav }
uiText = { ui }
    />

    <main className="pb-20" >
        { renderMainContent() }
        </main>

        < footer className = "mt-auto py-10 border-t border-zinc-200 dark:border-zinc-900 flex flex-col sm:flex-row justify-between items-center text-zinc-500 text-sm gap-4" >
            <div>& copy; { new Date().getFullYear() } { data.profile.name }.</div>
                < SocialLinks links = { data.profile.socialLinks } />
                    </footer>
                    </div>
                    </div>
  );
}
