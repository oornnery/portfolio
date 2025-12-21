// @ts-nocheck
import { Show } from 'solid-js';
import { SiteLayout } from '../components/layouts/SiteLayout';
import { ContactSection } from '../components/molecules/ContactSection';
import { useTheme } from '../stores/theme';
import { useI18n } from '../stores/i18n';
import { usePortfolio } from '../stores/content';
import { Skeleton } from '../components/atoms/Skeleton';

export default function ContactPage() {
  const { isDark, toggleTheme } = useTheme();
  const { lang, toggleLang, ui } = useI18n();
  const { data } = usePortfolio();
  const portfolio = () => data();

  return (
    <SiteLayout ui={ui()} lang={lang()} toggleLang={toggleLang} isDark={isDark()} toggleTheme={toggleTheme} data={portfolio()}>
      <Show
        when={!data.loading && portfolio()}
        fallback={
          <div class="space-y-4 py-12">
            <Skeleton class="h-8 w-48" />
            <Skeleton class="h-4 w-64" />
            <Skeleton class="h-96 w-full rounded-2xl" />
          </div>
        }
      >
        <ContactSection uiText={ui()} profile={portfolio().profile} />
      </Show>
    </SiteLayout>
  );
}