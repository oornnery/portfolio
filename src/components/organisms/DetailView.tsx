// @ts-nocheck
import { createSignal, Show, For } from 'solid-js';
import { ArrowLeft, Calendar, Clock, Code2, ExternalLink, List, X } from 'lucide-solid';
import { Button } from '../atoms/Button';
import { Tag } from '../atoms/Tag';
import { Sidebar } from './Sidebar';

export const DetailView = (props) => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = createSignal(false);
  
  const item = () => props.selectedType === 'post' 
    ? props.data.posts.find(p => p.id === props.selectedItemId) 
    : props.data.projects.find(p => p.id === props.selectedItemId);
  
  const isPost = () => props.selectedType === 'post';
  
  const relatedItems = () => isPost()
    ? props.data.posts.filter(p => p.id !== item()?.id).slice(0, 3)
    : props.data.projects.filter(p => p.id !== item()?.id).slice(0, 3);

  return (
    <Show when={item()}>
      <div class="animate-in fade-in duration-500 relative">
        <div class="flex justify-between items-center mb-8">
          <Button variant="ghost" onClick={props.onBack} class="pl-0 hover:bg-transparent">
            <ArrowLeft size={16} /> {isPost() ? props.ui.buttons.backBlog : props.ui.buttons.backProjects}
          </Button>
          <div class="lg:hidden">
            <Button variant="icon" onClick={() => setIsMobileMenuOpen(true)} aria-label={props.ui.buttons.openSidebar}>
              <List size={20} />
            </Button>
          </div>
        </div>
        
        <div class="grid grid-cols-1 lg:grid-cols-[280px_1fr] gap-12 items-start">
          <div class="hidden lg:block sticky top-8">
            <Sidebar 
              profile={props.data.profile} 
              uiText={props.ui} 
              onGoToAbout={props.onGoToAbout}
              title={isPost() ? props.ui.sections.latestBlog : props.ui.sections.latestProjects}
              items={relatedItems()}
              onItemClick={(i) => props.onItemClick(i, props.selectedType)}
              onTagClick={(t) => props.onTagClick(t, props.selectedType)}
              isProject={!isPost()}
            />
          </div>

          <Show when={isMobileMenuOpen()}>
            <div class="fixed inset-0 z-50 lg:hidden flex justify-end">
              <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={() => setIsMobileMenuOpen(false)} />
              <div class="relative w-80 bg-white dark:bg-zinc-900 h-full shadow-xl p-6 overflow-y-auto animate-in slide-in-from-right duration-300">
                <div class="flex justify-end mb-4">
                  <Button variant="icon" onClick={() => setIsMobileMenuOpen(false)} aria-label={props.ui.buttons.closeSidebar}>
                    <X size={20} />
                  </Button>
                </div>
                <Sidebar 
                  profile={props.data.profile} 
                  uiText={props.ui} 
                  onGoToAbout={() => { props.onGoToAbout(); setIsMobileMenuOpen(false); }}
                  title={isPost() ? props.ui.sections.latestBlog : props.ui.sections.latestProjects}
                  items={relatedItems()}
                  onItemClick={(i) => { props.onItemClick(i, props.selectedType); setIsMobileMenuOpen(false); }}
                  onTagClick={(t) => { props.onTagClick(t, props.selectedType); setIsMobileMenuOpen(false); }}
                  isProject={!isPost()}
                />
              </div>
            </div>
          </Show>

          <article class="min-w-0">
            <header class="mb-10 border-b border-zinc-200 dark:border-zinc-800 pb-10">
              <div class="flex flex-wrap gap-3 text-xs font-mono text-zinc-500 mb-6">
                <Show when={isPost()} fallback={
                  <span class="bg-zinc-100 dark:bg-zinc-800 px-2 py-0.5 rounded text-zinc-600 dark:text-zinc-400">{item()?.year}</span>
                }>
                  <span class="flex items-center gap-1"><Calendar size={12}/> {item()?.date}</span>
                  <span>•</span>
                  <span class="flex items-center gap-1"><Clock size={12}/> {item()?.readTime}</span>
                </Show>
              </div>
              <h1 class="text-3xl sm:text-4xl font-extrabold text-zinc-900 dark:text-zinc-100 mb-6 tracking-tight leading-tight">{item()?.title}</h1>
              <Show when={item()?.tags}>
                <div class="flex flex-wrap gap-2 mb-6">
                  <For each={item()?.tags}>
                    {(tag) => <Tag onClick={() => props.onTagClick(tag, props.selectedType)}>{tag}</Tag>}
                  </For>
                </div>
              </Show>
              <p class="text-xl text-zinc-600 dark:text-zinc-400 leading-relaxed">{item()?.desc}</p>
              <Show when={!isPost()}>
                <div class="flex gap-4 mt-8">
                  <a href={item()?.link} class="inline-flex items-center gap-2 px-4 py-2 bg-zinc-900 dark:bg-zinc-100 text-white dark:text-zinc-900 rounded-lg font-medium text-sm hover:opacity-90 transition-opacity">
                    <ExternalLink size={16} /> {props.ui.buttons.liveDemo}
                  </a>
                  <a href={item()?.repo} class="inline-flex items-center gap-2 px-4 py-2 border border-zinc-300 dark:border-zinc-700 text-zinc-700 dark:text-zinc-300 rounded-lg font-medium text-sm hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors">
                    <Code2 size={16} /> {props.ui.buttons.viewCode}
                  </a>
                </div>
              </Show>
            </header>

            <div class="prose prose-zinc dark:prose-invert max-w-none">
              <Show when={isPost()} fallback={
                <div>
                  <h3 class="text-xl font-bold text-zinc-900 dark:text-zinc-100 mb-4">{props.ui.sections.aboutProject}</h3>
                  <p class="text-zinc-700 dark:text-zinc-300 leading-7 mb-6">{item()?.details}</p>
                  <h3 class="text-xl font-bold text-zinc-900 dark:text-zinc-100 mb-4">{props.ui.sections.technologies}</h3>
                  <ul class="list-disc list-inside text-zinc-700 dark:text-zinc-300 space-y-2 mb-8">
                    <li>Framework: {item()?.tags?.[0]}</li>
                    <li>Styling: Tailwind CSS</li>
                  </ul>
                  <div class="bg-zinc-50 dark:bg-zinc-900/50 border border-zinc-200 dark:border-zinc-800 rounded-xl p-12 flex items-center justify-center text-zinc-500 mb-8">
                    <span class="text-sm italic">{props.ui.sections.screenshot}</span>
                  </div>
                </div>
              }>
                <p class="text-zinc-700 dark:text-zinc-300 leading-7 mb-6 whitespace-pre-line">{item()?.content}</p>
                <div class="bg-zinc-50 dark:bg-[#161618] border border-zinc-200 dark:border-zinc-800 rounded-lg p-4 my-8 overflow-x-auto">
                  <pre class="font-mono text-sm text-blue-600 dark:text-blue-300">{'// Code example placeholder'}</pre>
                </div>
              </Show>
            </div>
          </article>
        </div>
      </div>
    </Show>
  );
};
