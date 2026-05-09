from fastapi.middleware.cors import CORSMiddleware


def configure_middlewares(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5175",
            "http://localhost:5176",
            "http://127.0.0.1:5175",
            "http://127.0.0.1:5176",
            "http://localhost:8001",
            "http://127.0.0.1:8001",
            "*"
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )
