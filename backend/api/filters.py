import django_filters

from foodgram_app.models import Recipe


class RecipeFilter(django_filters.filterset.FilterSet):
    tags = django_filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = django_filters.NumberFilter(method='filter_favorite')
    is_in_shopping_cart = django_filters.NumberFilter(
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
