import pytest
from pydantic import ValidationError

from app.schemas import CarInput
def test_car():
 with pytest.raises(ValidationError):
     CarInput(
     make=" Mazda ",
     model=" ",
     year=2020,
     color=" Red ",
     )