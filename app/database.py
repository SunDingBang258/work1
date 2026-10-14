"""SQLite CRUD using only the Python standard library. No ORM."""

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from contextlib import contextmanager
from typing import Any, Iterator
import pymysql
from pymysql.cursors import DictCursor

from app.schemas import Car, CarInput


# @contextmanager
# def connect(database_path: Path) -> Iterator[sqlite3.Connection]:
#     # A fresh connection per operation keeps connections on their owning thread.
#     connection = sqlite3.connect(database_path, timeout=10)
#     connection.row_factory = sqlite3.Row
#     try:
#         # Commit on success, roll back on failure.
#         with connection:
#             yield connection
#     finally:
#         # sqlite3's connection context manager does NOT close the connection.
#         connection.close()
#
# def get_connection(config: dict[str, Any]):
#     """Create a new MySQL connection."""
#     return pymysql.connect(
#         host=config["host"],
#         port=int(config.get("port", 3306)),
#         user=config["user"],
#         password=config["password"],
#         database=config["database"],
#         charset="utf8mb4",
#         cursorclass=DictCursor,
#         autocommit=False,
#         connect_timeout=10,
#     )
# @contextmanager
# def connect(config: dict[str, Any]) -> Iterator[Any]:
#     """Commit on success, roll back on failure, and close the connection."""
#     connection = get_connection(config)
#     try:
#         yield connection
#         connection.commit()
#     except Exception:
#         connection.rollback()
#         raise
#     finally:
#         connection.close()
#
# def initialize(config: dict[str, Any]) -> None:
#     """Initialize the MySQL database."""
#     with connect(config) as connection:
#         with connection.cursor() as cursor:
#             cursor.execute("""
#                 CREATE TABLE IF NOT EXISTS cars (
#                     id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
#                     make VARCHAR(100) NOT NULL,
#                     model VARCHAR(100) NOT NULL,
#                     year INT NOT NULL,
#                     color VARCHAR(50) NOT NULL
#                 ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
#             """)

#################
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

import pymysql
from pymysql.constants import CLIENT
from pymysql.cursors import DictCursor


def get_connection(config: dict[str, Any] | None = None):
    """Create a new MySQL connection."""
    if config is None:
        config = {
            "host": os.environ.get("MYSQL_HOST", "db"),
            "port": int(os.environ.get("MYSQL_PORT", "3306")),
            "user": os.environ["MYSQL_USER"],
            "password": os.environ["MYSQL_PASSWORD"],
            "database": os.environ["MYSQL_DATABASE"],
        }

    return pymysql.connect(
        host=config.get("host", "db"),
        port=int(config.get("port", 3306)),
        user=config["user"],
        password=config["password"],
        database=config["database"],
        charset="utf8mb4",
        cursorclass=DictCursor,
        autocommit=False,
        client_flag=CLIENT.FOUND_ROWS,
        connect_timeout=10,
    )


@contextmanager
def connect(config: dict[str, Any] | None = None) -> Iterator[Any]:
    """Commit on success, roll back on failure, and close the connection."""
    connection = get_connection(config)
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def initialize(config: dict[str, Any] | Path | None = None) -> None:
    """Initialize the MySQL database."""
    # Support the existing initialize(_database_path) calling convention.
    if isinstance(config, Path):
        config = None

    with connect(config) as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cars (
                    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                    make VARCHAR(60) NOT NULL,
                    model VARCHAR(60) NOT NULL,
                    year INT NOT NULL,
                    color VARCHAR(40) NOT NULL DEFAULT '',
                    CONSTRAINT valid_make
                        CHECK (CHAR_LENGTH(TRIM(make)) > 0),
                    CONSTRAINT valid_model
                        CHECK (CHAR_LENGTH(TRIM(model)) > 0),
                    CONSTRAINT valid_year
                        CHECK (year BETWEEN 1886 AND 2100)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)




def list_cars(config: dict[str, Any]) -> list[Car]:
    with connect(config) as connection:
     with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM cars ORDER BY id DESC")
        rows = cursor.fetchall()
    return [Car(**row) for row in rows]

def get_car(config: dict[str, Any], car_id: int) -> Car | None:
    with connect(config) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
            "SELECT * FROM cars WHERE id = %s",
            (car_id,),
            )
            row = cursor.fetchone()
    return Car(**row) if row is not None else None

def create_car(config: dict[str, Any], car: CarInput) -> Car:
    with connect(config) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
            """
            INSERT INTO cars (make, model, year, color)
            VALUES (%s, %s, %s, %s)
            """,
            (car.make, car.model, car.year, car.color),
            )
            car_id = cursor.lastrowid


    return get_car(config, car_id)

def update_car(
    config: dict[str, Any],
    car_id: int,
    car: CarInput,
    ) -> Car | None:
    with connect(config) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
            """
            UPDATE cars
            SET make = %s, model = %s, year = %s, color = %s
            WHERE id = %s
            """,
            (car.make, car.model, car.year, car.color, car_id),
            )


    return get_car(config, car_id)


def delete_car(config: dict[str, Any], car_id: int) -> bool:
    with connect(config) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
            "DELETE FROM cars WHERE id = %s",
            (car_id,),
            )
    return cursor.rowcount == 1


#
#
# def list_cars(database_path: Path) -> list[Car]:
#     with connect(database_path) as connection:
#         rows = connection.execute("SELECT * FROM cars ORDER BY id DESC").fetchall()
#         return [Car(**dict(row)) for row in rows]
#
#
# def get_car(database_path: Path, car_id: int) -> Car | None:
#     with connect(database_path) as connection:
#         row = connection.execute("SELECT * FROM cars WHERE id = ?", (car_id,)).fetchone()
#         return Car(**dict(row)) if row is not None else None
#
#
# def create_car(database_path: Path, car: CarInput) -> Car:
#     with connect(database_path) as connection:
#         cursor = connection.execute(
#             "INSERT INTO cars (make, model, year, color) VALUES (?, ?, ?, ?)",
#             (car.make, car.model, car.year, car.color),
#         )
#         return Car(id=cursor.lastrowid, **car.model_dump())
#
#
# def update_car(database_path: Path, car_id: int, car: CarInput) -> Car | None:
#     with connect(database_path) as connection:
#         cursor = connection.execute(
#             "UPDATE cars SET make = ?, model = ?, year = ?, color = ? WHERE id = ?",
#             (car.make, car.model, car.year, car.color, car_id),
#         )
#         if cursor.rowcount == 0:
#             return None
#         return Car(id=car_id, **car.model_dump())
#
#
# def delete_car(database_path: Path, car_id: int) -> bool:
#     with connect(database_path) as connection:
#         cursor = connection.execute("DELETE FROM cars WHERE id = ?", (car_id,))
#         return cursor.rowcount == 1
