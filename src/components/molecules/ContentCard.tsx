// @ts-nocheck
import { Show, For } from 'solid-js';
import { ArrowRight } from 'lucide-solid';
import { Tag } from '../atoms/Tag';

export const ContentCard = (props) => (
  <div 
    onClick={() => props.onClick && props.onClick()}
    class="group cursor-pointer bg-white dark:bg-zinc-900/30 rounded-lg p-6 hover:bg-zinc-50 dark:hover:bg-zinc-900/50 transition-all border border-zinc-100 dark:border-transparent shadow-sm dark:shadow-none"
  >
    <div class="flex items-center gap-3 text-xs text-zinc-500 mb-3 font-mono">
      {props.meta1}
      <Show when={props.meta2}>
        <span>•</span>
        {props.meta2}
      </Show>
    </div>
    
    <h3 class="text-xl font-bold text-zinc-900 dark:text-zinc-100 mb-2 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
      {props.title}
    </h3>
    
    <Show when={props.tags}>
      <div class="mb-3">
        <div class="flex flex-wrap gap-2">
          <For each={props.tags}>
            {(tag) => <Tag onClick={() => props.onTagClick && props.onTagClick(tag)}>{tag}</Tag>}
          </For>
        </div>
      </div>
    </Show>

    <p class="text-zinc-600 dark:text-zinc-400 leading-relaxed text-sm mb-4 line-clamp-3">
      {props.desc}
    </p>

    <Show when={props.actionText}>
      <div class="flex items-center text-sm text-blue-600 dark:text-blue-400 font-medium opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all duration-300">
        {props.actionText} <ArrowRight size={14} class="ml-1" />
      </div>
    </Show>
  </div>
);
