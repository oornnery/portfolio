// @ts-nocheck
import { createSignal, For, Show } from 'solid-js';
import { useLocation, useNavigate } from '@solidjs/router';
import { Github, Globe, Menu, Moon, Sun, X } from 'lucide-solid';
import { Button } from '../atoms/Button';

const navItems = [
  { key: 'home', href: '/', match: '/' },
  { key: 'about', href: '/about', match: '/about' },
  { key: 'blog', href: '/blog', match: '/blog' },
  { key: 'projects', href: '/projects', match: '/projects' },
  { key: 'contact', href: '/contact', match: '/contact' },
];

export const NavBar = (props) => {
  const [isMenuOpen, setIsMenuOpen] = createSignal(false);
  const location = useLocation();
  const navigate = useNavigate();

  const isActive = (match) => location.pathname === match || location.pathname.startsWith(match + '/');

  const handleNavClick = (href) => {
    navigate(href);
    setIsMenuOpen(false);
  };

  return (
    <div>
      <header class="flex justify-between items-center py-8 mb-12 sm:mb-20">
        <button
          class="text-xl font-bold tracking-tight cursor-pointer select-none z-50 relative"
          onClick={() => handleNavClick('/')}
        >
          fabio<span class="text-zinc-400 dark:text-zinc-600">.dev</span>
        </button>
        
        {/* Desktop Navigation */}
        <div class="hidden md:flex items-center gap-6">
          <nav class="flex gap-6 text-sm font-medium text-zinc-500 dark:text-zinc-400">
            <For each={navItems}>
              {(item) => (
                <button
                  onClick={() => handleNavClick(item.href)}
                  class={`transition-colors hover:text-zinc-900 dark:hover:text-zinc-100 ${isActive(item.match) ? 'text-zinc-900 dark:text-zinc-100 font-semibold' : ''}`}
                >
                  {props.navLabels[item.key]}
                </button>
              )}
            </For>
          </nav>

          <div class="w-px h-4 bg-zinc-300 dark:bg-zinc-800" />

          <div class="flex items-center gap-4">
            <Button variant="icon" onClick={props.toggleLang} class="text-xs font-mono font-bold flex gap-1 w-auto px-2">
              <Globe size={16} /> {props.lang.toUpperCase()}
            </Button>
            <Button variant="icon" onClick={props.toggleTheme}>
              {props.isDark ? <Sun size={18} /> : <Moon size={18} />}
            </Button>
            <a href="http://github.com/oornnery/" target="_blank" rel="noreferrer" class="text-zinc-500 hover:text-zinc-900 dark:hover:text-zinc-100 transition-colors">
              <Github size={18} />
            </a>
          </div>
        </div>

        {/* Mobile Menu Button */}
        <div class="md:hidden flex items-center gap-4">
           <Button variant="icon" onClick={() => setIsMenuOpen(true)} aria-label={props.uiText.buttons.openMenu}>
             <Menu size={24} />
           </Button>
        </div>
      </header>

      {/* Mobile Drawer */}
      <Show when={isMenuOpen()}>
        <div class="fixed inset-0 z-[100] md:hidden flex justify-end">
          <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={() => setIsMenuOpen(false)} />
          
          <div class="relative w-64 bg-white dark:bg-zinc-900 h-full shadow-2xl p-6 flex flex-col animate-in slide-in-from-right duration-300">
            <div class="flex justify-end mb-8">
              <Button variant="icon" onClick={() => setIsMenuOpen(false)} aria-label={props.uiText.buttons.closeMenu}>
                <X size={24} />
              </Button>
            </div>

            <nav class="flex flex-col gap-6 text-lg font-medium text-zinc-600 dark:text-zinc-400">
              <For each={navItems}>
                {(item) => (
                  <button
                    onClick={() => handleNavClick(item.href)}
                    class={`text-left transition-colors hover:text-zinc-900 dark:hover:text-zinc-100 ${isActive(item.match) ? 'text-zinc-900 dark:text-zinc-100 font-bold' : ''}`}
                  >
                    {props.navLabels[item.key]}
                  </button>
                )}
              </For>
            </nav>

            <div class="mt-auto pt-8 border-t border-zinc-200 dark:border-zinc-800 flex flex-col gap-6">
               <div class="flex items-center justify-between">
                  <span class="text-sm text-zinc-500">Theme</span>
                  <Button variant="icon" onClick={props.toggleTheme}>
                    {props.isDark ? <Sun size={18} /> : <Moon size={18} />}
                  </Button>
               </div>
               <div class="flex items-center justify-between">
                  <span class="text-sm text-zinc-500">Language</span>
                  <Button variant="icon" onClick={props.toggleLang} class="text-xs font-mono font-bold">
                    <Globe size={16} /> {props.lang.toUpperCase()}
                  </Button>
               </div>
               <div class="flex items-center justify-between">
                  <span class="text-sm text-zinc-500">Github</span>
                  <a href="http://github.com/oornnery/" target="_blank" rel="noreferrer" class="p-2 text-zinc-500 hover:text-zinc-900 dark:hover:text-zinc-100 transition-colors">
                    <Github size={18} />
                  </a>
               </div>
            </div>
          </div>
        </div>
      </Show>
    </div>
  );
};
