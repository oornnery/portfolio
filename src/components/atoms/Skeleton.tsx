// @ts-nocheck
export const Skeleton = (props) => (
  <div
    class={`animate-pulse bg-zinc-300 dark:bg-zinc-700 rounded ${props.class || ''}`}
    style={{ "min-height": "1rem" }}
    aria-hidden="true"
  />
);
