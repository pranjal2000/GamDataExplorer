from fastapi import FastAPI, Request
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from api.logger_config import setup_logging
from api.routers import upload, explore

# Load environment variables from .env file
load_dotenv()

# Initialize logging
setup_logging()

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow your frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
app.mount("/static", StaticFiles(directory=".", html=True), name="static")

app.include_router(upload.router, prefix="/api")
app.include_router(explore.router, prefix="/api")