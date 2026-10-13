"""FastAPI routes: five JSON endpoints and plain HTML pages."""

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, HTTPException, Path as PathParam, Response, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app import database
from app.schemas import Car, CarInput

APP_DIR = Path(__file__).resolve().parent
CarId = Annotated[int, PathParam(gt=0)]


def create_app(database_config: dict | None = None) -> FastAPI:
    db_config = database_config or {
        "host": os.environ.get("MYSQL_HOST", "127.0.0.1"),
        "port": int(os.environ.get("MYSQL_PORT", "3306")),
        "user": os.environ.get("MYSQL_USER", "root"),
        "password": os.environ.get("MYSQL_PASSWORD", ""),
        "database": os.environ.get("MYSQL_DATABASE", "test_db"),
    }

    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        database.initialize(db_config)
        yield

    application = FastAPI(title="Cars API", version="1.0.0", lifespan=lifespan)
    application.mount("/static", StaticFiles(directory=APP_DIR / "static"), name="static")

    def require_car(car_id: int) -> Car:
        car = database.get_car(db_config, car_id)
        if car is None:
            raise HTTPException(status_code=404, detail="Car not found")
        return car

    # HTML files contain no templates. Their JavaScript calls the JSON API below.
    @application.get("/", include_in_schema=False)
    def index() -> FileResponse:
        return FileResponse(APP_DIR / "static" / "index.html")

    @application.get("/cars/new", include_in_schema=False)
    def new_car_page() -> FileResponse:
        return FileResponse(APP_DIR / "static" / "car-form.html")

    @application.get("/cars/{car_id}/edit", include_in_schema=False)
    def edit_car_page(car_id: CarId) -> FileResponse:
        require_car(car_id)
        return FileResponse(APP_DIR / "static" / "car-form.html")

    @application.get("/cars/{car_id}", include_in_schema=False)
    def car_page(car_id: CarId) -> FileResponse:
        require_car(car_id)
        return FileResponse(APP_DIR / "static" / "car-detail.html")

    @application.get("/api/cars", response_model=list[Car], tags=["cars"])
    def list_cars() -> list[Car]:
        return database.list_cars(db_config)

    @application.post(
        "/api/cars", response_model=Car, status_code=status.HTTP_201_CREATED, tags=["cars"]
    )
    def create_car(car: CarInput, response: Response) -> Car:
        created = database.create_car(db_config, car)
        response.headers["Location"] = f"/api/cars/{created.id}"
        return created

    @application.get("/api/cars/{car_id}", response_model=Car, tags=["cars"])
    def get_car(car_id: CarId) -> Car:
        return require_car(car_id)

    @application.put("/api/cars/{car_id}", response_model=Car, tags=["cars"])
    def update_car(car_id: CarId, car: CarInput) -> Car:
        updated = database.update_car(db_config, car_id, car)
        if updated is None:
            raise HTTPException(status_code=404, detail="Car not found")
        return updated

    @application.delete("/api/cars/{car_id}", status_code=204, tags=["cars"])
    def delete_car(car_id: CarId) -> Response:
        if not database.delete_car(db_config, car_id):
            raise HTTPException(status_code=404, detail="Car not found")
        return Response(status_code=204)

    return application


app = create_app()
