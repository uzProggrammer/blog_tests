from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ball = models.FloatField(default=0)
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    full_name = models.CharField(max_length=100)
    date_brith = models.DateField(null=True, blank=True)
    jins = models.CharField(max_length=10, choices=(('Erkak', 'Erkak'), ('Ayol', 'Ayol')))

    class Meta:
        verbose_name = 'Foydalanuvchi'
        verbose_name_plural = 'Foydalanuvchilar'

    def __str__(self):
        return self.full_name
    
class Group(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    students = models.ManyToManyField(User, related_name='guruhlar')
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Guruh'
        verbose_name_plural = 'Guruhlar'

    def __str__(self):
        return self.name
    
class ChatWithAdmin(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chats_with_admin')
    messages = models.ManyToManyField('MessageForAdmin', related_name='chats_with_admin')
    created_at = models.DateTimeField(auto_now_add=True)
    last_message = models.TextField(null=True, blank=True)
    class Meta:
        verbose_name = 'Admin chat'
        verbose_name_plural = 'Admin chatlar'

    def __str__(self):
        return self.user.full_name
    
    
class MessageForAdmin(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages_for_admin')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    is_admin_message = models.BooleanField(default=False)
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages_for_user1', null=True, blank=True)

    class Meta:
        verbose_name = 'Admin xabar'
        verbose_name_plural = 'Admin xabarlar'

    def __str__(self):
        return self.user.full_name