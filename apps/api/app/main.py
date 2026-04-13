import sys
from pathlib import Path

from fastapi import FastAPI

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.api.v1.api import api_router
from app.core.startup import configure_middlewares

app = FastAPI(title="REVISA Platform API", version="1.0.0")
configure_middlewares(app)
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)
