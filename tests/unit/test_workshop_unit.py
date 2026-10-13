from app.schemas import CarInput
def test_car_text_fields_are_trimmed():
 car = CarInput(
 make=" Mazda ",
 model=" MX-5 ",
 year=2020,
 color=" Red ",
 )
 assert car.make == "Mazda"
 assert car.model == "MX-5"
 assert car.color == "Red"
