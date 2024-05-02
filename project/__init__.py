from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from project.config import settings


def create_app() -> FastAPI:
    app = FastAPI()

    from project.bot import bot_router
    app.include_router(bot_router, tags=['bot'])

    from project.ws import ws_router
    app.include_router(ws_router, tags=['ws'])

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.mount('/static', StaticFiles(directory="static"), name="static")

    return app
