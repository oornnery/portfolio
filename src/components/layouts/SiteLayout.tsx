// @ts-nocheck
import { Show } from 'solid-js';
import { SocialLinks } from '../atoms/SocialLinks';
import { NavBar } from '../organisms/NavBar';

export const SiteLayout = (props) => (
  <div class={`min-h-screen font-sans selection:bg-blue-500/30 transition-colors duration-300 ${props.isDark ? 'bg-[#111111] text-[#EDEDED]' : 'bg-white text-zinc-900'}`}>
    <div class="max-w-[900px] mx-auto px-6 border-x border-zinc-100 dark:border-zinc-900/50 min-h-screen flex flex-col">
      <NavBar 
        navLabels={props.ui.nav}
        uiText={props.ui}
        lang={props.lang}
        toggleLang={props.toggleLang}
        isDark={props.isDark}
        toggleTheme={props.toggleTheme}
      />

      <main class="pb-20 flex-1">{props.children}</main>

      <footer class="mt-auto py-10 border-t border-zinc-200 dark:border-zinc-900 flex flex-col sm:flex-row justify-between items-center text-zinc-500 text-sm gap-4">
        <Show when={props.data}>
          <div>&copy; {new Date().getFullYear()} {props.data.profile.name}.</div>
          <SocialLinks links={props.data.profile.socialLinks} />
        </Show>
      </footer>
    </div>
  </div>
);
