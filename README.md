# Autonomous AI Revenue Recovery Engine 🚀
> Built for the **Razorpay AI Builder Hackathon** (Track 3: AI Revenue Recovery)

An intelligent, autonomous payment recovery system designed to analyze failed payment webhooks, categorize root causes, dynamically schedule retries, and deliver personalized customer recovery communications—backed by a **100% deterministic fallback safety net**.

---

## 📌 Problem Statement
Payment failures cost merchants millions annually in lost revenue and customer churn. Traditional retry systems rely on static interval retries that fail to account for failure contexts—repeatedly attempting transactions during bank downtime or spamming users when card balances are low. 

Merchants require an adaptive engine that:
1. **Differentiates** between temporary technical glitches and financial constraints.
2. **Schedules intelligent retries** based on optimal recovery windows.
3. **Engages users dynamically** via personalized communication channels (WhatsApp, SMS, Email).
4. **Guarantees zero downtime** even when external LLM APIs experience latency or outages.

---

## 🏗 System Architecture

                  
                   ┌────────────────────────┐
                   │ Failed Payment Webhook │
                   └───────────┬────────────┘
                               │
                               ▼
                   ┌────────────────────────┐
                   │  FastAPI Ingestion Hub │
                   └───────────┬────────────┘
                               │
              ┌────────────────┴────────────────┐
              ▼                                 ▼
           
     LLM Decision Engine            Deterministic Safety 
    (Structured Output)            Fallback Engine    
           
              │                                 │
              │ (On API Timeout / Exception)    | 
              └────────────────┬────────────────┘
                               │
                               ▼
                   ┌────────────────────────┐
                   │ Structured Plan Output │
                   │ ├─ Failure Category    │
                   │ ├─ Retry Schedule      │
                   │ ├─ Optimal Channel     │
                   │ └─ Personalized Nudge  │
                   └────────────────────────┘

---

## Key Features & Evaluator Metrics

* **Autonomous Categorization:** Automatically routes failures into `Technical`, `Financial`, `Security`, or `Network` buckets.
* **Deterministic Fallback Engine (Resilience Metric):** If the LLM API times out, fails, or receives malformed data, the engine seamlessly switches to rule-based fallback decision trees to guarantee high availability.
* **Smart Retry & Multi-Channel Nudging:** Calculates dynamic retry delays (e.g., 48 hours for balance issues vs. 1 hour for network timeouts) and generates personalized recovery messages with direct links.
* **Pydantic Data Validation:** Ensures strict typing and structured JSON responses with zero schema drift.

---

## 🛠 Tech Stack

* **Language:** Python 3.10+
* **Framework:** FastAPI
* **Data Validation:** Pydantic v2
* **LLM Engine:** OpenAI GPT-4o-mini (Structured Outputs)
* **Server:** Uvicorn

---

## 📂 Project Structure

```text
razorpay-revenue-recovery/
├── main.py                  # FastAPI server & route handlers
├── recovery_agent.py        # Core AI engine & deterministic fallback logic
├── requirements.txt         # Project dependencies
├── mock_webhooks.json       # Sample test payloads for evaluation
└── README.md                # System documentation

🚀 Quickstart Guide
1. Prerequisites
Ensure you have Python 3.10+ installed on your system.

2. Clone & Install Dependencies

git clone [https://github.com/PujithaAtmakuri/Razorpay-revenue-recovery.git]
cd Razorpay-revenue-recovery
py -m pip install -r requirements.txt

3. Run the API Server
Bash
py main.py
The server will start at http://127.0.0.1:8000.

🧪 Testing the API
Interactive API Documentation (Swagger UI)
Navigate to http://127.0.0.1:8000/docs in your web browser.

Expand the POST /api/v1/recover-payment endpoint.

Click Try it out, paste the following payload, and click Execute:

JSON
{
  "event": "payment.failed",
  "payment_id": "pay_TEST999",
  "amount": 150000,
  "currency": "INR",
  "customer_name": "Pujitha Atmakuri",
  "customer_email": "pujitha@example.com",
  "customer_phone": "+919876543210",
  "method": "upi",
  "error_code": "BAD_REQUEST_INSUFFICIENT_FUNDS",
  "error_description": "UPI transaction failed due to low account balance",
  "gateway": "NPCI_UPI"
}
Example API Response (200 OK)
JSON
{
  "success": true,
  "message": "Recovery plan generated successfully",
  "recovery_record": {
    "payment_id": "pay_TEST999",
    "processed_at": "2026-09-02T08:13:11.007844+00:00",
    "customer": "Pujitha Atmakuri",
    "amount_inr": 1500.0,
    "error_code": "BAD_REQUEST_INSUFFICIENT_FUNDS",
    "ai_strategy": {
      "failure_category": "Financial",
      "root_cause": "Insufficient account balance or credit limit exceeded.",
      "recommended_action": "Schedule retry on typical salary payout date.",
      "retry_recommended": true,
      "retry_delay_hours": 48,
      "optimal_channel": "whatsapp",
      "customer_message": "Hi Pujitha Atmakuri, your payment of INR 1500.00 was unsuccessful due to balance constraints. Click to complete payment: [https://rzp.io/r/fallback-pay](https://rzp.io/r/fallback-pay)",
      "ai_confidence_score": 0.9,
      "fallback_used": true
    },
    "scheduled_retry_time": "2026-09-04T08:13:11.007820+00:00",
    "status": "SCHEDULED"
  }
}
📜 License
This project is open-source and available under the MIT License.
