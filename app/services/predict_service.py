import asyncio
import time
from functools import lru_cache
from typing import Dict, Any, Optional
from app.core.exceptions import ModelUnavailable, PredictionTimeout
from app.services.gc_tuning import RequestGCTuner
from async_lru import alru_cache


# async ML prediction function
async def async_call_credit_risk_model(model_name: str, features: Dict[str, float]) -> Dict[str, Any]:
    """
    Simulate a ML prediction call with async event loop
    """
    await asyncio.sleep(0.05)  # simulate async I/O latency

    # Simulated prediction logic
    score = (features["income"] / 200000) + (features["credit_history_length"] / 10) - (features["loan_amount"] / 100000)

    # Clamp score between 0-1
    prediction = max(0.0, min(1.0, round(score, 2)))

    return {
        "prediction": prediction,
        "confidence": 0.89,
        "model_version": "v2.1"
    }

def preprocess(model_name: str, features: Dict[str, float]) -> Dict[str, Any]:
    """
    Example preprocessing: type coercion, validation, normalization.
    """
    try:
        processed = {k: float(v) for k, v in features.items()}
    except Exception:
        raise ModelUnavailable("Invalid feature values")

    return processed

def postprocess(response: Dict[str, Any], start_ms: float) -> Dict[str, Any]:
    """
    Adds metadata such as latency.
    """
    end_ms = (time.time() - start_ms) * 1000

    return {
        "prediction": response["prediction"],
        "confidence": response["confidence"],
        "metadata": {
            "model_version": response["model_version"],
            "processing_ms": str(int(end_ms))
        }
    }
# Least-recently-used cache: it's like a hashmap
# if the same key is passed, alru_cache will return the previous result and bypass the async event loop -> need to use alru_cache to cache async results
# Note: we cannot use functools.lru_cache as this was created before async existed. Therefore, when the async function returns a coroutine object, lru_cache doesn't know and cache the coroutine object NOT the awaited result.
# Why the 2nd time the same request hit functools.lru_cache will fail?
# Answer: because FastAPI will await the SAME coroutine object. Once a coroutine executes it code, it will then become exhausted and cannot be reused. -> we need to create a new coroutine or reuse the result -> this is why alru_cache comes into play
@alru_cache(maxsize=256)
async def cached_prediction(key: frozenset) -> Dict[str, Any]:
    """
    Cache based on model_name + features
    """
    data = dict(key)
    model_name = data.pop("__model__")
    return await async_call_credit_risk_model(model_name, data)

async def predict_service(request_id: str, model_name: str, features: Dict[str, Any]) -> Dict[str, Any]:
    """
    Full ML wrapper service pipeline:
    - preprocess
    - cache check
    - async model call
    - postprocess
    """
    with RequestGCTuner():
        start_time = time.time()
        processed_features = preprocess(model_name, features)

        # Build cache key:
        # we can not use {"__model__": model_name, **processed_features} as the cache key because it's a dict
        # we have to convert the dict to a frozenset so it become hashable
        cache_key = frozenset({"__model__": model_name, **processed_features}.items())
        # In this case, ** is to merge 2 dict together
        # result of {"__model__": model_name, **processed_features} is:
        # {
        #     "__model__": "credit_risk_classifier",
        #     "age": 29,
        #     "income": 72000
        # }

        # result of {"__model__": model_name, **processed_features}.items() is:
        # dict_items([
        #     ("__model__", "credit_risk_classifier"),
        #     ("age", 29),
        #     ("income", 72000)
        # ])
        # => If we don't do .items(), we don't have key-value pairs and frozenset will only have the keys in it (missing all the values)

        # Call the (cached) model
        try:
            model_response = await cached_prediction(cache_key)
        except asyncio.TimeoutError:
            raise PredictionTimeout("Model inference took too long")

        # Combine into final phase
        final = postprocess(model_response, start_time)


    # ** = (a) unpacking dictionary OR (b) merge 2 dictionaries into 1
    #  in this case, ** is to merge 2 dict together
    return {
        "request_id": request_id,
        "model_name": model_name,
        **final
    }















