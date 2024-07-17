from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import ParseError


class ProductPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100.0

    def get_page_size(self, request):
        try:
            if self.page_size_query_param in request.query_params:
                page_size = int(request.query_params[self.page_size_query_param])
                if page_size > self.max_page_size:
                    page_size = self.max_page_size
                elif page_size < 1:
                    raise ValueError
                return page_size
        except (ValueError, TypeError):
            raise ParseError(f"Invalid page size: {request.query_params.get(self.page_size_query_param)}")
        return self.page_size
