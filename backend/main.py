from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.routers import games


def create_app():
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(games.router)

    app.mount('/', StaticFiles(directory='frontend/src/'), name='static')

    @app.get('/')
    def index():
        return app.send_static_file('app.html')
    
    return app


app = create_app()
