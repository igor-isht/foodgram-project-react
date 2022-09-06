from django.contrib import admin

from .models import (Basket, Favorite, Ingredient, IngredientsForRecipy,
                     Recipy, Tag)


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    list_filter = ('name',)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)


class IngredientsForRecipyAdmin(admin.StackedInline):
    model = IngredientsForRecipy
    extra = 0


class RecipyAdmin(admin.ModelAdmin):
    inlines = (IngredientsForRecipyAdmin, )
    list_display = (
        'author',
        'name',
        'image',
        'text',
        'cooking_time',
    )
    search_fields = ('author', 'name', 'tags')
    list_filter = ('author', 'name', 'tags')


class BasketAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user',)


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user',)


admin.site.register(Recipy, RecipyAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Basket, BasketAdmin)
