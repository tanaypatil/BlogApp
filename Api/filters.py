import django_filters
from django.db.models import Q

from Api.models import Blog, BLOG_CATEGORIES, Tag


class BlogFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_search', label='Search')

    category = django_filters.ChoiceFilter(
        choices=BLOG_CATEGORIES,
        label='Category'
    )

    tags = django_filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags',
        label='Tags'
    )

    tag_names = django_filters.CharFilter(
        method='filter_by_tag_names',
        label='Tag Names (comma-separated)'
    )

    author = django_filters.CharFilter(
        field_name='author__username',
        lookup_expr='icontains',
        label='Author Username'
    )

    created_after = django_filters.DateTimeFilter(
        field_name='created',
        lookup_expr='gte',
        label='Created After'
    )

    created_before = django_filters.DateTimeFilter(
        field_name='created',
        lookup_expr='lte',
        label='Created Before'
    )

    has_tags = django_filters.BooleanFilter(
        method='filter_has_tags',
        label='Has Tags'
    )

    def filter_search(self, queryset, name, value):
        """
        Search in title, body, and author username
        """
        if value:
            return queryset.filter(
                Q(title__icontains=value) |
                Q(body__icontains=value) |
                Q(author__username__icontains=value)
            ).distinct()
        return queryset

    def filter_by_tag_names(self, queryset, name, value):
        """
        Filter by comma-separated tag names
        Example: ?tag_names=python,django,web
        """
        if value:
            tag_names = [name.strip() for name in value.split(',')]
            return queryset.filter(tags__name__in=tag_names).distinct()
        return queryset

    def filter_has_tags(self, queryset, name, value):
        """
        Filter blogs that have or don't have tags
        """
        if value:
            return queryset.filter(tags__isnull=False).distinct()
        else:
            return queryset.filter(tags__isnull=True)

    class Meta:
        model = Blog
        fields = {
            'title': ['icontains', 'exact'],
            'slug': ['exact', 'icontains'],
            'category': ['exact'],
            'created': ['gte', 'lte', 'exact'],
            'updated': ['gte', 'lte', 'exact'],
        }
