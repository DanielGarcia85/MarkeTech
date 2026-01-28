from django.contrib import admin
from .models import Message

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "subject", "created_at")
    search_fields = ("subject", "body")
    ordering = ("-created_at",)
