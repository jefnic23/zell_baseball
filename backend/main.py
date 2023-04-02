from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.database import db
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

    # app.mount('/', StaticFiles(directory='build/'), name='static')

    # @app.on_event('startup')
    # async def startup():
    #     await db.get_session()

    # @app.on_event('shutdown')
    # async def shutdown():
    #     await db.close()

    # @app.get('/')
    # def index():
    #     return app.send_static_file('index.html')
    
    return app


app = create_app()
