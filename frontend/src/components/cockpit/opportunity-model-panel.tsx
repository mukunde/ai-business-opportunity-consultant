import type { ContextNode } from "@/lib/api";

function Group({
  title,
  dot,
  children,
}: {
  title: string;
  dot: string;
  children: React.ReactNode;
}) {
  return (
    <div>
      <h2 className="text-muted-foreground flex items-center gap-2 text-xs font-medium tracking-wide uppercase">
        <span className={`size-1.5 rounded-full ${dot}`} aria-hidden />
        {title}
      </h2>
      <div className="mt-3">{children}</div>
    </div>
  );
}

export function OpportunityModelPanel({ nodes }: { nodes: ContextNode[] }) {
  const facts = nodes.filter((n) => n.type === "FACT");
  const assumptions = nodes.filter((n) => n.type === "ASSUMPTION");
  const unknowns = nodes.filter((n) => n.type === "UNKNOWN");

  return (
    <div className="space-y-6">
      <Group title="Facts" dot="bg-emerald-500">
        {facts.length > 0 ? (
          <dl className="space-y-2">
            {facts.map((n) => (
              <div key={n.id} className="text-sm">
                <dt className="text-muted-foreground text-xs">{n.label}</dt>
                <dd className="font-medium">{n.description}</dd>
              </div>
            ))}
          </dl>
        ) : (
          <p className="text-muted-foreground text-sm">Nothing established yet.</p>
        )}
      </Group>

      <Group title="Assumptions" dot="bg-amber-500">
        {assumptions.length > 0 ? (
          <ul className="space-y-1.5 text-sm">
            {assumptions.map((n) => (
              <li key={n.id}>{n.label}</li>
            ))}
          </ul>
        ) : (
          <p className="text-muted-foreground text-sm">None recorded.</p>
        )}
      </Group>

      <Group title="Unknowns" dot="bg-zinc-400">
        {unknowns.length > 0 ? (
          <ul className="text-muted-foreground space-y-1.5 text-sm">
            {unknowns.map((n) => (
              <li key={n.id}>{n.label}</li>
            ))}
          </ul>
        ) : (
          <p className="text-muted-foreground text-sm">None.</p>
        )}
      </Group>
    </div>
  );
}
