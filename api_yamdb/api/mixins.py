from api.permissions import IsAdminUser, ReadOnly
from rest_framework import filters, mixins, viewsets
from rest_framework.pagination import PageNumberPagination


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
