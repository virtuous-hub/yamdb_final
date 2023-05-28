from rest_framework import mixins, viewsets
from rest_framework import filters
from rest_framework.pagination import PageNumberPagination

from api.permissions import IsAdminUser, ReadOnly


class CategoryGenreViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
):

    permission_classes = [ReadOnly | IsAdminUser]
    pagination_class = PageNumberPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ('name',)
    lookup_field = 'slug'
