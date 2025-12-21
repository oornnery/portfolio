// @ts-nocheck
import { Show, For } from 'solid-js';
import { useNavigate } from '@solidjs/router';
import { Calendar, Clock, User, ArrowRight } from 'lucide-solid';
import { Button } from '../components/atoms/Button';
import { SocialLinks } from '../components/atoms/SocialLinks';
import { ContentCard } from '../components/molecules/ContentCard';
import { ContactSection } from '../components/molecules/ContactSection';
import { SiteLayout } from '../components/layouts/SiteLayout';
import { Skeleton } from '../components/atoms/Skeleton';
import { useTheme } from '../stores/theme';
import { useI18n } from '../stores/i18n';
import { usePortfolio } from '../stores/content';

export default function HomePage() {
  const navigate = useNavigate();
  const { isDark, toggleTheme } = useTheme();
  const { lang, toggleLang, ui } = useI18n();
  const { data } = usePortfolio();
  const portfolio = () => data();

  return (
    <SiteLayout ui={ui()} lang={lang()} toggleLang={toggleLang} isDark={isDark()} toggleTheme={toggleTheme} data={portfolio()}> 
      <Show when={!data.loading && portfolio()} fallback={
        <div class="flex flex-col gap-10 py-12">
          <div class="bg-zinc-50 dark:bg-zinc-900/30 rounded-2xl p-8 border border-zinc-100 dark:border-transparent">
            <div class="flex flex-col md:flex-row gap-8 items-start">
              <Skeleton class="w-24 h-24 sm:w-32 sm:h-32 rounded-full" />
              <div class="flex-1 space-y-3">
                <Skeleton class="h-8 w-2/3" />
                <Skeleton class="h-4 w-1/3" />
                <Skeleton class="h-4 w-full" />
                <Skeleton class="h-4 w-5/6" />
                <div class="flex gap-3 mt-4">
                  <Skeleton class="h-10 w-28" />
                  <Skeleton class="h-10 w-28" />
                  <Skeleton class="h-10 w-24" />
                </div>
              </div>
            </div>
          </div>

          <div class="space-y-4">
            <Skeleton class="h-3 w-32" />
            <Skeleton class="h-24 w-full rounded-xl" />
            <Skeleton class="h-24 w-full rounded-xl" />
          </div>

          <div class="space-y-4">
            <Skeleton class="h-3 w-36" />
            <Skeleton class="h-24 w-full rounded-xl" />
            <Skeleton class="h-24 w-full rounded-xl" />
          </div>
        </div>
      }>
        <section class="mb-16 animate-in fade-in duration-500">
          <div class="bg-zinc-50 dark:bg-zinc-900/30 rounded-2xl p-8 flex flex-col md:flex-row gap-8 items-start border border-zinc-100 dark:border-transparent">
            <div class="shrink-0">
              <div class="w-24 h-24 sm:w-32 sm:h-32 bg-zinc-200 dark:bg-zinc-800 rounded-full flex items-center justify-center text-zinc-400 dark:text-zinc-500 overflow-hidden border-2 border-white dark:border-zinc-700/50">
                <User size={48} />
              </div>
            </div>
            <div class="flex-1">
              <h1 class="text-3xl sm:text-4xl font-extrabold tracking-tight text-zinc-900 dark:text-zinc-100 mb-2">{portfolio().profile.greeting}</h1>
              <p class="text-sm text-zinc-500 font-mono mb-4">{portfolio().profile.role}</p>
              <p class="text-lg text-zinc-600 dark:text-zinc-400 leading-relaxed mb-6 max-w-2xl">{portfolio().profile.shortBio}</p>
              <SocialLinks links={portfolio().profile.socialLinks} class="mb-8" />
              <div class="flex flex-wrap gap-3 items-center">
                <Button onClick={() => navigate('/about')}><User size={16} /> {ui().buttons.about}</Button>
                <Button variant="secondary" onClick={() => navigate('/projects')}>{ui().buttons.projects}</Button>
                <Button variant="ghost" onClick={() => navigate('/blog')}>{ui().buttons.blog} <ArrowRight size={16} /></Button>
              </div>
            </div>
          </div>
        </section>

        <section class="mb-16 animate-in slide-in-from-bottom-4 duration-500">
          <h2 class="text-xs font-bold text-zinc-500 uppercase tracking-wider mb-6">{ui().sections.latestBlog}</h2>
          <div class="space-y-4">
            <For each={portfolio().posts.slice(0, 2)}>
              {(post) => (
                <ContentCard 
                  title={post.title}
                  desc={post.desc}
                  meta1={<span class="flex items-center gap-1"><Calendar size={12}/>{post.date}</span>}
                  meta2={<span class="flex items-center gap-1"><Clock size={12}/>{post.readTime}</span>}
                  tags={post.tags}
                  onClick={() => navigate(`/blog/${post.slug}`)}
                  onTagClick={() => navigate('/blog')}
                  actionText={ui().buttons.readMore}
                />
              )}
            </For>
          </div>
        </section>

        <section class="mb-16 animate-in slide-in-from-bottom-8 duration-500 delay-75">
          <h2 class="text-xs font-bold text-zinc-500 uppercase tracking-wider mb-6">{ui().sections.latestProjects}</h2>
          <div class="space-y-4">
            <For each={portfolio().projects.slice(0, 2)}>
              {(project) => (
                <ContentCard 
                  title={project.title}
                  desc={project.desc}
                  meta1={<span class="bg-zinc-100 dark:bg-zinc-800 px-2 py-0.5 rounded text-zinc-600 dark:text-zinc-400">{project.year}</span>}
                  tags={project.tags}
                  onClick={() => navigate(`/projects/${project.id}`)}
                  onTagClick={() => navigate('/projects')}
                  actionText={ui().buttons.viewDetails}
                />
              )}
            </For>
          </div>
        </section>
        
        <ContactSection uiText={ui()} profile={portfolio().profile} />
      </Show>
    </SiteLayout>
  );
}
