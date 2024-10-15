from django.contrib import admin
from users.models import User, Group, MessageForAdmin

admin.site.register(User)
admin.site.register(Group)
admin.site.register(MessageForAdmin)