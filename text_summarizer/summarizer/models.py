from django.db import models
from django.contrib.auth.models import User  # Optional for associating history with users

class FileHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Null for non-authenticated users
    file_name = models.CharField(max_length=255)
    summary = models.TextField()
    insights = models.JSONField()  # To store insights as structured data
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file_name} - {self.timestamp}"
