"use client";

import { Maximize, ZoomIn, ZoomOut } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";

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

const LEGEND: { key: Quadrant; label: string; swatch: string }[] = [
  { key: "quick", label: "Quick Wins", swatch: "bg-emerald-500" },
  { key: "bet", label: "Strategic Bets", swatch: "bg-amber-500" },
  { key: "low", label: "Low Priority", swatch: "bg-zinc-400" },
];

// Plot geometry (SVG units).
const W = 480;
const H = 440;
const PAD = { l: 52, r: 24, t: 24, b: 44 };
const PLOT_W = W - PAD.l - PAD.r;
const PLOT_H = H - PAD.t - PAD.b;

const x = (feasibility: number) => PAD.l + (feasibility / 10) * PLOT_W;
const y = (impact: number) => PAD.t + (1 - impact / 10) * PLOT_H;
const radius = (finalScore: number | null | undefined) =>
  5 + ((finalScore ?? 0) / 10) * 4;

function truncate(s: string, n = 16) {
  return s.length > n ? `${s.slice(0, n - 1)}…` : s;
}

const MIN_ZOOM = 1;
const MAX_ZOOM = 3;
const ZOOM_STEP = 0.5;

const controlBtn =
  "bg-card/90 text-foreground hover:bg-muted disabled:pointer-events-none disabled:opacity-40 grid size-8 place-items-center rounded-md border shadow-sm backdrop-blur transition-colors";

export function PortfolioMatrix({ items }: { items: OpportunitySummary[] }) {
  const t = useT();
  const router = useRouter();
  const [zoom, setZoom] = useState(1);

  const setZoomClamped = (z: number) =>
    setZoom(Math.min(MAX_ZOOM, Math.max(MIN_ZOOM, Math.round(z * 10) / 10)));

  // Opportunities at the same impact/feasibility coincide on the plot; collapse
  // them into one marker carrying a count badge instead of overlapping dots.
  const groups = Object.values(
    items.reduce<Record<string, OpportunitySummary[]>>((acc, o) => {
      const key = `${(o.impact_score as number).toFixed(1)}|${(o.feasibility_score as number).toFixed(1)}`;
      (acc[key] ??= []).push(o);
      return acc;
    }, {}),
  );

  return (
    <div>
      <div className="relative">
        <div className="max-h-[75vh] overflow-auto rounded-lg">
          <svg
            viewBox={`0 0 ${W} ${H}`}
            className="block h-auto"
            style={{ width: `${zoom * 100}%` }}
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

        {/* Markers: one per coincident group, staggered fade + zoom entrance. */}
        {groups.map((group, i) => {
          const first = group[0];
          const impact = first.impact_score as number;
          const feas = first.feasibility_score as number;
          const count = group.length;
          const single = count === 1;
          const q = quadrantOf(impact, feas);
          const cx = x(feas);
          const cy = y(impact);
          const r =
            Math.max(...group.map((o) => radius(o.final_score))) + (single ? 0 : 2);
          const go = () => router.push(`/opportunities/${first.id}`);

          // Flip the label left when a right-side label would overflow the viewBox.
          const label = single ? truncate(first.title) : `${count} ${t("opportunities")}`;
          const flipLeft = cx + r + 3 + label.length * 5.6 > W - 4;
          const labelX = flipLeft ? cx - r - 3 : cx + r + 3;
          const tip = single
            ? `${first.title}: ${t("Impact")} ${impact.toFixed(1)}, ${t("Feasibility")} ${feas.toFixed(1)}`
            : group.map((o) => o.title).join(", ");

          return (
            <g
              key={single ? first.id : `cluster-${i}`}
              className={`animate-in fade-in zoom-in-75 fill-mode-both motion-reduce:animate-none group outline-none duration-500 ease-out ${single ? "cursor-pointer" : ""}`}
              style={{
                animationDelay: `${Math.min(i, 14) * 45}ms`,
                transformBox: "fill-box",
                transformOrigin: "center",
              }}
              role={single ? "link" : "img"}
              tabIndex={single ? 0 : undefined}
              aria-label={single ? tip : `${count} ${t("opportunities")}: ${tip}`}
              onClick={single ? go : undefined}
              onKeyDown={
                single
                  ? (e) => {
                      if (e.key === "Enter" || e.key === " ") {
                        e.preventDefault();
                        go();
                      }
                    }
                  : undefined
              }
            >
              <title>{tip}</title>
              <circle
                cx={cx}
                cy={cy}
                r={r}
                className={`${DOT_FILL[q]} stroke-background transition-[stroke] ${single ? "group-hover:stroke-foreground group-focus-visible:stroke-foreground" : ""}`}
                strokeWidth={1.5}
              />
              <text
                x={labelX}
                y={cy + 3}
                textAnchor={flipLeft ? "end" : "start"}
                className="fill-foreground group-hover:font-medium text-[10px]"
              >
                {label}
              </text>
              {!single ? (
                <>
                  <circle
                    cx={cx + r * 0.72}
                    cy={cy - r * 0.72}
                    r={7}
                    className="fill-foreground stroke-background"
                    strokeWidth={1.5}
                  />
                  <text
                    x={cx + r * 0.72}
                    y={cy - r * 0.72 + 3}
                    textAnchor="middle"
                    className="fill-background text-[9px] font-semibold"
                  >
                    {count}
                  </text>
                </>
              ) : null}
            </g>
          );
        })}
          </svg>
        </div>

        <div className="absolute top-2 right-2 flex flex-col gap-1">
          <button
            type="button"
            onClick={() => setZoomClamped(zoom + ZOOM_STEP)}
            disabled={zoom >= MAX_ZOOM}
            aria-label={t("Zoom in")}
            className={controlBtn}
          >
            <ZoomIn className="size-4" />
          </button>
          <button
            type="button"
            onClick={() => setZoomClamped(zoom - ZOOM_STEP)}
            disabled={zoom <= MIN_ZOOM}
            aria-label={t("Zoom out")}
            className={controlBtn}
          >
            <ZoomOut className="size-4" />
          </button>
          <button
            type="button"
            onClick={() => setZoom(1)}
            disabled={zoom === 1}
            aria-label={t("Reset zoom")}
            className={controlBtn}
          >
            <Maximize className="size-4" />
          </button>
        </div>
      </div>

      {/* Legend: colour encodes the quadrant, dot radius encodes priority score. */}
      <div className="text-muted-foreground mt-3 flex flex-wrap items-center justify-between gap-x-6 gap-y-2 border-t pt-3 text-xs">
        <div className="flex flex-wrap items-center gap-x-4 gap-y-1">
          {LEGEND.map((l) => (
            <span key={l.key} className="flex items-center gap-1.5">
              <span
                className={`size-2 rounded-full ${l.swatch}`}
                aria-hidden
              />
              {t(l.label)}
            </span>
          ))}
        </div>
        <div className="flex items-center gap-1.5" aria-hidden>
          <span className="bg-muted-foreground/60 size-1.5 rounded-full" />
          <span className="bg-muted-foreground/60 size-3 rounded-full" />
          <span>{t("Priority score")}</span>
        </div>
      </div>
    </div>
  );
}
