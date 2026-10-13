
import os

import pytest
from app import database
from app.schemas import CarInput


@pytest.fixture
def mysql_database_path():
 """读取 MySQL 数据库连接配置。"""
 return {
 "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
 "port": int(os.getenv("MYSQL_PORT", "3306")),
 "user": os.getenv("MYSQL_USER", "root"),
 "password": os.getenv("MYSQL_PASSWORD", ""),
 "database": os.getenv("MYSQL_DATABASE", "test_db"),
 }

def test_insert_one_car(mysql_database_path):
    config = mysql_database_path

    database.initialize(config)

    saved = database.create_car(
        config,
        CarInput(
            make="Toyota",
            model="Yaris",
            year=2020,
            color="Blue",
        ),
    )
    saved2 = database.create_car(
        config,
        CarInput(
            make="BMW",
            model="BMWX8",
            year=2022,
            color="red",
        ),
    )
    database.delete_car(config, saved.id)
    assert database.get_car(config, saved.id) is None
    cars =database.list_cars(config)
    assert any(saved2.id==car.id for car in cars)