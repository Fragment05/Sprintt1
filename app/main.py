from fastapi import FastAPI, Request
from fastapi.exception_handlers import (
    http_exception_handler as default_http_exception_handler,
)
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1.restaurants import router as restaurants_router
from app.api.views import router as views_router
from app.core.config import settings
from app.core.templating import BASE_DIR, templates

app = FastAPI(title=settings.APP_NAME)

app.include_router(restaurants_router, prefix="/api/v1")
app.include_router(views_router)
app.mount("/static", StaticFiles(directory=str(BASE_DIR.parent / "static")), name="static")


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """La API responde JSON; las páginas HTML responden con una vista de error."""
    path = request.url.path
    if path.startswith("/api/") or path in ("/health", "/docs", "/openapi.json"):
        return await default_http_exception_handler(request, exc)
    return templates.TemplateResponse(
        request,
        "error.html",
        {"status_code": exc.status_code, "detail": exc.detail},
        status_code=exc.status_code,
    )
