"use client";

/**
 * A tiny "(?)" trigger that reveals a definition on hover or keyboard focus.
 * CSS-only (group-hover / focus-within), so no portal or extra dependency.
 */
export function InfoTip({ text }: { text: string }) {
  return (
    <span className="group relative ml-1 inline-flex align-middle">
      <button
        type="button"
        aria-label={text}
        className="border-border text-muted-foreground/70 hover:text-foreground focus-visible:ring-ring/50 flex size-3.5 items-center justify-center rounded-full border text-[9px] leading-none font-medium outline-none focus-visible:ring-2"
      >
        ?
      </button>
      <span
        role="tooltip"
        className="bg-popover text-popover-foreground border-border pointer-events-none absolute top-full left-0 z-40 mt-1.5 hidden w-48 rounded-md border p-2 text-xs leading-snug font-normal shadow-sm group-focus-within:block group-hover:block"
      >
        {text}
      </span>
    </span>
  );
}
