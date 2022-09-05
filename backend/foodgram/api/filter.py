from rest_framework import filters

from recipys.models import Ingredient


class IngredientFilter(filters.SearchFilter):
    search_param = 'name'

