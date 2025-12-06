from datetime import datetime
from typing import Dict, Optional
from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    # three dots ... means this is a required field. Field() enables the following capabilities:
    # descriptions
    # validation
    # constraints
    # examples
    # minimum / maximum
    # values
    # regex
    # rules
    # default
    # factories
    # metadata
    request_id: str = Field(..., description="Unique request identifier", pattern="^[0-9]+$", min_length=4, max_length=15)
    model_name: str = Field(..., examples=["model_fraud_detection_v1.3"])
    features: Dict[str, float] = Field(..., description="Key-value feature inputs for the model",
        examples=[{"transaction_amount": 120.50, "user_age": 32}])
    timestamp: Optional[datetime] = Field(default_factory=datetime.now, description="Time request was generated")

""" SAMPLE:
{
    "request_id": "2025012590",
    "model_name": "credit_risk_classifier",
    "features": {
        "income": 72000,
        "age": 29,
        "credit_history_length": 5,
        "loan_amount": 30000
    }
}
"""