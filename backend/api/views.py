from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from foodgram_app.models import Recipe, Tag, Ingredient, Follow, Favorite, Purchase, RecipeIngredient
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import CustomUser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .filters import RecipeFilter
from django.db.models import Sum
# from .permissions import RecipesPermission

from .serializers import (
    TagSerializer, RecipeReadSerializer, FavoriteSerializer,
    IngredientSerializer, FollowSerializer, RecipeWriteSerializer, ShoppingCartSerializer)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ('author', )
    search_fields = ('name', )
    filter_class = RecipeFilter
    permission_classes = [AllowAny, ]

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeWriteSerializer

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('^name',)
    pagination_class = None

class APIFollow(APIView):
    def post(self, request, pk=None):
        user = self.request.user
        author = get_object_or_404(CustomUser, id=self.kwargs['pk'])
        if user == author:
            return Response('You can not follow yourself', status=status.HTTP_400_BAD_REQUEST)
        if Follow.objects.filter(author=author, user=user).exists():
            return Response('You already subscribed', status=status.HTTP_400_BAD_REQUEST)
        serializer = FollowSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        user = self.request.user
        author = get_object_or_404(CustomUser, id=self.kwargs['pk'])
        follow = get_object_or_404(Follow, user=user, author=author)
        if Follow.objects.filter(user=user, author=author).exists():
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)


class APIFollowList(ListAPIView):
    serializer_class = FollowSerializer

    def get_queryset(self):
        user = self.request.user
        followers = user.follower.all()
        return followers


class APIFavorite(APIView):
    def post(self, request, pk=None):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=self.kwargs['pk'])
        serializer = FavoriteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=self.kwargs['pk'])
        favorite = get_object_or_404(Favorite, user=user, recipe=recipe)
        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)


class APIShopping(APIView):
    def post(self, request, pk=None):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=self.kwargs['pk'])
        serializer = ShoppingCartSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=self.kwargs['pk'])
        purchase = get_object_or_404(Purchase, user=user, recipe=recipe)
        if Purchase.objects.filter(user=user, recipe=recipe).exists():
            purchase.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class APIDownload(APIView):
    def get(self, request):
        user = self.request.user
        purchases = user.purchases.all()
        lines = []
        for purchase in purchases:
            recipe = purchase.recipe
            ingredients = RecipeIngredient.objects.filter(recipe=recipe).values('ingredient__name', 'ingredient__measurement_unit').annotate(quantity=Sum('amount'))
            for i in ingredients:
                lines.append(f'{i["ingredient__name"]} ({i["ingredient__measurement_unit"]}) — {i["quantity"]}')
        text = '\n'.join(lines)
        response = HttpResponse(text, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="Список Покупок.txt"'
        return response




