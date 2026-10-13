# from app import database
# from app.schemas import CarInput
# def test_saved_car_can_be_read_from_sqlite(database_path):
#  database.initialize(database_path)
#  saved = database.create_car(
#  database_path,
#  CarInput(make="Toyota", model="Yaris", year=2020, color="Blue"),
#  )
#  loaded = database.get_car(database_path, saved.id)
#  assert loaded is not None
#  assert loaded.id == saved.id
#  assert loaded.make == "Toyota"
#  assert loaded.year == 2020




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

def test_saved_car_can_be_read_from_mysql(mysql_database_path):
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

 loaded = database.get_car(config, saved.id)

 assert loaded is not None
 assert loaded.id == saved.id
 assert loaded.make == "Toyota"
 assert loaded.year == 2020