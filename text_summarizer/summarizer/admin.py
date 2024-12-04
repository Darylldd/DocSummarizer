from django.contrib import admin
from .models import FileHistory

@admin.register(FileHistory)
class FileHistoryAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'user', 'timestamp')
    search_fields = ('file_name', 'user__username')
