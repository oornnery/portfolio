import { createSignal } from 'solid-js';
import { UI_CONFIG } from '../data/ui-config';
import type { Language } from '../types/portfolio';

// Export signal directly for use in other stores
export const [lang, setLang] = createSignal<Language>('en');

export const useI18n = () => ({
  lang,
  toggleLang: () => setLang((prev) => (prev === 'en' ? 'pt' : 'en')),
  ui: () => UI_CONFIG[lang()]
});
