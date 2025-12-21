import type { Language, PortfolioData } from '../types/portfolio';

const BASE_PROFILE = {
  name: 'Fabio Souza',
  location: 'São Paulo, Brazil',
  email: 'fabio@example.com',
  phone: '+55 11 99999-9999',
  socialLinks: [
    { network: 'github', url: 'http://github.com/oornnery/' },
    { network: 'linkedin', url: '#' },
    { network: 'twitter', url: '#' },
    { network: 'whatsapp', url: 'https://wa.me/5511999999' },
    { network: 'email', url: 'mailto:fabio@example.com' }
  ]
};

const EN_DATA: PortfolioData = {
  profile: {
    ...BASE_PROFILE,
    greeting: "Hi, I'm dev Fabio.",
    role: 'VoIP Engineer & DevOps',
    shortBio: 'Specializing in SIP, networking, and automation. Enhancing reliability in telecom environments.',
    longBio: 'Experienced telecommunications engineer with a strong focus on voice and data services. Specialized in technical support for SIP Trunk, SIP Link, PBX, and Call Center services. Proficient in service monitoring, log analysis, and automation using tools like Zabbix, Grafana, Splunk, and Python 3.'
  },
  skills: ['Git', 'React.js', 'FastAPI', 'SIP', 'Networking', 'DevOps', 'Zabbix', 'Grafana', 'Python 3', 'Splunk'],
  experience: [
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
  ],
  education: [
    { id: 1, title: 'Universidade Anhembi Morumbi', subtitle: "Bachelor's, Information Security", date: '2021 — 2023' },
    { id: 2, title: 'UNINOVE', subtitle: 'IT Management, Information Technology', date: '2018 — 2020' }
  ],
  certificates: [
    { id: 1, title: 'LPIC-1: Linux Administrator', subtitle: 'Linux Professional Institute', date: '2023' },
    { id: 2, title: 'Zabbix Certified Specialist', subtitle: 'Zabbix LLC', date: '2022' }
  ],
  projects: [
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
  ],
  posts: [
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
};

const PT_DATA: PortfolioData = {
  profile: {
    ...BASE_PROFILE,
    greeting: 'Olá, Eu sou o dev Fabio.',
    role: 'Engenheiro VoIP & DevOps',
    shortBio: 'Especializado em SIP, redes e automação. Aumentando a confiabilidade em ambientes de telecomunicações.',
    longBio: 'Engenheiro de telecomunicações experiente com forte foco em serviços de voz e dados. Especializado em suporte técnico para serviços SIP Trunk, SIP Link, PBX e Call Center. Proficiente em monitoramento de serviços, análise de logs e automação utilizando ferramentas como Zabbix, Grafana, Splunk e Python 3.'
  },
  skills: ['Git', 'React.js', 'FastAPI', 'SIP', 'Networking', 'DevOps', 'Zabbix', 'Grafana', 'Python 3', 'Splunk'],
  experience: [
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
  education: [
    { id: 1, title: 'Universidade Anhembi Morumbi', subtitle: 'Graduação, Segurança da informação', date: '2021 — 2023' },
    { id: 2, title: 'UNINOVE', subtitle: 'Gestão Tecnologia da Informação, Tecnologia da Informação', date: '2018 — 2020' }
  ],
  certificates: [
    { id: 1, title: 'LPIC-1: Linux Administrator', subtitle: 'Linux Professional Institute', date: '2023' },
    { id: 2, title: 'Zabbix Certified Specialist', subtitle: 'Zabbix LLC', date: '2022' }
  ],
  projects: [
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
  posts: [
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
};

const PORTFOLIO_DATA: Record<Language, PortfolioData> = { en: EN_DATA, pt: PT_DATA };

export const mockApiCall = (lang: Language): Promise<PortfolioData> => new Promise((resolve) => {
  setTimeout(() => {
    resolve(PORTFOLIO_DATA[lang] ?? EN_DATA);
  }, 1000); // 1 segundo para visualizar o skeleton
});

export const fetchPortfolioData = async (lang: Language) => mockApiCall(lang);
