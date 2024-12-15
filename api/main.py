from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from api.logger_config import setup_logging
from api.routers import upload, explore, config

# Load environment variables from .env file
load_dotenv()

# Initialize logging
setup_logging()

app = FastAPI()

# Create FastAPI app with custom Swagger UI endpoint
app = FastAPI(docs_url="/docs", openapi_url="/docs/openapi.json")

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
app.include_router(config.router, prefix="/api")

# Serve index.html at the root path
@app.get("/view", include_in_schema=False)
async def read_index():
    return FileResponse("index.html")