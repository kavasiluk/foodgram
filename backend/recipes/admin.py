from django.contrib import admin

from recipes.models import Ingredient, Tag, Recipe, Amount

admin.site.register(Ingredient)
admin.site.register(Tag)
admin.site.register(Amount)

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'cooking_time')
    search_fields = ('name', 'author', 'tags')
    list_filter = ('name', 'author', 'tags')
