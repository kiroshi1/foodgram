from foodgram_app.models import (Favorite, Follow, Ingredient, Purchase,
                                 Recipe, RecipeIngredient, Tag)
from rest_framework import serializers
from users.models import CustomUser


class Base64ImageField(serializers.ImageField):

    def to_internal_value(self, data):
        import base64
        import uuid

        import six
        from django.core.files.base import ContentFile

        if isinstance(data, six.string_types):
            if 'data:' in data and ';base64,' in data:
                header, data = data.split(';base64,')

            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail('invalid_image')

            file_name = str(uuid.uuid4())[:12]
            file_extension = self.get_file_extension(file_name, decoded_file)

            complete_file_name = "%s.%s" % (file_name, file_extension, )

            data = ContentFile(decoded_file, name=complete_file_name)

        return super(Base64ImageField, self).to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):
        import imghdr

        extension = imghdr.what(file_name, decoded_file)
        extension = "jpg" if extension == "jpeg" else extension

        return extension


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
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data, author=author)
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                ingredient=ingredient['id'],
                amount=ingredient['amount'],
                recipe=recipe)
        for tag in tags:
            recipe.tags.add(tag)
        return recipe

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags')
        instance.tags.set(tags_data)
        RecipeIngredient.objects.filter(recipe=instance).all().delete()
        ingredients = validated_data.pop('ingredients')
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                ingredient=ingredient['id'],
                amount=ingredient['amount'],
                recipe=instance)
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        instance.save()
        return instance

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
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    recipes = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='author.recipes.count')

    class Meta:
        model = Follow
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed', 'recipes',
            'recipes_count')

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
