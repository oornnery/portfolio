// @ts-nocheck

export const Tag = (props) => {
  const sizes = {
    small: 'text-[9px] px-1.5 py-0.5',
    normal: 'text-[10px] px-2 py-1'
  };

  const baseClasses = () => `font-mono uppercase tracking-wider rounded border transition-colors ${sizes[props.size || 'normal']}`;
  const interactiveClasses = () => (props.onClick ? 'cursor-pointer hover:bg-zinc-200 dark:hover:bg-zinc-800 hover:text-zinc-900 dark:hover:text-zinc-300' : '');
  const activeClasses = () => props.active
    ? 'bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-500/20'
    : 'text-zinc-500 dark:text-zinc-400 bg-zinc-100 dark:bg-zinc-900 border-zinc-200 dark:border-zinc-800';

  return (
    <span 
      onClick={(e) => {
        if(props.onClick) { e.stopPropagation(); props.onClick(); }
      }}
      class={`${baseClasses()} ${activeClasses()} ${interactiveClasses()}`}
    >
      {props.children}
    </span>
  );
};
