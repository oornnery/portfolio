// @ts-nocheck
import { For, Show } from 'solid-js';
import { Calendar, Clock, Search, X } from 'lucide-solid';
import { Tag } from '../atoms/Tag';
import { Button } from '../atoms/Button';
import { ContentCard } from '../molecules/ContentCard';

export const ListView = (props) => {
  const isPost = () => props.type === 'blog';
  const title = () => isPost() ? props.ui.sections.blog : props.ui.sections.projects;
  const items = () => isPost() ? props.filteredPosts : props.filteredProjects;
  const itemType = () => isPost() ? 'post' : 'project';

  return (
    <section class="animate-in fade-in duration-500">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between mb-8 gap-4">
        <h1 class="text-3xl font-bold text-zinc-900 dark:text-zinc-100">{title()}</h1>
        <div class="relative">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500" size={16} />
          <input 
            type="text" 
            placeholder={props.ui.placeholders.search}
            value={props.searchText}
            onInput={(e) => props.setSearchText(e.target.value)}
            class="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 text-zinc-900 dark:text-zinc-200 text-sm rounded-full pl-10 pr-4 py-2 focus:outline-none focus:border-zinc-400 dark:focus:border-zinc-600 w-full sm:w-64 placeholder:text-zinc-400 dark:placeholder:text-zinc-600 transition-colors"
          />
        </div>
      </div>

      <Show when={props.selectedTag}>
        <div class="flex items-center gap-2 mb-6 animate-in fade-in">
          <span class="text-sm text-zinc-500 dark:text-zinc-400">{props.ui.buttons.filteringBy}</span>
          <Tag active onClick={props.clearFilters}>
            <span class="flex items-center gap-1">{props.selectedTag} <X size={12} /></span>
          </Tag>
          <Button variant="link" onClick={props.clearFilters} class="text-xs">{props.ui.buttons.clearFilter}</Button>
        </div>
      </Show>

      <div class="grid gap-6">
        <Show when={items().length > 0} fallback={
          <div class="text-center py-20 border border-dashed border-zinc-200 dark:border-zinc-800 rounded-lg">
            <p class="text-zinc-500">{isPost() ? props.ui.placeholders.emptyBlog : props.ui.placeholders.emptyProjects}</p>
            <Button variant="link" onClick={props.clearFilters}>{props.ui.buttons.clearFilter}</Button>
          </div>
        }>
          <For each={items()}>
            {(item) => (
              <ContentCard 
                title={item.title}
                desc={item.desc}
                meta1={itemType() === 'post' ? <span class="flex items-center gap-1"><Calendar size={12}/>{item.date}</span> : <span class="bg-zinc-100 dark:bg-zinc-800 px-2 py-0.5 rounded text-zinc-600 dark:text-zinc-400">{item.year}</span>}
                meta2={itemType() === 'post' ? <span class="flex items-center gap-1"><Clock size={12}/>{item.readTime}</span> : null}
                tags={item.tags}
                onClick={() => props.onItemClick(item, itemType())}
                onTagClick={(tag) => props.onTagClick(tag, itemType())}
                actionText={itemType() === 'post' ? props.ui.buttons.readMore : props.ui.buttons.viewDetails}
              />
            )}
          </For>
        </Show>
      </div>
    </section>
  );
};
