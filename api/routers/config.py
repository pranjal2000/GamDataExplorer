import os
from fastapi import APIRouter

router = APIRouter()

@router.get("/config")
def get_config():
    """
    Get the API keys from the environment variables.

    Returns:
        dict: A dictionary containing the API keys.
    """
    api_keys = os.getenv("API_KEYS", "").split(",")
    return {"api_keys": api_keys}