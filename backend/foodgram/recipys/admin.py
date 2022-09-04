from django.contrib import admin

from .models import (Basket, Favorite, Ingredient, IngredientsForRecipy,
                     Recipy, Tag)


class RecipyAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    list_filter = ('author', 'name', 'tags')
    # TODO favorited =


class IngredientsAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)


admin.site.register(Recipy, RecipyAdmin)
admin.site.register(Ingredient, IngredientsAdmin)
admin.site.register(IngredientsForRecipy)
admin.site.register(Tag)
admin.site.register(Favorite)
admin.site.register(Basket)
