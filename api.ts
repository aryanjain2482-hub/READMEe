import type { AppState } from "./types";

async function call(method: string, path: string, body?: unknown): Promise<AppState> {
  const res = await fetch(`/api${path}`, {
    method,
    headers: { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  if (!res.ok) {
    let msg = `${res.status} ${res.statusText}`;
    try { msg = (await res.json()).detail ?? msg; } catch { /* ignore */ }
    throw new Error(msg);
  }
  return res.json();
}

export interface NewOrderInput {
  name: string; lat: number; lng: number; demand: number; priority: number;
  tw_start: number; tw_end: number;
}

export const api = {
  state: () => call("GET", "/state"),
  optimize: () => call("POST", "/optimize"),
  reset: () => call("POST", "/reset"),
  addOrder: (o: NewOrderInput) => call("POST", "/orders", o),
  cancel: (id: string) => call("POST", `/orders/${id}/cancel`),
  restore: (id: string) => call("POST", `/orders/${id}/restore`),
  delay: (id: string, minutes: number) => call("POST", `/orders/${id}/delay`, { minutes }),
  reassign: (id: string, agent_id: string | null) =>
    call("POST", `/orders/${id}/reassign`, { agent_id }),
  agentAvailability: (id: string, available: boolean) =>
    call("POST", `/agents/${id}/availability`, { available }),
};
