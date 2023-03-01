from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class FriendshipPagination(PageNumberPagination):
    # Default page size, can be overwritten by ?page_size=xxx
    page_size = 20

    # Page_size_query_param is set to None when not defined
    # Use this to define wanted page size so that it can be used
    # in the frontend to different page sizes for different clients
    page_size_query_param = 'page_size'

    # Maximum page size
    max_page_size = 20

    def get_paginated_response(self, data):
        return Response({
            'total_results': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'page_number': self.page.number,
            'has_next_page': self.page.has_next(),
            'results': data,
        })
