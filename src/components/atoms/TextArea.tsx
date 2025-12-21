// @ts-nocheck
import { Show } from 'solid-js';

export const TextArea = (props) => (
  <div>
     <Show when={props.label}>
      <label for={props.id} class="block text-xs font-bold text-zinc-500 dark:text-zinc-400 uppercase tracking-wider mb-2">
        {props.label}
      </label>
    </Show>
    <textarea 
      id={props.id}
      rows={props.rows || 4}
      placeholder={props.placeholder}
      class="w-full bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-zinc-400 dark:focus:border-zinc-600 transition-colors text-zinc-900 dark:text-zinc-100 placeholder:text-zinc-400 dark:placeholder:text-zinc-600 resize-y" 
    />
  </div>
);
