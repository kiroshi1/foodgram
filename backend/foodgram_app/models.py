from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=200, unique=True, verbose_name='Name')
    color = models.CharField(
        max_length=150, unique=True, verbose_name='Color')
    slug = models.SlugField(
        max_length=50, unique=True, verbose_name='Slug')

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __str__(self):
        return f'{self.name}'


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200, verbose_name='Name')
    measurement_unit = models.CharField(
        max_length=10, verbose_name='Measurement_unit')

    class Meta:
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'

    def __str__(self):
        return f'{self.name}'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Author')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='RecipeIngredients'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Tags')
    image = models.ImageField(verbose_name='Image')
    name = models.CharField(max_length=200, verbose_name='Name')
    text = models.TextField(max_length=256, verbose_name='Text')
    cooking_time = models.IntegerField(verbose_name='Cooking time')
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True, verbose_name='Pub_date'
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'

    def __str__(self):
        return f'{self.name}'


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='RecipeIngredient')
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients_amounts',
        verbose_name='RecipeForIngredient'
    )
    amount = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Amount'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('ingredient', 'recipe'),
                name='unique_recipe_ingredient'
            )
        ]
        verbose_name = 'RecipeIngredient'
        verbose_name_plural = 'RecipeIngredients'


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Follower')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Following')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=('user', 'author'),
                                    name='unique_follow')]
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='FavoriteUser')
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favored_by',
        verbose_name='FavoriteRecipe')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=('user', 'recipe'),
                                    name='unique_favorite_list')]
        verbose_name = 'Favorite'
        verbose_name_plural = 'Favorites'


class Purchase(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='purchases',
        verbose_name='Purchaser')
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='purchased_by',
        verbose_name='RecipePurchase')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=('user', 'recipe'),
                                    name='unique_purchase_list')]
        verbose_name = 'Purchase'
        verbose_name_plural = 'Purchases'


