# backend/config/views.py

"""
Project views — technical endpoints that belong to no business domain
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Expose the endpoints that describe the state of the backend itself. Business
features live in their own applications, not here.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    """Report that the backend is running. Requires no authentication."""
    return Response({"status": "ok"})
