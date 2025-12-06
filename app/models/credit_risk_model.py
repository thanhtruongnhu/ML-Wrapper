from typing import Dict, Any
import asyncio
from .base import BaseModel

# This is one of the ML models which complies with BaseModel interface. There could be many other models.
class FakeCreditRiskModel(BaseModel):
    async def predict(self, features: Dict[str, float]) -> Dict[str, Any]:

        await asyncio.sleep(0.05)

        score = (
            features["income"] * 0.00001 +
            features["age"] * 0.1 -
            features["loan_amount"] * 0.00005 +
            features["credit_history_length"] * 0.5
            )
        
        # Clamp confidence between 0-1
        confidence = max(0.0, min(1.0, round(score, 2)))

        return {
            "prediction": score,
            "confidence": confidence,
            "model_version": "v1.0"
        }