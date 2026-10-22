import { AGENT_COLORS, AppState, clock } from "../types";
import { MASCOT_KINDS, MASCOT_NAMES, mascotSvg } from "../mascots";

interface Props {
  state: AppState;
  busy: boolean;
  onToggle: (id: string, available: boolean) => void;
}

export default function AgentsPanel({ state, busy, onToggle }: Props) {
  const { agents, orders } = state.scenario;
  const routes = state.optimized?.routes ?? [];

  return (
    <section className="toon-card p-4">
      <h2 className="mb-3 toon-title">Agents &amp; routes</h2>
      <div className="space-y-3">
        {agents.map((a, i) => {
          const color = AGENT_COLORS[i % AGENT_COLORS.length];
          const r = routes.find((x) => x.agent_id === a.id);
          const pct = r ? Math.min(100, Math.round((r.load / a.capacity) * 100)) : 0;
          return (
            <div key={a.id} className={`rounded-xl border-2 p-3 ${a.available ? "border-slate-900" : "border-dashed border-slate-400 bg-slate-50"}`}>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span
                    className={a.available ? "rw-mascot" : "opacity-40 grayscale"}
                    title={MASCOT_NAMES[MASCOT_KINDS[i % MASCOT_KINDS.length]]}
                    dangerouslySetInnerHTML={{ __html: mascotSvg(MASCOT_KINDS[i % MASCOT_KINDS.length], color, 40) }}
                  />
                  <div className="leading-tight">
                    <div className="font-extrabold text-slate-900">{a.name}</div>
                    <div className="text-[11px] text-slate-400">{MASCOT_NAMES[MASCOT_KINDS[i % MASCOT_KINDS.length]]}</div>
                  </div>
                </div>
                <button
                  disabled={busy}
                  onClick={() => onToggle(a.id, !a.available)}
                  className={`toon-btn-sm px-2.5 py-0.5 text-[11px] ${
                    a.available ? "bg-emerald-100 text-emerald-700 hover:bg-emerald-200"
                                : "bg-slate-200 text-slate-600 hover:bg-slate-300"} disabled:opacity-50`}
                  title="Simulate a breakdown / sick leave"
                >
                  {a.available ? "On duty" : "Off duty"}
                </button>
              </div>

              {a.available && r ? (
                <>
                  <div className="mt-2 flex gap-3 text-xs text-slate-500">
                    <span>{r.stops.length} stops</span>
                    <span>{r.distance_km} km</span>
                    <span>~{Math.round(r.duration_min)} min</span>
                  </div>
                  <div className="mt-1.5 flex items-center gap-2">
                    <div className="h-1.5 flex-1 overflow-hidden rounded bg-slate-100">
                      <div className="h-full" style={{ width: `${pct}%`, background: color }} />
                    </div>
                    <span className="text-[11px] text-slate-500">{r.load}/{a.capacity} pkgs</span>
                  </div>
                  <ol className="mt-2 space-y-0.5 text-xs">
                    {r.stops.map((s, k) => {
                      const o = orders.find((x) => x.id === s.order_id);
                      return (
                        <li key={s.order_id} className="flex justify-between">
                          <span className="text-slate-600">{k + 1}. {o?.name ?? s.order_id}</span>
                          <span className={s.late > 0.5 ? "font-semibold text-red-600" : "text-slate-400"}>
                            {clock(s.arrival)}{s.late > 0.5 ? ` (+${Math.round(s.late)}m)` : ""}
                          </span>
                        </li>
                      );
                    })}
                  </ol>
                </>
              ) : (
                <p className="mt-2 text-xs text-slate-400">Not receiving orders. Their work was handed to other agents.</p>
              )}
            </div>
          );
        })}
      </div>
    </section>
  );
}
