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