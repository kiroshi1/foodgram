from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=200, unique=True, blank=False, verbose_name='Name')
    color = models.CharField(
        max_length=150, unique=True, blank=False,  verbose_name='Color')
    slug = models.SlugField(
        max_length=50, unique=True, blank=False, verbose_name='Slug')

    def __str__(self):
        return f'{self.name}'


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200, verbose_name='Name', blank=False)
    measurement_unit = models.CharField(
        max_length=10, verbose_name='measurement_unit', blank=False)

    def __str__(self):
        return f'{self.name}'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        blank=False)
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient'
    )
    tags = models.ManyToManyField(
        Tag,
        blank=False,
        related_name='recipes')
    image = models.ImageField(blank=False)
    name = models.CharField(max_length=200, blank=False, verbose_name='Name')
    text = models.TextField(max_length=256, blank=False, verbose_name='Text')
    cooking_time = models.IntegerField(
        blank=False, verbose_name='Cooking time')
    pub_date = models.DateTimeField(
        'Дата добавления',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'

    def __str__(self):
        return f'{self.name}'


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients_amounts'
    )
    amount = models.IntegerField(
        validators=[MinValueValidator(1)]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('ingredient', 'recipe'),
                name='unique_recipe_ingredient'
            )
        ]


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='follower')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='following')


class Favorite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='favorites')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='favored_by')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=('user', 'recipe'),
                                    name='unique_favorite_list')]


class Purchase(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='purchases')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='purchased_by')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=('user', 'recipe'),
                                    name='unique_purchase_list')]
