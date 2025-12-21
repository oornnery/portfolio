// @ts-nocheck
import { Show, For } from 'solid-js';
import { GraduationCap, Award, MapPin } from 'lucide-solid';
import { SiteLayout } from '../components/layouts/SiteLayout';
import { SocialLinks } from '../components/atoms/SocialLinks';
import { Tag } from '../components/atoms/Tag';
import { TimelineItem } from '../components/molecules/TimelineItem';
import { Skeleton } from '../components/atoms/Skeleton';
import { useTheme } from '../stores/theme';
import { useI18n } from '../stores/i18n';
import { usePortfolio } from '../stores/content';

export default function AboutPage() {
  const { isDark, toggleTheme } = useTheme();
  const { lang, toggleLang, ui } = useI18n();
  const { data } = usePortfolio();
  const portfolio = () => data();

  return (
    <SiteLayout ui={ui()} lang={lang()} toggleLang={toggleLang} isDark={isDark()} toggleTheme={toggleTheme} data={data()}>
      <Show
        when={!data.loading && portfolio()}
        fallback={
          <div class="max-w-2xl mx-auto space-y-6 py-12">
            <Skeleton class="h-8 w-2/3" />
            <Skeleton class="h-4 w-40" />
            <Skeleton class="h-4 w-56" />
            <Skeleton class="h-4 w-full" />
            <Skeleton class="h-4 w-5/6" />
            <div class="grid grid-cols-2 gap-3">
              <Skeleton class="h-8" />
              <Skeleton class="h-8" />
              <Skeleton class="h-8" />
              <Skeleton class="h-8" />
            </div>
            <Skeleton class="h-5 w-32" />
            <Skeleton class="h-24 w-full" />
            <Skeleton class="h-5 w-32" />
            <Skeleton class="h-24 w-full" />
          </div>
        }
      >
        <section class="animate-in fade-in duration-500 max-w-2xl mx-auto">
          <div class="flex flex-col gap-6 mb-12">
            <div>
              <h1 class="text-3xl font-bold text-zinc-900 dark:text-zinc-100 mb-2">{portfolio().profile.name}</h1>
              <p class="text-lg text-zinc-600 dark:text-zinc-400">{portfolio().profile.role}</p>
              <div class="flex items-center gap-2 text-zinc-500 text-sm mt-2">
                <MapPin size={14} />
                <a href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(portfolio().profile.location)}`} target="_blank" rel="noreferrer" class="hover:text-zinc-900 dark:hover:text-zinc-100 transition-colors">{portfolio().profile.location}</a>
              </div>
            </div>
            <div class="prose prose-zinc dark:prose-invert">
              <p class="text-zinc-600 dark:text-zinc-300 leading-relaxed">{portfolio().profile.longBio}</p>
            </div>
            <SocialLinks links={portfolio().profile.socialLinks} />
          </div>

          <div class="space-y-16">
            <div>
              <h2 class="text-xs font-bold text-zinc-500 uppercase tracking-wider mb-6">{ui().sections.skills}</h2>
              <div class="flex flex-wrap gap-2">
                <For each={portfolio().skills}>{(skill) => <Tag>{skill}</Tag>}</For>
              </div>
            </div>
            <div>
              <h2 class="text-xs font-bold text-zinc-500 uppercase tracking-wider mb-8">{ui().sections.experience}</h2>
              <div class="space-y-2">
                <For each={portfolio().experience}>
                  {(job, i) => <TimelineItem {...job} isLast={i() === portfolio().experience.length - 1} />}
                </For>
              </div>
            </div>
            <div>
              <h2 class="text-xs font-bold text-zinc-500 uppercase tracking-wider mb-6 flex items-center gap-2"><GraduationCap size={16} /> {ui().sections.education}</h2>
              <div class="space-y-2">
                <For each={portfolio().education}>
                  {(edu, i) => <TimelineItem {...edu} isLast={i() === portfolio().education.length - 1} />}
                </For>
              </div>
            </div>
            <div>
              <h2 class="text-xs font-bold text-zinc-500 uppercase tracking-wider mb-6 flex items-center gap-2"><Award size={16} /> {ui().sections.certificates}</h2>
              <div class="space-y-2">
                <For each={portfolio().certificates}>
                  {(cert, i) => <TimelineItem {...cert} isLast={i() === portfolio().certificates.length - 1} />}
                </For>
              </div>
            </div>
          </div>
        </section>
      </Show>
    </SiteLayout>
  );
}
