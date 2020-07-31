from rest_framework import pagination


class Pagination(pagination.CursorPagination):
    ordering = '-id'

    def paginate_queryset(self, queryset, request, view=None):
        return super().paginate_queryset(queryset, request, view)
