from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import viewsets
from .models import Message
from .serializers import MessageSerializer

@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    return Response({"status": "ok"})

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all().order_by("-created_at")
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
