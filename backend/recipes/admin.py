from django.contrib import admin

from .models import (
    Favorite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    ShoppingCart,
    Tag,
)


class RecipeIngredientInline(admin.TabularInline):
    model = IngredientInRecipe
    min_num = 1
    extra = 0


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientInline,)
    list_display = ('name', 'author', 'pub_date', 'favorite_count')
    list_filter = ('name', 'author')
    search_fields = ('name',)

    def favorite_count(self, obj):
        return obj.FavoriteRecipe.count()

    favorite_count.short_description = 'В избранном'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
