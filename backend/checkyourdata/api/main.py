from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from checkyourdata.api.routes import router
from checkyourdata.db.session import init_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    init_db()
    yield


app = FastAPI(title="CheckYourData", lifespan=lifespan)
app.include_router(router)
