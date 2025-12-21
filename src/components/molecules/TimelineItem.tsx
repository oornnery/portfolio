// @ts-nocheck
import { Show } from 'solid-js';

export const TimelineItem = (props) => (
  <div class="relative pl-8 pb-12 group">
    <Show when={!props.isLast}>
      <div class="absolute left-0 top-2 h-full w-px bg-zinc-200 dark:bg-zinc-800" />
    </Show>
    <div class="absolute left-[-4px] top-2 w-2 h-2 rounded-full bg-zinc-300 dark:bg-zinc-700 border border-white dark:border-zinc-900 group-hover:bg-blue-500 transition-colors" />
    
    <div class="flex flex-col sm:flex-row sm:items-baseline justify-between mb-1">
      <h3 class="text-zinc-900 dark:text-zinc-100 font-medium text-lg">{props.title}</h3>
      <span class="text-xs font-mono text-zinc-500 shrink-0">{props.date}</span>
    </div>
    <div class="flex flex-wrap items-center gap-2 text-sm text-zinc-500 mb-3">
      <span class="font-medium text-zinc-700 dark:text-zinc-300">{props.subtitle}</span>
      <Show when={props.location}>
         <span class="text-zinc-400">•</span>
         <span>{props.location}</span>
      </Show>
    </div>
    <Show when={props.description}>
      <p class="text-sm text-zinc-600 dark:text-zinc-400 leading-relaxed text-justify">
        {props.description}
      </p>
    </Show>
  </div>
);
