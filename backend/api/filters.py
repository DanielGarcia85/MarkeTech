from django_filters import rest_framework as filters
from .models import JobPost

class JobPostFilter(filters.FilterSet):
    title = filters.CharFilter(field_name="title", lookup_expr="icontains")
    location = filters.CharFilter(field_name="location", lookup_expr="icontains")
    salary_min = filters.NumberFilter(field_name="salary_min", lookup_expr="gte")
    created_after = filters.DateFilter(field_name="created_at", lookup_expr="gte") 

    class Meta:
        model = JobPost
        fields = ['title', 'location', 'salary_min', 'created_after']