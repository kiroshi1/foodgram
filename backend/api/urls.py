from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TagViewSet, RecipeViewSet, IngredientViewSet, FollowViewSet

router = DefaultRouter()
router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('subscriptions', FollowViewSet, basename='subscriptions')


urlpatterns = [
    path('', include('djoser.urls')),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),

]