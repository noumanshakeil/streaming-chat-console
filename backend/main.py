from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.api import api_router
from backend.db import init_db
from backend.logging_config import configure_logging
from backend.middleware import RequestContextMiddleware

@asynccontextmanager
async def lifespan(_app: FastAPI):
    configure_logging()
    await init_db()
    yield

app = FastAPI(title="Streaming Chat Console", version="2.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestContextMiddleware)
app.mount("/static", StaticFiles(directory="backend/static"), name="static")
app.include_router(api_router)
