import { InfoTip } from "@/components/info-tip";
import type { Completeness, ContextNode } from "@/lib/api";

function Ring({ value }: { value: number }) {
  const r = 34;
  const c = 2 * Math.PI * r;
  const pct = Math.max(0, Math.min(1, value));
  return (
    <div className="relative grid size-24 place-items-center">
      <svg viewBox="0 0 80 80" className="size-24 -rotate-90">
        <circle
          cx="40"
          cy="40"
          r={r}
          fill="none"
          stroke="var(--muted)"
          strokeWidth="7"
        />
        <circle
          cx="40"
          cy="40"
          r={r}
          fill="none"
          stroke="var(--primary)"
          strokeWidth="7"
          strokeLinecap="round"
          strokeDasharray={c}
          strokeDashoffset={c * (1 - pct)}
          className="transition-[stroke-dashoffset] duration-500 ease-out motion-reduce:transition-none"
        />
      </svg>
      <span className="absolute font-mono text-lg font-semibold tabular-nums">
        {Math.round(pct * 100)}%
      </span>
    </div>
  );
}

function Bar({
  label,
  value,
  tip,
}: {
  label: string;
  value: number;
  tip?: string;
}) {
  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between text-xs">
        <span className="text-muted-foreground">
          {label}
          {tip ? <InfoTip text={tip} /> : null}
        </span>
        <span className="font-mono tabular-nums">{Math.round(value * 100)}%</span>
      </div>
      <div className="bg-muted h-1.5 overflow-hidden rounded-full">
        <div
          className="bg-primary h-full rounded-full transition-[width] duration-500 ease-out motion-reduce:transition-none"
          style={{ width: `${Math.round(value * 100)}%` }}
        />
      </div>
    </div>
  );
}

export function ContextStatusPanel({
  completeness,
  nodes,
}: {
  completeness: Completeness | null;
  nodes: ContextNode[];
}) {
  const missing = nodes.filter((n) => n.type === "UNKNOWN");
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-muted-foreground text-xs font-medium tracking-wide uppercase">
          Context completeness
        </h2>
        <div className="mt-3 flex justify-center">
          <Ring value={completeness?.overall_score ?? 0} />
        </div>
      </div>

      <div className="space-y-3">
        <Bar
          label="Business context"
          value={completeness?.business_context_score ?? 0}
          tip="Do we understand the business problem and who owns it? Built from business volume and the process owner."
        />
        <Bar
          label="Process understanding"
          value={completeness?.process_understanding_score ?? 0}
          tip="Do we understand how the current process works? Built from the average handling time."
        />
        <Bar
          label="Data readiness"
          value={completeness?.data_readiness_score ?? 0}
          tip="Is there data available to build the AI on? Drives feasibility and time to value; its absence raises risk."
        />
        <Bar
          label="ROI readiness"
          value={completeness?.roi_readiness_score ?? 0}
          tip="Can we estimate the return? Needs both business volume and handling time to size the savings."
        />
      </div>

      <div>
        <h2 className="text-muted-foreground text-xs font-medium tracking-wide uppercase">
          Missing context
        </h2>
        {missing.length > 0 ? (
          <ul className="mt-3 space-y-2">
            {missing.map((n) => (
              <li key={n.id} className="flex items-center gap-2 text-sm">
                <span className="bg-highlight size-1.5 rounded-full" aria-hidden />
                {n.label}
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-muted-foreground mt-3 text-sm">
            All required context collected.
          </p>
        )}
      </div>
    </div>
  );
}
