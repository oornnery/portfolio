import type { UIConfig } from '../types/portfolio';

export const UI_CONFIG: Record<'en' | 'pt', UIConfig> = {
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
