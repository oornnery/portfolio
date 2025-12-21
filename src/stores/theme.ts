import { createSignal, createEffect, onMount } from 'solid-js';

const [isDark, setIsDark] = createSignal(true);
let effectSetup = false;

export const useTheme = () => {
  // Setup the DOM effect only once, inside a component context
  if (!effectSetup) {
    effectSetup = true;
    onMount(() => {
      createEffect(() => {
        const root = document.documentElement;
        if (isDark()) root.classList.add('dark');
        else root.classList.remove('dark');
      });
    });
  }

  return {
    isDark,
    toggleTheme: () => setIsDark((prev) => !prev)
  };
};
