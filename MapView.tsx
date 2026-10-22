import { useEffect, useRef } from "react";
import L from "leaflet";
import { AGENT_COLORS, AppState, PRIORITY_LABEL, clock } from "../types";
import { MASCOT_KINDS, MASCOT_NAMES, mascotSvg } from "../mascots";

interface Props {
  state: AppState;
  pickMode: boolean;
  picked: { lat: number; lng: number } | null;
  onPick: (lat: number, lng: number) => void;
}

function pin(color: string, label: string, size = 24, dashed = false) {
  return L.divIcon({
    className: "",
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2],
    html: `<div class="rw-pin" style="width:${size}px;height:${size}px;background:${color};${
      dashed ? "opacity:.45;border-style:dashed;" : ""
    }">${label}</div>`,
  });
}

export default function MapView({ state, pickMode, picked, onPick }: Props) {
  const el = useRef<HTMLDivElement>(null);
  const map = useRef<L.Map | null>(null);
  const layer = useRef<L.LayerGroup | null>(null);
  const fitted = useRef(false);
  const pickRef = useRef({ pickMode, onPick });
  pickRef.current = { pickMode, onPick };

  // create the map once
  useEffect(() => {
    if (!el.current || map.current) return;
    const m = L.map(el.current, { zoomControl: true }).setView(
      [state.scenario.depot.lat, state.scenario.depot.lng], 12
    );
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    }).addTo(m);
    layer.current = L.layerGroup().addTo(m);
    m.on("click", (e: L.LeafletMouseEvent) => {
      if (pickRef.current.pickMode) pickRef.current.onPick(e.latlng.lat, e.latlng.lng);
    });
    map.current = m;
    return () => { m.remove(); map.current = null; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // cursor feedback while picking a location
  useEffect(() => {
    if (el.current) el.current.style.cursor = pickMode ? "crosshair" : "";
  }, [pickMode]);

  // redraw routes + markers whenever the plan changes
  useEffect(() => {
    const m = map.current, g = layer.current;
    if (!m || !g) return;
    g.clearLayers();

    const { depot, agents, orders } = state.scenario;
    const sol = state.optimized;
    const colorOf: Record<string, string> = {};
    agents.forEach((a, i) => { colorOf[a.id] = AGENT_COLORS[i % AGENT_COLORS.length]; });
    const owner: Record<string, { agent: string; seq: number; arrival: number; late: number }> = {};
    const bounds: L.LatLngTuple[] = [[depot.lat, depot.lng]];

    sol?.routes.forEach((r) => {
      const pts: L.LatLngTuple[] = [[depot.lat, depot.lng]];
      r.stops.forEach((s, i) => {
        owner[s.order_id] = { agent: r.agent_id, seq: i + 1, arrival: s.arrival, late: s.late };
        const o = orders.find((x) => x.id === s.order_id);
        if (o) pts.push([o.lat, o.lng]);
      });
      pts.push([depot.lat, depot.lng]);
      if (pts.length > 2) {
        L.polyline(pts, { color: colorOf[r.agent_id], weight: 5, opacity: 0.85, lineCap: "round" }).addTo(g);
        // the agent's mascot sits at the midpoint of its first leg, heading out of the depot
        const ai = agents.findIndex((a) => a.id === r.agent_id);
        const kind = MASCOT_KINDS[ai % MASCOT_KINDS.length];
        const mid: L.LatLngTuple = [(pts[0][0] + pts[1][0]) / 2, (pts[0][1] + pts[1][1]) / 2];
        L.marker(mid, {
          icon: L.divIcon({
            className: "",
            iconSize: [38, 38],
            iconAnchor: [19, 19],
            html: `<div class="rw-mascot">${mascotSvg(kind, colorOf[r.agent_id], 38)}</div>`,
          }),
          zIndexOffset: 900,
        }).bindPopup(`<b>${MASCOT_NAMES[kind]}</b><br/>${agents[ai].name} · ${r.stops.length} stops · ${r.distance_km} km`).addTo(g);
      }
    });

    orders.forEach((o) => {
      bounds.push([o.lat, o.lng]);
      const ow = owner[o.id];
      const cancelled = o.status === "cancelled";
      const color = cancelled ? "#94a3b8" : ow ? colorOf[ow.agent] : "#475569";
      const marker = L.marker([o.lat, o.lng], {
        icon: pin(color, cancelled ? "×" : ow ? String(ow.seq) : "!", 24, cancelled),
      }).addTo(g);
      const agentName = ow ? agents.find((a) => a.id === ow.agent)?.name : "—";
      marker.bindPopup(
        `<b>${o.id} · ${o.name}</b><br/>` +
          `Priority: ${PRIORITY_LABEL[o.priority]} · Packages: ${o.demand}<br/>` +
          `Window: ${clock(o.tw_start + o.delay)}–${clock(o.tw_end + o.delay)}` +
          (o.delay ? ` (delayed ${o.delay} min)` : "") + `<br/>` +
          (cancelled
            ? "<i>Cancelled</i>"
            : ow
            ? `Agent: ${agentName} · Stop #${ow.seq}<br/>ETA ${clock(ow.arrival)}` +
              (ow.late > 0.5 ? ` <span style="color:#dc2626">(${Math.round(ow.late)} min late)</span>` : " ✓ on time")
            : "<b style='color:#dc2626'>Unassigned</b>")
      );
    });

    L.marker([depot.lat, depot.lng], {
      icon: pin("#0f172a", "D", 30),
      zIndexOffset: 1000,
    }).bindPopup(`<b>${depot.name}</b>`).addTo(g);

    if (picked) {
      L.marker([picked.lat, picked.lng], { icon: pin("#f59e0b", "+", 28) }).addTo(g);
    }

    if (!fitted.current && bounds.length > 1) {
      m.fitBounds(L.latLngBounds(bounds), { padding: [40, 40] });
      fitted.current = true;
    }
  }, [state, picked]);

  return (
    <div className="relative h-full w-full">
      <div ref={el} className="h-full w-full rounded-xl" />
      {pickMode && (
        <div className="absolute left-1/2 top-3 z-[1000] -translate-x-1/2 rounded-full bg-amber-500 px-4 py-1.5 text-sm font-semibold text-white shadow">
          Click on the map to choose the delivery location
        </div>
      )}
    </div>
  );
}
