import { AGENT_COLORS, AppState, PRIORITY_LABEL, clock } from "../types";

interface Props {
  state: AppState;
  busy: boolean;
  onCancel: (id: string) => void;
  onRestore: (id: string) => void;
  onDelay: (id: string, minutes: number) => void;
  onReassign: (id: string, agentId: string | null) => void;
}

const PRIO_STYLE: Record<number, string> = {
  1: "bg-slate-100 text-slate-600",
  2: "bg-amber-100 text-amber-700",
  3: "bg-red-100 text-red-700",
};

export default function OrdersPanel({ state, busy, onCancel, onRestore, onDelay, onReassign }: Props) {
  const { agents, orders } = state.scenario;
  const owner: Record<string, { agent: string; late: number; arrival: number }> = {};
  state.optimized?.routes.forEach((r) =>
    r.stops.forEach((s) => { owner[s.order_id] = { agent: r.agent_id, late: s.late, arrival: s.arrival }; })
  );

  return (
    <section className="toon-card p-4">
      <h2 className="mb-3 toon-title">
        Orders ({orders.filter((o) => o.status !== "cancelled").length} active)
      </h2>
      <div className="max-h-[420px] space-y-2 overflow-y-auto pr-1">
        {orders.map((o) => {
          const cancelled = o.status === "cancelled";
          const ow = owner[o.id];
          const idx = agents.findIndex((a) => a.id === ow?.agent);
          return (
            <div key={o.id} className={`rounded-lg border p-2.5 ${cancelled ? "border-dashed bg-slate-50 opacity-60" : "border-slate-200"}`}>
              <div className="flex items-center justify-between gap-2">
                <div className="min-w-0">
                  <span className="text-xs text-slate-400">{o.id}</span>{" "}
                  <span className="font-semibold text-slate-800">{o.name}</span>
                </div>
                <span className={`shrink-0 rounded px-1.5 py-0.5 text-[10px] font-bold ${PRIO_STYLE[o.priority]}`}>
                  {PRIORITY_LABEL[o.priority]}
                </span>
              </div>
              <div className="mt-0.5 text-xs text-slate-500">
                {o.demand} pkg · {clock(o.tw_start + o.delay)}–{clock(o.tw_end + o.delay)}
                {o.delay > 0 && <span className="text-amber-600"> (delayed +{o.delay}m)</span>}
                {ow && !cancelled && (
                  <span className={ow.late > 0.5 ? "text-red-600" : "text-emerald-600"}>
                    {" "}· ETA {clock(ow.arrival)}{ow.late > 0.5 ? " late" : " ✓"}
                  </span>
                )}
              </div>

              <div className="mt-2 flex flex-wrap items-center gap-1.5">
                {cancelled ? (
                  <button disabled={busy} onClick={() => onRestore(o.id)}
                    className="toon-btn-sm bg-emerald-600 px-2 py-1 text-[11px] font-semibold text-white hover:bg-emerald-700 disabled:opacity-50">
                    Restore
                  </button>
                ) : (
                  <>
                    <span className="inline-block h-2.5 w-2.5 rounded-full"
                      style={{ background: idx >= 0 ? AGENT_COLORS[idx % AGENT_COLORS.length] : "#475569" }} />
                    <select
                      disabled={busy}
                      value={o.locked_agent ?? ""}
                      onChange={(e) => onReassign(o.id, e.target.value || null)}
                      className="rounded-lg border-2 border-slate-900 bg-white px-1 py-0.5 text-[11px] font-bold"
                      title="Manually assign to an agent (locks it), or leave on Auto"
                    >
                      <option value="">Auto{ow ? ` (${agents.find((a) => a.id === ow.agent)?.name})` : ""}</option>
                      {agents.filter((a) => a.available).map((a) => (
                        <option key={a.id} value={a.id}>{a.name}</option>
                      ))}
                    </select>
                    <button disabled={busy} onClick={() => onDelay(o.id, 30)}
                      className="toon-btn-sm bg-amber-100 px-2 py-1 text-[11px] font-semibold text-amber-800 hover:bg-amber-200 disabled:opacity-50">
                      +30 min delay
                    </button>
                    <button disabled={busy} onClick={() => onCancel(o.id)}
                      className="toon-btn-sm bg-red-100 px-2 py-1 text-[11px] font-semibold text-red-700 hover:bg-red-200 disabled:opacity-50">
                      Cancel
                    </button>
                  </>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
