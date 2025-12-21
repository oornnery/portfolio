// @ts-nocheck
import { Show, For } from 'solid-js';
import { Github, Twitter, Linkedin, Mail, ExternalLink } from 'lucide-solid';

const WhatsappIcon = (props) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width={props.size || 20}
    height={props.size || 20}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    class={props.class || ''}
  >
    <path d="M3 21l1.65-3.8a9 9 0 1 1 3.4 2.9L3 21" />
    <path d="M9 10a1 1 0 0 0 1 1" stroke="none" />
  </svg>
);

export const SocialLinks = (props) => {
  const IconMap = { 
    github: Github, 
    twitter: Twitter, 
    linkedin: Linkedin, 
    mail: Mail, 
    email: Mail,
    whatsapp: WhatsappIcon
  };
  
  return (
    <Show when={props.links}>
      <div class={`flex gap-4 ${props.class || ''}`} onClick={(e) => e.stopPropagation()}>
        <For each={props.links}>
          {(link) => {
            const Icon = IconMap[link.network.toLowerCase()] || ExternalLink;
            return (
              <a 
                href={link.url} 
                target="_blank" 
                rel="noreferrer" 
                class="text-zinc-500 hover:text-zinc-900 dark:hover:text-zinc-300 transition-colors" 
                aria-label={link.network}
              >
                <Icon size={20} />
              </a>
            );
          }}
        </For>
      </div>
    </Show>
  );
};
