import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from checkyourdata.api.routes import router
from checkyourdata.db.session import init_db

# Mirrors the repo layout (backend/checkyourdata/api/main.py -> ../../../frontend/dist),
# which the Dockerfile replicates so this needs no env var override in production.
FRONTEND_DIST = Path(__file__).resolve().parents[3] / "frontend" / "dist"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    init_db()
    yield


app = FastAPI(title="CheckYourData", lifespan=lifespan)

cors_origins = (os.environ.get("CORS_ORIGINS") or "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

# Serves the built frontend when present (Docker/production). Registered after the API
# router so /datasets/... is never shadowed. Absent in day-to-day local dev, where the
# frontend runs separately via `npm run dev` — API-only mode keeps working as before.
if FRONTEND_DIST.is_dir():

    @app.api_route("/{full_path:path}", methods=["GET", "HEAD"])
    async def serve_frontend(full_path: str) -> FileResponse:
        candidate = (FRONTEND_DIST / full_path).resolve()
        if candidate.is_file() and candidate.is_relative_to(FRONTEND_DIST):
            return FileResponse(candidate)
        return FileResponse(FRONTEND_DIST / "index.html")
