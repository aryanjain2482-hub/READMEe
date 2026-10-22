"""RouteWise API (FastAPI).

Run:  uvicorn app.main:app --reload --port 8000
Docs: http://localhost:8000/docs
"""
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .engine import HAS_ORTOOLS, Engine

app = FastAPI(title="RouteWise API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = Engine()


class NewOrder(BaseModel):
    name: str = ""
    lat: float
    lng: float
    demand: int = Field(1, ge=1, le=10)
    priority: int = Field(1, ge=1, le=3)
    tw_start: int = Field(0, ge=0)
    tw_end: int = Field(240, ge=0)


class DelayBody(BaseModel):
    minutes: int = Field(30, ge=1, le=240)


class ReassignBody(BaseModel):
    agent_id: Optional[str] = None  # null = unlock, let optimizer decide


class AgentBody(BaseModel):
    available: bool


def _guard(fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e).strip("'\""))
    return engine.snapshot()


@app.get("/api/health")
def health():
    return {"status": "ok", "ortools": HAS_ORTOOLS}


@app.get("/api/state")
def state():
    return engine.snapshot()


@app.post("/api/optimize")
def optimize():
    engine.optimize("manual", "Manual re-optimization requested")
    return engine.snapshot()


@app.post("/api/reset")
def reset():
    return engine.reset()


@app.post("/api/orders")
def add_order(body: NewOrder):
    engine.add_order(**body.model_dump())
    return engine.snapshot()


@app.post("/api/orders/{order_id}/cancel")
def cancel(order_id: str):
    return _guard(engine.cancel_order, order_id)


@app.post("/api/orders/{order_id}/restore")
def restore(order_id: str):
    return _guard(engine.restore_order, order_id)


@app.post("/api/orders/{order_id}/delay")
def delay(order_id: str, body: DelayBody):
    return _guard(engine.delay_order, order_id, body.minutes)


@app.post("/api/orders/{order_id}/reassign")
def reassign(order_id: str, body: ReassignBody):
    return _guard(engine.reassign_order, order_id, body.agent_id)


@app.post("/api/agents/{agent_id}/availability")
def agent_availability(agent_id: str, body: AgentBody):
    return _guard(engine.set_agent_available, agent_id, body.available)
