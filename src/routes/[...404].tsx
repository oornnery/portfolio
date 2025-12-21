// @ts-nocheck
import { Title } from '@solidjs/meta';
import { HttpStatusCode, useNavigate } from '@solidjs/router';
import { Loader2, Home, ArrowLeft } from 'lucide-solid';
import { Show } from 'solid-js';
import { SiteLayout } from '../components/layouts/SiteLayout';
import { Button } from '../components/atoms/Button';
import { useTheme } from '../stores/theme';
import { useI18n } from '../stores/i18n';
import { usePortfolio } from '../stores/content';

const COPY = {
  en: {
    title: 'Page Not Found',
    desc: "We couldn't find the page you're looking for.",
    back: 'Go back',
    home: 'Go home'
  },
  pt: {
    title: 'Página não encontrada',
    desc: 'Não conseguimos encontrar a página que você procura.',
    back: 'Voltar',
    home: 'Ir para início'
  }
};

export default function NotFound() {
  const navigate = useNavigate();
  const { isDark, toggleTheme } = useTheme();
  const { lang, toggleLang, ui } = useI18n();
  const { data } = usePortfolio();
  const text = () => COPY[lang()] ?? COPY.en;

  return (
    <SiteLayout ui={ui()} lang={lang()} toggleLang={toggleLang} isDark={isDark()} toggleTheme={toggleTheme} data={data()}>
      <Title>{text().title}</Title>
      <HttpStatusCode code={404} />
      <Show
        when={!data.loading}
        fallback={
          <div class="flex flex-col items-center justify-center py-20 gap-4">
            <Loader2 class="animate-spin" size={32} />
            <span class="text-sm font-mono animate-pulse">{ui().buttons.loading}</span>
          </div>
        }
      >
        <div class="min-h-[60vh] flex flex-col items-center justify-center text-center gap-6">
          <div class="flex items-center gap-3 text-sm text-zinc-500">
            <span class="px-2 py-1 rounded-full bg-zinc-100 dark:bg-zinc-900 font-mono border border-zinc-200 dark:border-zinc-800">404</span>
            <span class="uppercase tracking-widest text-xs">{text().title}</span>
          </div>
          <h1 class="text-3xl sm:text-4xl font-extrabold text-zinc-900 dark:text-zinc-100">{text().title}</h1>
          <p class="text-zinc-600 dark:text-zinc-400 max-w-xl">{text().desc}</p>
          <div class="flex flex-wrap gap-3 justify-center">
            <Button variant="secondary" onClick={() => navigate(-1)}>
              <ArrowLeft size={16} /> {text().back}
            </Button>
            <Button onClick={() => navigate('/')}>
              <Home size={16} /> {text().home}
            </Button>
          </div>
        </div>
      </Show>
    </SiteLayout>
  );
}
