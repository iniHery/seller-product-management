from rest_framework.pagination import PageNumberPagination


class ProductPagination(PageNumberPagination):
    """Pagination for Product list view.

    Uses a fixed page size of 5 items per page.
    """

    page_size = 5
