// @ts-nocheck
import { For, Show } from 'solid-js';
import { ArrowRight, User } from 'lucide-solid';
import { SocialLinks } from '../atoms/SocialLinks';
import { Tag } from '../atoms/Tag';

export const Sidebar = (props) => (
  <aside class="space-y-8 animate-in fade-in slide-in-from-left-4 duration-700 delay-150">
    <div 
      onClick={() => props.onGoToAbout && props.onGoToAbout()}
      class="group cursor-pointer transition-all bg-white dark:bg-zinc-900/30 rounded-xl p-6 border border-zinc-100 dark:border-transparent shadow-sm dark:shadow-none"
    >
      <div class="w-16 h-16 bg-zinc-200 dark:bg-zinc-800 rounded-full mb-4 flex items-center justify-center text-zinc-400 dark:text-zinc-500 overflow-hidden">
        <User size={32} />
      </div>
      <h3 class="font-bold text-zinc-900 dark:text-zinc-100 mb-1">{props.profile.greeting}</h3>
      <p class="text-xs text-zinc-500 font-mono mb-3">{props.profile.role}</p>
      <p class="text-sm text-zinc-600 dark:text-zinc-400 leading-relaxed mb-4">
        {props.profile.shortBio}
      </p>

      <SocialLinks links={props.profile.socialLinks} class="mb-4" />
      
      <div class="flex items-center text-sm text-blue-600 dark:text-blue-400 font-medium opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all duration-300">
        {props.uiText.buttons.seeMore} <ArrowRight size={14} class="ml-1" />
      </div>
    </div>

    {/* Dynamic List */}
    <Show when={props.items && props.items.length > 0}>
      <div>
        <h4 class="text-xs font-bold text-zinc-500 uppercase tracking-wider mb-6">
          {props.title}
        </h4>
        <div class="space-y-4">
          <For each={props.items}>
            {(item) => (
              <div 
                onClick={() => props.onItemClick && props.onItemClick(item)}
                class="group cursor-pointer bg-white dark:bg-zinc-900/30 p-4 rounded-xl border border-zinc-100 dark:border-transparent shadow-sm dark:shadow-none hover:bg-zinc-50 dark:hover:bg-zinc-900/50 transition-all"
              >
                <h5 class="text-sm text-zinc-700 dark:text-zinc-300 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors line-clamp-2 leading-snug mb-2 font-medium">
                  {item.title}
                </h5>
                <div class="flex justify-between items-center mb-2">
                   <span class="text-xs text-zinc-500 dark:text-zinc-600 font-mono">{props.isProject ? item.year : item.date}</span>
                </div>
                 <Show when={item.tags}>
                    <div class="flex flex-wrap gap-1.5">
                      <For each={item.tags.slice(0, 3)}>
                        {(tag) => <Tag size="small" onClick={() => props.onTagClick(tag)}>{tag}</Tag>}
                      </For>
                    </div>
                 </Show>
              </div>
            )}
          </For>
        </div>
      </div>
    </Show>
  </aside>
);
