from django_filters.rest_framework import FilterSet, filters
from rest_framework.filters import SearchFilter

from foodgram_app.models import Recipe


class IngredientFilter(SearchFilter):
    search_param = 'name'


class RecipeFilter(FilterSet):
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    author = filters.CharFilter(field_name='author__id')
    is_favorited = filters.NumberFilter(method='filter_favorite')
    is_in_shopping_cart = filters.NumberFilter(
        method='filter_shopping_cart')

    def filter_favorite(self, queryset, name, value):
        if value == 1:
            return queryset.filter(favored_by__user=self.request.user)
        elif value == 0:
            return queryset.filter(favored_by__user__isnull=True)
        return queryset

    def filter_shopping_cart(self, queryset, name, value):
        if value == 1:
            return queryset.filter(purchased_by__user=self.request.user)
        elif value == 0:
            return queryset.filter(purchased_by__user__isnull=True)
        return queryset

    class Meta:
        model = Recipe
        fields = ['tags', 'is_favorited', 'is_in_shopping_cart', ]
