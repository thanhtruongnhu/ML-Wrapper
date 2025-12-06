from abc import ABC, abstractmethod
from typing import Dict, Any

# To force all models to behave the same way (same method names, same structure) so the service layer doesn’t care which model is used.
class BaseModel(ABC):
    @abstractmethod
    # abstractmethod marks predict as mandatory - any child class MUST implement it. Python will raise TypeError if you try to instantiate a child class without implementing predict
    async def predict(self, features:Dict[str, float]) -> Dict[str, Any]:
        pass