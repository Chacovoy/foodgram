from rest_framework.pagination import PageNumberPagination

from foodgram.constants import PAGE_SIZE, PAGE_SIZE_QUERY_PARAM


class CustomPagination(PageNumberPagination):
    page_size_query_param = PAGE_SIZE_QUERY_PARAM
    page_size = PAGE_SIZE
