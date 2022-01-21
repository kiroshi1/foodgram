from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from foodgram_app.models import Recipe, RecipeIngredient


def create(request, serializer, pk):
    user = request.user
    recipe = get_object_or_404(Recipe, id=pk)
    serializer = serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save(user=user, recipe=recipe)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def delete(request, model_name, pk):
    user = request.user
    recipe = get_object_or_404(Recipe, id=pk)
    model = get_object_or_404(model_name, user=user, recipe=recipe)
    if model:
        model.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(status=status.HTTP_404_NOT_FOUND)


def ingredients_create(products, recipe):
    for product in products:
        RecipeIngredient.objects.create(
            ingredient=product['id'],
            amount=product['amount'],
            recipe=recipe)