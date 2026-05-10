from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from app import home

def create_app():
    app = FastAPI()

    # Montar estáticos
    app.mount("/static", StaticFiles(directory="static"), name="static")

    # Rutas
    app.include_router(home.router)

    # Plantillas
    Jinja2Templates(directory="templates")

    return app
