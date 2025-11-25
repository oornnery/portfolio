import logging
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from app.config import settings
from app.db import init_db

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan,
    docs_url=None if settings.ENV == "production" else "/docs",
)

# Register middlewares using the correct pattern
app.add_middleware(
    CORSMiddleware,  # type: ignore
    allow_origins=settings.ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    TrustedHostMiddleware,  # type: ignore
    allowed_hosts=settings.ALLOWED_HOSTS,
)


@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=404,
        content={
            "status": "error",
            "type": "not_found",
            "message": f"A rota '{request.url.path}' não foi encontrada no sistema.",
        },
    )


@app.exception_handler(500)
async def internal_server_error_handler(request: Request, exc: Exception):
    logger.error(f"❌ ERRO CRÍTICO: {exc!s}")

    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "type": "server_error",
            "message": "An unexpected error occurred. Please try again later.",
        },
    )


@app.get("/")
async def root():
    return JSONResponse(status_code=200, content={"message": "OK"})


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "message": "Server is running",
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/helloworld")
async def hello_world():
    return {"message": "Hello World!"}
