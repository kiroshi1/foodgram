from django.contrib import admin

from foodgram_app import models

from .models import CustomUser


class RecipesAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'favorites_count')
    list_filter = ('name', 'author', 'tags')

    def favorites_count(self, obj):
        return models.Favorite.objects.filter(recipe=obj).count()


class UserAdmin(admin.ModelAdmin):
    list_filter = ('first_name', 'email')


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name', )


admin.site.register(CustomUser, UserAdmin)
admin.site.register(models.Tag)
admin.site.register(models.Ingredient, IngredientAdmin)
admin.site.register(models.RecipeIngredient)
admin.site.register(models.Recipe, RecipesAdmin)
admin.site.register(models.Follow)
admin.site.register(models.Favorite)
admin.site.register(models.Purchase)
