import time
import uuid
import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from bot import VeraComposer

# Set up absolute paths for Docker stability
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DASHBOARD_PATH = os.path.join(BASE_DIR, "dashboard.html")

app = FastAPI(title="magicpin Vera AI Engine", version="1.0.0")

# --- STARTUP LOGGING (Extra Hardened) ---
try:
    raw_port = os.environ.get("PORT", "8080")
    PORT = int(raw_port) if raw_port.strip() else 8080
except Exception:
    PORT = 8080

print(f"!!! VERA ENGINE BOOTING ON PORT {PORT} !!!")

composer = VeraComposer()

# --- IN-MEMORY STATE MANAGEMENT (Top 1 Performance) ---
# O(1) retrieval is critical for the 10s judge timeout
context_store: Dict[Tuple[str, str], Dict] = {}
conversations: Dict[str, List[Dict]] = {}
sent_keys = set()

# --- SCHEMAS ---
class ContextPayload(BaseModel):
    scope: str
    context_id: str
    version: int
    payload: Dict[str, Any]
    delivered_at: str

class TickRequest(BaseModel):
    merchant_ids: List[str]

class ReplyRequest(BaseModel):
    conversation_id: str
    merchant_id: str
    customer_id: Optional[str]
    message: str
    turn_number: int

# --- ENDPOINTS ---

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Premium Dashboard for human evaluators with hardened path resolution."""
    try:
        if not os.path.exists(DASHBOARD_PATH):
            return "<html><body><h1>Vera Engine Online</h1><p>Dashboard file missing.</p></body></html>"
        with open(DASHBOARD_PATH, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"<html><body><h1>Vera Engine Online</h1><p>Error: {str(e)}</p></body></html>"

@app.get("/v1/healthz")
async def healthz():
    """Judge calls this every 60s to check liveness."""
    return {"status": "ok", "uptime": time.time()}

@app.get("/v1/metadata")
async def metadata():
    return {
        "team_name": "Team RUTHLESS",
        "model": "Deterministic Orchestration Engine v1.0",
        "version": "1.0.0-PROD"
    }

@app.post("/v1/context")
async def receive_context(payload: ContextPayload):
    key = (payload.scope, payload.context_id)
    context_store[key] = payload.payload
    return {"accepted": True}

@app.post("/v1/tick")
async def tick(request: TickRequest):
    actions = []
    all_triggers = [ctx for (scope, _), ctx in context_store.items() if scope == 'trigger']
    
    for m_id in request.merchant_ids:
        merch = context_store.get(('merchant', m_id))
        if not merch: continue
        cat_id = merch.get('identity', {}).get('category_id')
        cat = context_store.get(('category', cat_id))
        if not cat: continue

        for trg in all_triggers:
            t_id = trg.get('trigger_id')
            s_key = trg.get('suppression_key', f"{t_id}:{m_id}")
            if s_key in sent_keys: continue
            
            trg_m_id = trg.get('merchant_id')
            if trg_m_id and trg_m_id != m_id: continue
            
            cust_id = trg.get('customer_id')
            cust = context_store.get(('customer', cust_id)) if cust_id else None
            
            try:
                result = composer.compose(cat, merch, trg, cust)
                conv_id = f"conv_{m_id}_{int(time.time())}"
                conversations[conv_id] = [{"from": "vera", "body": result["body"]}]
                sent_keys.add(s_key)

                actions.append({
                    "conversation_id": conv_id,
                    "merchant_id": m_id,
                    "customer_id": cust_id,
                    "send_as": result["send_as"],
                    "trigger_id": t_id,
                    "body": result["body"],
                    "cta": result["cta"],
                    "suppression_key": s_key,
                    "rationale": result["rationale"]
                })
            except: continue
                
    return {"actions": actions}

@app.post("/v1/reply")
async def reply(request: ReplyRequest):
    m_id = request.merchant_id
    msg = request.message.strip()
    merch = context_store.get(('merchant', m_id))
    cat_id = merch.get('identity', {}).get('category_id') if merch else None
    cat = context_store.get(('category', cat_id)) if cat_id else None
    
    # Simple multi-turn logic
    if "ok" in msg.lower() or "theek" in msg.lower():
        return {"body": "Ji, process shuru kar diya hai.", "cta": "open_ended", "rationale": "Affirmative response."}
    
    if cat and merch:
        body = f"Ji {merch['identity'].get('owner_first_name', 'Partner')}, isse visibility badhegi. Continue karein?"
        return {"body": body, "cta": "YES/STOP", "rationale": "Follow-up."}

    return {"body": "Hum ispe kaam kar rahe hain.", "cta": "open_ended", "rationale": "Fallback."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
