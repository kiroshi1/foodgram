from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from foodgram_app.models import (Favorite, Follow, Ingredient, Purchase,
                                 Recipe, RecipeIngredient, Tag)
from rest_framework import filters, status, viewsets
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import CustomUser

from .filters import RecipeFilter
from .permissions import RecipesPermission
from .serializers import (FavoriteSerializer, FollowSerializer,
                          IngredientSerializer, RecipeReadSerializer,
                          RecipeWriteSerializer, ShoppingCartSerializer,
                          TagSerializer)


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
        if user == author:
            return Response(
                'You can not follow yourself',
                status=status.HTTP_400_BAD_REQUEST)
        if Follow.objects.filter(author=author, user=user).exists():
            return Response(
                'You already subscribed', status=status.HTTP_400_BAD_REQUEST)
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
        names = []
        quantity = []
        for purchase in purchases:
            recipe = purchase.recipe
            ingredients = RecipeIngredient.objects.filter(
                recipe=recipe).values(
                'ingredient__name', 'ingredient__measurement_unit').annotate(
                quantity=Sum('amount'))
            for i in ingredients:
                names.append(
                    f'{i["ingredient__name"]}'
                    f' ({i["ingredient__measurement_unit"]})')
                quantity.append(int(i['quantity']))
        products = []
        for i in range(len(names)):
            products.append([])
            products[i].append(names[i])
            products[i].append(quantity[i])
        dict = {}
        for i in products:
            if i[0] in dict:
                dict[i[0]] += i[1]
            else:
                dict[i[0]] = i[1]
        answer = []
        for key, value in dict.items():
            answer.append(f'{key} — {value}')
        text = '\n'.join(answer)
        response = HttpResponse(
            text, content_type='text/plain')
        response['Content-Disposition'] =\
            'attachment; filename="Список Покупок.txt"'
        return response
