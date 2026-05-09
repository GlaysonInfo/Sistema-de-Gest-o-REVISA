import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.api.v1.api import api_router
from app.core.startup import configure_middlewares

app = FastAPI(title="REVISA Platform API", version="1.0.0")
configure_middlewares(app)
app.include_router(api_router, prefix="/api/v1")


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def root():
    return """
    <!doctype html>
    <html lang="pt-BR">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>REVISA API</title>
        <style>
          :root {
            color-scheme: light;
            font-family: Inter, Segoe UI, Arial, sans-serif;
            color: #17201b;
            background: #f4f8f6;
          }
          body {
            margin: 0;
            min-height: 100vh;
            display: grid;
            place-items: center;
            padding: 24px;
          }
          main {
            width: min(720px, 100%);
            background: #ffffff;
            border: 1px solid #d8e2dc;
            border-radius: 8px;
            padding: 32px;
            box-shadow: 0 16px 45px rgba(23, 32, 27, 0.08);
          }
          h1 {
            margin: 0 0 8px;
            font-size: clamp(28px, 5vw, 44px);
            letter-spacing: 0;
          }
          p {
            margin: 0 0 24px;
            color: #53615a;
            line-height: 1.6;
          }
          nav {
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
          }
          a {
            color: #ffffff;
            background: #2d7b8f;
            border-radius: 6px;
            padding: 12px 16px;
            text-decoration: none;
            font-weight: 700;
          }
          a.secondary {
            color: #2d7b8f;
            background: #e7f2f5;
          }
        </style>
      </head>
      <body>
        <main>
          <h1>REVISA API</h1>
          <p>
            Servico online. Use a documentacao interativa para testar endpoints
            ou a rota de saude para validar o deploy no Render.
          </p>
          <nav aria-label="Links da API">
            <a href="/docs">Abrir documentacao</a>
            <a class="secondary" href="/health">Verificar saude</a>
            <a class="secondary" href="/openapi.json">OpenAPI JSON</a>
          </nav>
        </main>
      </body>
    </html>
    """


@app.get("/health")
def health():
    return {"status": "ok", "service": "REVISA Platform API"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)
