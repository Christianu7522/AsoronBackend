from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class DefaultPagination(PageNumberPagination):
    page_size=6
    def get_paginated_response(self, data):
        total_pages = self.page.paginator.num_pages
        return Response({
            'Paginacion': {
                'actual_page': self.page.number,
                'count': self.page.paginator.count,
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
                'total_pages': total_pages
            },
            'results': data
        })

class CustomPagination(PageNumberPagination):
    page_size=1
    def get_paginated_response(self, data):
        total_pages = self.page.paginator.num_pages
        return Response({
            'Paginacion': {
                'actual_page': self.page.number,
                'count': self.page.paginator.count,
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
                'total_pages': total_pages
            },
            'results': data
        })

class EventoPagination(PageNumberPagination):
    page_size=3
    def get_paginated_response(self, data):
        total_pages = self.page.paginator.num_pages
        return Response({
            'Paginacion': {
                'actual_page': self.page.number,
                'count': self.page.paginator.count,
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
                'total_pages': total_pages
            },
            'results': data
        })