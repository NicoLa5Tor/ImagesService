from pathlib import Path
from urllib.parse import parse_qs

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request

from app.api.routes import api_router
from app.core.config import get_settings


class DownloadStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope):  # type: ignore[override]
        response = await super().get_response(path, scope)
        if response.status_code != 200 or not path.lower().endswith(".apk"):
            return response

        query_params = parse_qs(scope.get("query_string", b"").decode("utf-8"))
        if query_params.get("raw") == ["1"]:
            filename = Path(path).name
            response.headers.setdefault("content-disposition", f'attachment; filename="{filename}"')
            return response

        request = Request(scope)
        file_url = str(request.url.include_query_params(raw=1))
        filename = Path(path).name.replace('"', "")
        html = f"""<!doctype html>
<html lang="es">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <title>Descargando {filename}</title>
    <style>
      :root {{
        color-scheme: only light;
      }}
      body {{
        margin: 0;
        min-height: 100vh;
        display: grid;
        place-items: center;
        font-family: "Playfair Display", "Georgia", serif;
        background: radial-gradient(circle at top, #f9efe4 0%, #f3d9c5 45%, #e7c4a8 100%);
        color: #3a2a1d;
      }}
      .card {{
        width: min(720px, 92vw);
        padding: 48px 56px;
        border-radius: 28px;
        background: rgba(255, 255, 255, 0.82);
        box-shadow: 0 30px 60px rgba(58, 42, 29, 0.18);
        text-align: center;
      }}
      h1 {{
        margin: 0 0 24px;
        font-size: clamp(28px, 4.5vw, 48px);
        letter-spacing: 0.02em;
      }}
      .name {{
        display: inline-block;
        font-weight: 700;
        word-break: break-all;
      }}
      .progress {{
        margin-top: 32px;
        width: 100%;
        height: 14px;
        background: #f0e2d4;
        border-radius: 999px;
        overflow: hidden;
      }}
      .bar {{
        height: 100%;
        width: 0%;
        background: linear-gradient(90deg, #b05b3b 0%, #d98b5f 50%, #b05b3b 100%);
        transition: width 0.2s ease;
      }}
      .status {{
        margin-top: 16px;
        font-family: "Work Sans", "Helvetica", sans-serif;
        font-size: 15px;
        letter-spacing: 0.08em;
        text-transform: uppercase;
      }}
      .hint {{
        margin-top: 10px;
        font-family: "Work Sans", "Helvetica", sans-serif;
        font-size: 13px;
        color: #6b4a34;
      }}
    </style>
  </head>
  <body>
    <main class="card">
      <h1>Descargando</h1>
      <div class="name">{filename}</div>
      <div class="progress" aria-hidden="true">
        <div class="bar" id="bar"></div>
      </div>
      <div class="status" id="status">Iniciando...</div>
      <div class="hint">Por favor no cierres esta pestaña.</div>
    </main>
    <script>
      const fileUrl = {file_url!r};
      const filename = {filename!r};
      const bar = document.getElementById("bar");
      const status = document.getElementById("status");

      function formatBytes(bytes) {{
        const mb = bytes / (1024 * 1024);
        return `${{mb.toFixed(1)}} MB`;
      }}

      async function startDownload() {{
        try {{
          const response = await fetch(fileUrl);
          if (!response.ok || !response.body) {{
            throw new Error("No se pudo descargar el archivo.");
          }}
          const total = Number(response.headers.get("content-length")) || 0;
          const reader = response.body.getReader();
          let received = 0;
          const chunks = [];

          while (true) {{
            const {{ done, value }} = await reader.read();
            if (done) break;
            received += value.length;
            chunks.push(value);
            if (total > 0) {{
              const percent = Math.round((received / total) * 100);
              bar.style.width = `${{percent}}%`;
              status.textContent = `${{percent}}%`;
            }} else {{
              status.textContent = formatBytes(received);
            }}
          }}

          bar.style.width = "100%";
          status.textContent = "Completado";
          const blob = new Blob(chunks);
          const blobUrl = URL.createObjectURL(blob);
          const link = document.createElement("a");
          link.href = blobUrl;
          link.download = filename;
          document.body.appendChild(link);
          link.click();
          link.remove();
          URL.revokeObjectURL(blobUrl);
        }} catch (error) {{
          status.textContent = "Error al descargar.";
        }}
      }}

      startDownload();
    </script>
  </body>
</html>
"""
        return HTMLResponse(content=html)


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
