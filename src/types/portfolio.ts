export type Language = 'en' | 'pt';

export type SocialNetwork = 'github' | 'twitter' | 'linkedin' | 'mail' | 'email' | 'whatsapp' | string;

export interface SocialLink {
  network: SocialNetwork;
  url: string;
}

export interface Profile {
  name: string;
  greeting: string;
  role: string;
  shortBio: string;
  longBio: string;
  location: string;
  email: string;
  phone: string;
  socialLinks: SocialLink[];
}

export interface ExperienceItem {
  id: number;
  title: string;
  subtitle: string;
  date: string;
  location: string;
  description: string;
}

export interface EducationItem {
  id: number;
  title: string;
  subtitle: string;
  date: string;
}

export interface CertificateItem {
  id: number;
  title: string;
  subtitle: string;
  date: string;
}

export interface ProjectItem {
  id: number;
  title: string;
  desc: string;
  details: string;
  tags: string[];
  year: string;
  link: string;
  repo: string;
  type: 'project';
}

export interface PostItem {
  id: number;
  slug: string;
  title: string;
  desc: string;
  content: string;
  date: string;
  readTime: string;
  tags: string[];
  type: 'post';
}

export interface PortfolioData {
  profile: Profile;
  skills: string[];
  experience: ExperienceItem[];
  education: EducationItem[];
  certificates: CertificateItem[];
  projects: ProjectItem[];
  posts: PostItem[];
}

export interface UIConfig {
  nav: Record<'home' | 'about' | 'blog' | 'projects' | 'contact', string>;
  buttons: Record<string, string>;
  sections: Record<string, string>;
  placeholders: Record<string, string>;
  contact: { title: string; subtitle: string };
}
