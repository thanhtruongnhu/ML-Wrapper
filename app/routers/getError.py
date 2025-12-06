from fastapi import APIRouter

from app.core.exceptions import BadRequest

router = APIRouter(prefix='/error', tags=["Errors"])

@router.get("/valueerror")
async def valueerror():
    raise ValueError("invalid value")

@router.get("/keyerror")
async def keyerror():
    raise KeyError("missing key")

@router.get("/demo/bad")
async def demo_bad():
    raise BadRequest(message="Invalid input for demo", details={"field": "age"})

@router.get("/runtime")
async def runtime_error():
    raise RuntimeError("This is a runtime error in route")