from fastapi import APIRouter
from app.schemas.request import PredictRequest
from app.schemas.response import PredictResponse
from app.services.predict_service import predict_service

router = APIRouter(prefix='/predict', tags=["Predict"])

@router.post("/", response_model = PredictResponse)
async def predict(request: PredictRequest) -> PredictResponse:
    result = await predict_service(request.request_id, request.model_name, request.features)
    # **result = unpacking dictionary into keyword arguments, for example: age=30, income=70000
    return PredictResponse(**result)

# async def predict(request: PredictRequest) -> PredictResponse:
# "-> PredictResponse" above DO NOT enforce the validations specified in response.py at runtime. It only:
# (a) help linters to check type and shows annotations/recommendations,
# (b) helps IDE autocomplete

# @router.post("/", response_model = PredictResponse)
# "response_model = PredictResponse" above will ENFORCE the validation at runtime. It will also do the following:
# (a) serialize response payload to JSON
# (b) generate Swagger
# (c) filter out extra fields
# Ultimately, this ensures predictable, consistent response