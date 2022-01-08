from users.models import CustomUser
from foodgram_app.models import Tag, Ingredient, Recipe, Follow
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField


class CustomUserSerializer(serializers.ModelSerializer):


    class Meta:
        model = CustomUser
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed')
        ordering = ['-id']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Ingredient


class RecipeReadSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(read_only=True, many=True)
    ingredients = IngredientSerializer(read_only=True, many=True)

    class Meta:
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time')
        model = Recipe

# class RecipeWriteSerializer(serializers.ModelSerializer):
#     author = CustomUserSerializer(read_only=True)
#     tags = TagSerializer(read_only=True, many=True)
#     ingredients = IngredientSerializer(read_only=True, many=True)
#
#     class Meta:
#         fields = (
#             'id', 'tags', 'author', 'ingredients', 'is_favorited',
#             'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time')
#         model = Recipe


class FollowersRecipesSerializer(serializers.ModelSerializer):

    class Meta:
        fields = (
            'id', 'name', 'image', 'cooking_time')
        model = Recipe


class UserWithRecipesSerializer(serializers.ModelSerializer):
    recipes = FollowersRecipesSerializer(read_only=True, many=True)
    recipes_count = serializers.IntegerField(
        source='recipes.count',
        read_only=True
    )

    class Meta:
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')
        model = CustomUser


class FollowSerializer(serializers.ModelSerializer):
    pass

