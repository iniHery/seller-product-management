from rest_framework.pagination import PageNumberPagination


class ProductPagination(PageNumberPagination):
    """Paginate products five items at a time."""

    page_size = 5
