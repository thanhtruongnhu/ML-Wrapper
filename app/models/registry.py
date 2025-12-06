from typing import Dict
from .base import BaseModel
from .credit_risk_model import FakeCreditRiskModel

class ModelRegistry:
    # If we have multiple models, we can register them here
    _models: Dict[str, BaseModel] = {
        "credit_risk_classifier": FakeCreditRiskModel()
    }
    # what if we don't use @classmethod before def get()? because the registry has no instance-specific state - it's just a static lookup table.
    @classmethod
    def get(cls, model_name: str) -> BaseModel:
        if model_name not in cls._models:
            raise ValueError(f"Model '{model_name}' not found in registry.")
        return cls._models[model_name]
