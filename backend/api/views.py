from rest_framework.response import Response
from rest_framework import serializers, viewsets, status
from users.models import CustomUser
from foodgram_app.models import Recipe, Tag, Ingredient, Follow
from .serializers import (
    CustomUserSerializer, TagSerializer, RecipeReadSerializer, FollowersRecipesSerializer,
    IngredientSerializer, FollowSerializer, UserWithRecipesSerializer)
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.decorators import action


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeReadSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None


class FollowViewSet(viewsets.ModelViewSet):
    serializer_class = UserWithRecipesSerializer

    # def perform_create(self, serializer):
    #

    def get_queryset(self):
        user = self.request.user
        queryset = CustomUser.objects.filter(following__user=user)
        return queryset













    # @action(detail=False, url_path='me')
    # def request_user_info(self, request):
    #     users = CustomUser.objects.all()[:2]
    #     serializer = self.get_serializer(users, many=True)
    #     return Response(serializer.data)