import os
import logging
from typing import Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from openai import OpenAI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RevenueRecoveryAgent")

class RecoveryActionPlan(BaseModel):
    failure_category: str = Field(description="Category: Technical, Financial, Security, or Network")
    root_cause: str = Field(description="Brief explanation of why the payment failed")
    recommended_action: str = Field(description="Actionable step for recovery")
    retry_recommended: bool = Field(description="True if an automatic retry should be attempted")
    retry_delay_hours: int = Field(description="Hours to wait before retrying (0-72)")
    optimal_channel: str = Field(description="Best channel to reach user: whatsapp, email, or sms")
    customer_message: str = Field(description="Personalized, empathetic message to customer")
    ai_confidence_score: float = Field(description="Confidence score from 0.0 to 1.0")
    fallback_used: bool = Field(default=False, description="Whether rule-based safety net was triggered")


class RevenueRecoveryAgent:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

    def execute_deterministic_fallback(self, payment_data: Dict[str, Any], reason: str) -> RecoveryActionPlan:
        logger.warning(f"Fallback triggered for payment {payment_data.get('payment_id')}. Reason: {reason}")
        
        error_code = str(payment_data.get("error_code", "UNKNOWN_ERROR")).upper()
        customer_name = payment_data.get("customer_name", "Valued Customer")
        amount = float(payment_data.get("amount", 0)) / 100.0
        currency = payment_data.get("currency", "INR")
        
        if "INSUFFICIENT" in error_code or "BALANCE" in error_code:
            return RecoveryActionPlan(
                failure_category="Financial",
                root_cause="Insufficient account balance or credit limit exceeded.",
                recommended_action="Schedule retry on typical salary payout date.",
                retry_recommended=True,
                retry_delay_hours=48,
                optimal_channel="whatsapp",
                customer_message=f"Hi {customer_name}, your payment of {currency} {amount:.2f} was unsuccessful due to balance constraints. Click to complete payment: https://rzp.io/r/fallback-pay",
                ai_confidence_score=0.90,
                fallback_used=True
            )
        elif "GATEWAY" in error_code or "TIMEOUT" in error_code or "NETWORK" in error_code:
            return RecoveryActionPlan(
                failure_category="Technical",
                root_cause="Banking gateway or network timeout during authorization.",
                recommended_action="Immediate auto-retry via alternate payment route.",
                retry_recommended=True,
                retry_delay_hours=1,
                optimal_channel="sms",
                customer_message=f"Hi {customer_name}, your transaction of {currency} {amount:.2f} timed out on the bank server. Retrying automatically in 1 hour.",
                ai_confidence_score=0.95,
                fallback_used=True
            )
        else:
            return RecoveryActionPlan(
                failure_category="Security/Auth",
                root_cause="Payment authentication or OTP verification failed.",
                recommended_action="Prompt customer to manually re-authorize using direct link.",
                retry_recommended=False,
                retry_delay_hours=0,
                optimal_channel="email",
                customer_message=f"Hi {customer_name}, we couldn't complete your payment of {currency} {amount:.2f}. Please click here to verify details: https://rzp.io/r/fallback-pay",
                ai_confidence_score=0.85,
                fallback_used=True
            )

    def process_failed_payment(self, payment_data: Dict[str, Any]) -> RecoveryActionPlan:
        # If API Key is not set, run deterministic engine immediately
        if not self.client:
            return self.execute_deterministic_fallback(payment_data, "OPENAI_API_KEY missing")

        prompt = f"""
        Analyze this failed payment webhook:
        Payment ID: {payment_data.get('payment_id')}
        Customer: {payment_data.get('customer_name')}
        Amount: {float(payment_data.get('amount', 0))/100} {payment_data.get('currency')}
        Error Code: {payment_data.get('error_code')}
        Error Description: {payment_data.get('error_description')}
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a fintech AI recovery agent. Return clear strategy responses."},
                    {"role": "user", "content": prompt}
                ],
                timeout=4.0
            )
            return self.execute_deterministic_fallback(payment_data, "Parsing LLM success fallback")

        except Exception as e:
            return self.execute_deterministic_fallback(payment_data, str(e))