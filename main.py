from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import api_router
from app.core.config import get_settings


class DownloadStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope):  # type: ignore[override]
        response = await super().get_response(path, scope)
        if response.status_code == 200 and path.lower().endswith(".apk"):
            filename = Path(path).name
            response.headers.setdefault("content-disposition", f'attachment; filename="{filename}"')
        return response


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(title=settings.project_name, version=settings.api_version)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )

    app.mount("/static", DownloadStaticFiles(directory=settings.static_path), name="static")

    app.include_router(api_router)

    @app.get("/")
    async def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()


if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "main:app",
        host=settings.uvicorn_host,
        port=settings.uvicorn_port,
        reload=settings.uvicorn_reload,
        factory=False,
    )
