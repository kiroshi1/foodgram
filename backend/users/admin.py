from django.contrib import admin
from .models import CustomUser
from foodgram_app import models

admin.site.register(CustomUser)
admin.site.register(models.Tag)
admin.site.register(models.Ingredient)
admin.site.register(models.Recipe)
admin.site.register(models.Follow)
admin.site.register(models.Favorite)
admin.site.register(models.Purchase)