from fastapi import FastAPI

from .api.auth import router as auth_router
from .api.preferences import router as preferences_router

app = FastAPI(title="AfterCart API", version="0.1.0")

app.include_router(auth_router, prefix="/api")
app.include_router(preferences_router, prefix="/api")
