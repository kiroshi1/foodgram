from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (APIDownload, APIFavorite, APIFollow, APIFollowList,
                    APIShopping, IngredientViewSet, RecipeViewSet, TagViewSet)

router = DefaultRouter()
router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredients', IngredientViewSet, basename='ingredients')


urlpatterns = [
    path(r'recipes/download_shopping_cart/', APIDownload.as_view(), name='download_shopping_cart'),
    path('', include(router.urls)),
    path(r'users/<int:pk>/subscribe/', APIFollow.as_view(), name='subscribe'),
    path(r'recipes/<int:pk>/favorite/', APIFavorite.as_view(), name='favorite'),
    path(r'recipes/<int:pk>/shopping_cart/', APIShopping.as_view(), name='shopping_cart'),
    path('users/subscriptions/', APIFollowList.as_view(), name='follow'),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
