"""FastAPI application instance for DeepTutor API."""

from deeptutor.api.main import app
from deeptutor.api.routers.diagnostic import router as diagnostic_router

# Ensure diagnostic router is included if not already present
if not any(
    hasattr(route, "path") and "/diagnostic" in route.path
    for route in app.routes
):
    app.include_router(diagnostic_router)

__all__ = ["app"]
