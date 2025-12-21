// @ts-nocheck

export const Button = (props) => {
  const base = 'inline-flex items-center gap-2 rounded-lg font-medium text-sm transition-all focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed';
  const variants = {
    primary: 'bg-zinc-900 dark:bg-zinc-100 text-white dark:text-zinc-950 hover:bg-zinc-700 dark:hover:bg-zinc-300 focus:ring-zinc-900 dark:focus:ring-zinc-100 px-5 py-2.5',
    secondary: 'text-zinc-700 dark:text-zinc-300 border border-zinc-300 dark:border-zinc-700 hover:bg-zinc-100 dark:hover:bg-zinc-800 focus:ring-zinc-500 px-5 py-2.5',
    ghost: 'text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-white hover:bg-zinc-100 dark:hover:bg-zinc-800/50 px-4 py-2',
    link: 'text-blue-600 dark:text-blue-400 hover:underline p-0 h-auto font-normal',
    icon: 'p-2 hover:bg-zinc-100 dark:hover:bg-zinc-800 rounded-full text-zinc-500 hover:text-zinc-900 dark:hover:text-zinc-100'
  };

  return (
    <button
      class={`${base} ${variants[props.variant || 'primary']} ${props.class || ''}`}
      onClick={(event) => props.onClick && props.onClick(event)}
      aria-label={props['aria-label']}
    >
      {props.children}
    </button>
  );
};
