// @ts-nocheck
import { Show } from 'solid-js';
import { useNavigate, useParams } from '@solidjs/router';
import { SiteLayout } from '../../components/layouts/SiteLayout';
import { DetailView } from '../../components/organisms/DetailView';
import { useTheme } from '../../stores/theme';
import { useI18n } from '../../stores/i18n';
import { usePortfolio } from '../../stores/content';
import { Skeleton } from '../../components/atoms/Skeleton';

export default function ProjectDetailPage() {
  const params = useParams();
  const { isDark, toggleTheme } = useTheme();
  const { lang, toggleLang, ui } = useI18n();
  const { data } = usePortfolio();
  const navigate = useNavigate();

  const projectFromId = () => data()?.projects.find((p) => String(p.id) === params.id);

  return (
    <SiteLayout ui={ui()} lang={lang()} toggleLang={toggleLang} isDark={isDark()} toggleTheme={toggleTheme} data={data()}>
      <Show
        when={!data.loading}
        fallback={
          <div class="space-y-4 py-12">
            <Skeleton class="h-4 w-32" />
            <Skeleton class="h-10 w-3/4" />
            <Skeleton class="h-6 w-2/3" />
            <Skeleton class="h-64 w-full rounded-xl" />
          </div>
        }
      >
        <Show when={projectFromId()} fallback={<div class="py-20 text-center text-zinc-500">Project not found.</div>}>
          <DetailView
            selectedItemId={projectFromId().id}
            selectedType="project"
            data={data()}
            ui={ui()}
            onBack={() => navigate('/projects')}
            onGoToAbout={() => navigate('/about')}
            onItemClick={(item) => navigate(`/projects/${item.id}`)}
            onTagClick={() => navigate('/projects')}
          />
        </Show>
      </Show>
    </SiteLayout>
  );
}
