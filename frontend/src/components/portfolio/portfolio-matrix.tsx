"use client";

import { useRouter } from "next/navigation";

import { useT } from "@/lib/i18n";
import type { OpportunitySummary } from "@/lib/api";

export type Quadrant = "quick" | "bet" | "low";

const MID = 5; // midpoint of the 0-10 axes

export function quadrantOf(impact: number, feasibility: number): Quadrant {
  if (impact >= MID && feasibility >= MID) return "quick";
  if (impact >= MID) return "bet";
  return "low";
}

const DOT_FILL: Record<Quadrant, string> = {
  quick: "fill-emerald-500",
  bet: "fill-amber-500",
  low: "fill-zinc-400",
};

// Plot geometry (SVG units).
const W = 480;
const H = 440;
const PAD = { l: 52, r: 24, t: 24, b: 44 };
const PLOT_W = W - PAD.l - PAD.r;
const PLOT_H = H - PAD.t - PAD.b;

const x = (feasibility: number) => PAD.l + (feasibility / 10) * PLOT_W;
const y = (impact: number) => PAD.t + (1 - impact / 10) * PLOT_H;

function truncate(s: string, n = 16) {
  return s.length > n ? `${s.slice(0, n - 1)}…` : s;
}

export function PortfolioMatrix({ items }: { items: OpportunitySummary[] }) {
  const t = useT();
  const router = useRouter();

  return (
    <svg
      viewBox={`0 0 ${W} ${H}`}
      className="w-full"
      role="img"
      aria-label={t("Impact vs feasibility matrix")}
    >
      {/* Quadrant tints */}
      <rect
        x={x(MID)}
        y={PAD.t}
        width={PLOT_W / 2}
        height={PLOT_H / 2}
        className="fill-emerald-500/8"
      />
      <rect
        x={PAD.l}
        y={PAD.t}
        width={PLOT_W / 2}
        height={PLOT_H / 2}
        className="fill-amber-500/8"
      />
      <rect
        x={PAD.l}
        y={y(MID)}
        width={PLOT_W}
        height={PLOT_H / 2}
        className="fill-muted/40"
      />

      {/* Quadrant labels */}
      <text
        x={x(MID) + PLOT_W / 4}
        y={PAD.t + 18}
        textAnchor="middle"
        className="fill-emerald-700 dark:fill-emerald-400 text-[11px] font-medium tracking-wide uppercase"
      >
        {t("Quick Wins")}
      </text>
      <text
        x={PAD.l + PLOT_W / 4}
        y={PAD.t + 18}
        textAnchor="middle"
        className="fill-amber-700 dark:fill-amber-400 text-[11px] font-medium tracking-wide uppercase"
      >
        {t("Strategic Bets")}
      </text>
      <text
        x={PAD.l + PLOT_W / 2}
        y={H - PAD.b - 10}
        textAnchor="middle"
        className="fill-muted-foreground text-[11px] font-medium tracking-wide uppercase"
      >
        {t("Low Priority")}
      </text>

      {/* Axes frame + midlines */}
      <rect
        x={PAD.l}
        y={PAD.t}
        width={PLOT_W}
        height={PLOT_H}
        fill="none"
        className="stroke-border"
        strokeWidth={1}
      />
      <line
        x1={x(MID)}
        y1={PAD.t}
        x2={x(MID)}
        y2={PAD.t + PLOT_H}
        className="stroke-border"
        strokeDasharray="4 4"
      />
      <line
        x1={PAD.l}
        y1={y(MID)}
        x2={PAD.l + PLOT_W}
        y2={y(MID)}
        className="stroke-border"
        strokeDasharray="4 4"
      />

      {/* Axis titles */}
      <text
        x={PAD.l + PLOT_W / 2}
        y={H - 8}
        textAnchor="middle"
        className="fill-foreground text-xs font-medium"
      >
        {t("Feasibility")} {"→"}
      </text>
      <text
        x={-(PAD.t + PLOT_H / 2)}
        y={14}
        transform="rotate(-90)"
        textAnchor="middle"
        className="fill-foreground text-xs font-medium"
      >
        {t("Impact")} {"→"}
      </text>

      {/* Points */}
      {items.map((o) => {
        const impact = o.impact_score as number;
        const feas = o.feasibility_score as number;
        const r = 5 + ((o.final_score ?? 0) / 10) * 4;
        const q = quadrantOf(impact, feas);
        return (
          <g
            key={o.id}
            className="cursor-pointer"
            onClick={() => router.push(`/opportunities/${o.id}`)}
          >
            <title>
              {o.title}: {t("Impact")} {impact.toFixed(1)}, {t("Feasibility")}{" "}
              {feas.toFixed(1)}
            </title>
            <circle
              cx={x(feas)}
              cy={y(impact)}
              r={r}
              className={`${DOT_FILL[q]} stroke-background`}
              strokeWidth={1.5}
            />
            <text
              x={x(feas) + r + 3}
              y={y(impact) + 3}
              className="fill-foreground text-[10px]"
            >
              {truncate(o.title)}
            </text>
          </g>
        );
      })}
    </svg>
  );
}
