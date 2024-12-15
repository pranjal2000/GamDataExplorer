import os
from fastapi import APIRouter

router = APIRouter()

@router.get("/config")
def get_config():
    api_keys = os.getenv("API_KEYS", "").split(",")
    return {"api_keys": api_keys}