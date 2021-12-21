from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Recipe(models.Model):
    INGREDIENTS_CHOICES = (
        ('', ''),
    )
    TAGS_CHOICES = (
        ('', ''),
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes')
    ingredients = models.CharField(
        max_length=256,
        choices=INGREDIENTS_CHOICES,
        verbose_name='Ingredients')
    tags = models.CharField(max_length=256, verbose_name='Tags')
    image = models.ImageField(verbose_name='Image')
    name = models.CharField(max_length=200, verbose_name='Name')
    text = models.TextField(max_length=256, verbose_name='Text')
    cooking_time = models.IntegerField(verbose_name='Cooking time')

    class Meta:
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'

class Tag(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name='Name')
    color = models.CharField(unique=True),
    slug = models.SlugField(max_length=50, unique=True, verbose_name='Slug')