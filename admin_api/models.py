from django.db import models

from users.models import User

class AdminLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_logs')
    action = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    href = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=255, choices=(('create', 'create'), ('update', 'update'), ('delete', 'delete')), default='create')

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.action} - {self.created_at}"