from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


# @pytest.fixture
# def database_path(tmp_path: Path) -> Path:
#     return tmp_path / "test-cars.db"
#
#
# @pytest.fixture
# def client(database_path: Path) -> Iterator[TestClient]:
#     # The context manager runs FastAPI's lifespan, including table creation.
#     # Each test gets a fresh on-disk database, never the real cars.db.
#     with TestClient(create_app(database_path)) as test_client:
#         yield test_client
#
#
# @pytest.fixture
# def car_payload() -> dict:
#     return {"make": "Toyota", "model": "Corolla", "year": 2024, "color": "Silver"}



import os
from typing import Iterator

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app import database

@pytest.fixture
def database_path() -> dict:
    """Use a dedicated MySQL database for integration tests."""
    config = {
        "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER", "root"),
        "password": os.environ.get("MYSQL_PASSWORD",""),
        "database": "test_db",
}


    if config["database"] != "test_db":
        raise RuntimeError("Refusing to use a non-test database")

    return config


@pytest.fixture
def client(database_path: dict) -> Iterator[TestClient]:
    # Remove data left by previous runs.
    database.initialize(database_path)
    with database.connect(database_path) as connection:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM cars")


    try:
        with TestClient(create_app(database_path)) as test_client:
            yield test_client #将yield 后面的对象传回用作参数
    finally:
        # Clean up data created by this test.
        with database.connect(database_path) as connection:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM cars")


@pytest.fixture
def car_payload() -> dict:
    return {
        "make": "Toyota",
        "model": "Corolla",
        "year": 2024,
        "color": "Silver",
    }
