import csv
from recipys.models import Ingredient


with open('ingredients.csv', newline='') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        Ingredient.objects.create(
            name=row[0],
            measurement_unit=row[1],
        )
