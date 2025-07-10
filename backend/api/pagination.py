from rest_framework.pagination import PageNumberPagination

class JobPostPagination(PageNumberPagination):
    page_size = 5  # Number of results per page
    page_size_query_param = 'page_size'  # Allows you to customise the page size using a parameter
    max_page_size = 50  # Maximum number of results per page