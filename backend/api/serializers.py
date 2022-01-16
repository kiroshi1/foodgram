from rest_framework import serializers
# from rest_framework.validators import UniqueTogetherValidator

from foodgram_app.models import (Favorite, Follow, Ingredient, Purchase,
                                 Recipe, RecipeIngredient, Tag)
from users.models import CustomUser

from .fields import Base64ImageField


class CustomUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed')
        ordering = ['-id']

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Follow.objects.filter(user=request.user, author=obj).exists()


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Ingredient


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


def ingredients_create(products, recipe):
    for product in products:
        RecipeIngredient.objects.create(
            ingredient=product['id'],
            amount=product['amount'],
            recipe=recipe)


class RecipeReadSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(read_only=True, many=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time')
        model = Recipe

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Purchase.objects.filter(user=request.user, recipe=obj).exists()

    def get_ingredients(self, obj):
        queryset = RecipeIngredient.objects.filter(recipe=obj)
        return RecipeIngredientsSerializer(queryset, many=True).data


class RecipeWriteSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all())
    ingredients = RecipeIngredientsSerializer(many=True)
    image = Base64ImageField(max_length=None, use_url=True)

    class Meta:
        fields = (
            'ingredients', 'tags', 'image', 'name', 'text', 'cooking_time')
        model = Recipe

    def create(self, validated_data):
        author = self.context.get('request').user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data, author=author)
        ingredients_create(ingredients, recipe)
        for tag in tags:
            recipe.tags.add(tag)
        return recipe

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags')
        instance.tags.set(tags_data)
        RecipeIngredient.objects.filter(recipe=instance).all().delete()
        ingredients = validated_data.pop('ingredients')
        ingredients_create(ingredients, instance)
        return super(
            RecipeWriteSerializer, self).update(instance, validated_data)

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeReadSerializer(instance, context=context).data


class FavoriteSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(read_only=True, source='recipe.image')
    name = serializers.CharField(read_only=True, source='recipe.name')
    id = serializers.IntegerField(read_only=True, source='recipe.id')
    cooking_time = serializers.IntegerField(
        read_only=True, source='recipe.cooking_time')

    class Meta:
        fields = (
            'id', 'name', 'image', 'cooking_time')
        model = Favorite


class ShortRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'cooking_time', 'image')
        model = Recipe


class ShoppingCartSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(read_only=True, source='recipe.image')
    name = serializers.CharField(read_only=True, source='recipe.name')
    id = serializers.IntegerField(read_only=True, source='recipe.id')
    cooking_time = serializers.IntegerField(
        read_only=True, source='recipe.cooking_time')

    class Meta:
        fields = (
            'id', 'name', 'image', 'cooking_time')
        model = Purchase


class FollowSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(default='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    recipes = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='author.recipes.count')

    class Meta:
        model = Follow
        fields = (
            'user', 'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed', 'recipes',
            'recipes_count')
        # validators = [
        #     UniqueTogetherValidator(
        #         queryset=Follow.objects.all(),
        #         fields=['field1', 'field2'],
        #         message='You\'re already following this user'
        #     )
        # ]

        # Я вроде всё исправил кроме валидации, пока не могу
        # разобраться, по логике в fields должен быть
        # автор и юзер, но я не объявляю эти поля,
        # поэтому застрял немного, я завтра смогу
        # только вечером увидеть ревью
        # поэтому отправил без этого, чтобы если есть ошибки,
        # Вы на них указали, а я исправлю уже всё вместе на втором

        # Так же ребята в слаке, подсказали что вроде во фронте нет кнопки
        # подписаться на себя и что достаточно ограничения в модели follow
        # не знаю в общем, как тут выкрутиться

    def get_recipes(self, obj):
        request = self.context.get('request')
        context = {'request': request}
        if request and request.user.is_authenticated:
            recipes_limit = request.query_params.get('recipes_limit')
            if recipes_limit is not None:
                queryset = obj.author.recipes.all()[:int(recipes_limit)]
            else:
                queryset = Recipe.objects.filter(author=obj.author)
        else:
            queryset = Recipe.objects.filter(author=obj.author)
        return ShortRecipeSerializer(queryset, many=True, context=context).data

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=request.user, author=obj.author).exists()

    # def validate(self, data):
