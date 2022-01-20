from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from foodgram_app.models import (Favorite, Follow, Ingredient, Purchase,
                                 Recipe, RecipeIngredient, Tag)
from users.models import CustomUser
from .filters import RecipeFilter
from .permissions import RecipesPermission
from .serializers import (FavoriteSerializer, FollowListSerializer,
                          IngredientSerializer, RecipeReadSerializer,
                          RecipeWriteSerializer, ShoppingCartSerializer,
                          TagSerializer, FollowWriteSerializer)
from .utils import create, delete


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ('author', )
    search_fields = ('name', )
    filter_class = RecipeFilter
    permission_classes = [RecipesPermission, ]

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
        # user = get_object_or_404(User, username=self.request.data['following'])
        data = {'user': user.id, 'author': author.id}
        serializer = FollowWriteSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user, author=author)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk=None):
        user = self.request.user
        author = get_object_or_404(CustomUser, id=self.kwargs['pk'])
        follow = get_object_or_404(Follow, user=user, author=author)
        if Follow.objects.filter(user=user, author=author).exists():
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)


class APIFollowList(ListAPIView):
    serializer_class = FollowListSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = CustomUser.objects.filter(following__user=user)
        return queryset


class APIFavorite(APIView):
    def post(self, request, pk=None):
        return create(request, FavoriteSerializer, self.kwargs['pk'])

    def delete(self, request, pk=None):
        return delete(request, Favorite, self.kwargs['pk'])


class APIShopping(APIView):
    def post(self, request, pk=None):
        return create(request, ShoppingCartSerializer, self.kwargs['pk'])

    def delete(self, request, pk=None):
        return delete(request, Purchase, self.kwargs['pk'])


class APIDownload(APIView):
    def get(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__purchased_by__user=request.user).values(
                'ingredient__name',
                'ingredient__measurement_unit').annotate(
                quantity=Sum('amount'))
        ingredient_strings = []
        for elem in ingredients:
            ingredient_strings.append(
                f'{elem["ingredient__name"]} '
                f'({elem["ingredient__measurement_unit"]}) — '
                f'{elem["quantity"]}')
        text = '\n'.join(ingredient_strings)
        response = HttpResponse(
            text, content_type='text/plain')
        response['Content-Disposition'] =\
            'attachment; filename="Список Покупок.txt"'
        return response
