from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from yukinoise_users.presentation.auth import setup_auth


def create_app() -> FastAPI:
    app = FastAPI(
        title="YukiNoise Users API",
        description="User management microservice for YukiNoise",
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    setup_auth(app)

    @app.get("/health")
    async def health_check() -> dict:
        return {"status": "healthy"}

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
