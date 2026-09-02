import json
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, List
from datetime import datetime, timezone, timedelta  # <-- Fixed: Added timedelta here
from recovery_agent import RevenueRecoveryAgent, RecoveryActionPlan

app = FastAPI(
    title="Razorpay AI Revenue Recovery Engine",
    description="Autonomous payment failure recovery system with AI decisioning and deterministic fallback.",
    version="1.0.0"
)

agent = RevenueRecoveryAgent()

# In-memory audit database for demonstration
AUDIT_LOGS: List[Dict[str, Any]] = []

class FailedPaymentWebhook(BaseModel):
    event: str = "payment.failed"
    payment_id: str
    amount: int  # in paisa
    currency: str = "INR"
    customer_name: str
    customer_email: str
    customer_phone: str
    method: str  # card, upi, netbanking
    error_code: str
    error_description: str
    gateway: str

@app.post("/api/v1/recover-payment", response_model=Dict[str, Any])
async def handle_failed_payment(webhook: FailedPaymentWebhook, background_tasks: BackgroundTasks):
    """
    Core API Endpoint: Ingests failed payment webhooks, processes them via AI, 
    and returns a structured recovery plan and execution timeline.
    """
    if webhook.event != "payment.failed":
        raise HTTPException(status_code=400, detail="Invalid event type")

    payment_data = webhook.model_dump()
    
    # Run recovery pipeline
    plan: RecoveryActionPlan = agent.process_failed_payment(payment_data)
    
    # Calculate execution schedule
    scheduled_time = datetime.now(timezone.utc) + timedelta(hours=plan.retry_delay_hours)
    
    record = {
        "payment_id": webhook.payment_id,
        "processed_at": datetime.now(timezone.utc).isoformat(),
        "customer": webhook.customer_name,
        "amount_inr": webhook.amount / 100.0,
        "error_code": webhook.error_code,
        "ai_strategy": plan.model_dump(),
        "scheduled_retry_time": scheduled_time.isoformat(),
        "status": "SCHEDULED" if plan.retry_recommended else "ACTION_REQUIRED"
    }
    
    AUDIT_LOGS.append(record)
    
    return {
        "success": True,
        "message": "Recovery plan generated successfully",
        "recovery_record": record
    }

@app.get("/api/v1/audit-logs")
async def get_audit_logs():
    """Returns past recovery actions and audit records."""
    return {
        "total_records": len(AUDIT_LOGS),
        "logs": AUDIT_LOGS
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "engine": "Razorpay AI Recovery Agent v1"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)