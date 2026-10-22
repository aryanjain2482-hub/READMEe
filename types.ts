export interface Depot { lat: number; lng: number; name: string }
export interface Agent { id: string; name: string; capacity: number; available: boolean }
export interface Order {
  id: string; name: string; lat: number; lng: number; demand: number; priority: number;
  tw_start: number; tw_end: number; service_time: number;
  status: "pending" | "cancelled" | "delayed"; delay: number; locked_agent: string | null;
}
export interface Stop { order_id: string; arrival: number; wait: number; late: number }
export interface Route {
  agent_id: string; stops: Stop[]; distance_km: number; duration_min: number; load: number;
}
export interface Metrics {
  total_distance_km: number; total_duration_min: number; late_deliveries: number;
  total_late_minutes: number; unassigned: number; balance_gap: number; priority_late: number;
}
export interface Solution {
  method: string; routes: Route[]; unassigned: string[]; metrics: Metrics; solve_ms: number;
}
export interface Improvement {
  distance_pct: number; late_deliveries_saved: number; late_minutes_pct: number;
  priority_late_saved: number; balance_gap_saved: number;
}
export interface LogEntry {
  id: number; time: string; type: string; description: string; reoptimize_ms: number;
  solver: string; orders_moved: number; before: Metrics | null; after: Metrics;
}
export interface AppState {
  scenario: { depot: Depot; agents: Agent[]; orders: Order[] };
  optimized: Solution | null;
  baseline: Solution | null;
  improvement: Improvement | null;
  log: LogEntry[];
  matrix_source: string;
  solver: string | null;
}

export const AGENT_COLORS = ["#2563eb", "#dc2626", "#16a34a", "#9333ea", "#ea580c", "#0891b2"];
export const PRIORITY_LABEL: Record<number, string> = { 1: "Normal", 2: "High", 3: "Urgent" };

/** Minutes from shift start -> clock time, shift starts 09:00. */
export function clock(min: number): string {
  const total = 9 * 60 + Math.round(min);
  const h = Math.floor(total / 60) % 24;
  const m = total % 60;
  return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}`;
}
