from datetime import datetime
from typing import Dict, Optional
from pydantic import BaseModel, Field


class PredictResponse(BaseModel):
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
    request_id: str
    model_name: str
    prediction: float = Field(..., description="Primary model output", examples=["0.87"])
    confidence: float = Field(..., ge=0, le=1, examples=["0.92"])
    metadata: Optional[Dict[str, str]] = Field(
        default=None,
        examples=[{"model_version": "1.3.4", "processing_ms": "12"}]
    )

""" SAMPLE:
{
    "request_id": "2025012590",
    "model_name": "credit_risk_classifier",
    "prediction": 0.73,
    "confidence": 0.89,
    "metadata": {
        "model_version": "v2.1",
        "processing_ms": "14"
    }
}
"""