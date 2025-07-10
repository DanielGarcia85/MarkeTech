from rest_framework.permissions import BasePermission


class IsEmployer(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='employer').exists()

    
class IsJobSeeker(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='jobseeker').exists()
    
class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='administrator').exists()