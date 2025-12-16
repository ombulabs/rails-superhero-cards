from pathlib import Path

import sentry_sdk
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from langfuse import Langfuse
from openinference.instrumentation.llama_index import LlamaIndexInstrumentor
from starlette.middleware.base import BaseHTTPMiddleware

from .api import router
from .config import settings
from .dependencies import lifespan
from .exceptions import ImageFormatError, ImageSizeError, InputValidationError


class LimitUploadSize(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI, max_upload_size: int):
        super().__init__(app)
        self.max_upload_size = max_upload_size

    async def dispatch(self, request: Request, call_next) -> Response:  # noqa: ANN001
        if request.method == "POST":
            content_length = request.headers.get("content-length")
            if content_length and int(content_length) > self.max_upload_size:
                return JSONResponse(
                    status_code=400,
                    content={"error": "Image too large. Maximum size is 4MB."},
                )
        return await call_next(request)


app = FastAPI(lifespan=lifespan)

# Limit request body size to 4MB
app.add_middleware(LimitUploadSize, max_upload_size=4 * 1024 * 1024)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

frontend_build_path = Path(__file__).parent.parent / "frontend" / "dist"

if frontend_build_path.exists():
    app.mount("/assets", StaticFiles(directory=frontend_build_path / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str) -> FileResponse:
        file_path = frontend_build_path / full_path
        if file_path.is_file():
            return FileResponse(file_path)

        return FileResponse(frontend_build_path / "index.html")


if settings.environment == "production":
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        enable_tracing=settings.sentry_enable_tracing,
        ignore_errors=[InputValidationError, ImageFormatError, ImageSizeError],
    )

if settings.enable_langfuse:
    langfuse = Langfuse(
        host=settings.langfuse_base_url,
        public_key=settings.langfuse_public_key,
        secret_key=settings.langfuse_secret_key,
    )
    LlamaIndexInstrumentor().instrument()
