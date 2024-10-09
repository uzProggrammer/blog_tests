from django.contrib import admin
from users.models import User, Group

admin.site.register(User)
admin.site.register(Group)