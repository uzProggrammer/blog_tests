"""
URL configuration for blog_tests project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.utils import timezone
from django.shortcuts import render
from users.models import MessageForAdmin
from users.views import login_view, logout_view,register_view,profile_view, pofile_image_update, send_message_admin,read_all_messages, my_feedbacks,informations_view, select_group_view
from quizes.models import DTM

def home(request):
    if request.user.is_authenticated:
        messages_with_admin = MessageForAdmin.objects.filter(user=request.user)
        messages_with_admin1 = MessageForAdmin.objects.filter(user1=request.user, is_admin_message=True)
        messages = messages_with_admin | messages_with_admin1
        messages = messages.order_by('created_at')
        new_message_count = messages_with_admin1.filter(is_read=False).count()
        if request.user.guruhlar.exists():
            blog_tests = DTM.objects.filter(group=request.user.guruhlar.first(), start_date__gt=timezone.now())
            blog_tests1 = DTM.objects.filter(group=None, start_date__gt=timezone.now())
            blog_tests = blog_tests | blog_tests1
            return render(request, 'home.html', {'blog_tests': blog_tests, 'messages': messages,'new_message_count': new_message_count})
        return render(request, 'home.html', {'messages': messages, 'new_message_count': new_message_count})
        
    return render(request, 'home.html')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('tests/', include('quizes.urls')),
    path('admin-api/', include('admin_api.urls')),
    path('blog-tests/', include('quizes.blog_tests_urls')),
    path('login/', login_view),
    path('logout/', logout_view),
    path('register/', register_view),
    path('profile/<str:username>/', profile_view),
    path('profile/<str:username>/update-image/', pofile_image_update),
    path('send-message/', send_message_admin),
    path('read-messages/', read_all_messages),
    path('my-feedbacks/', my_feedbacks),
    path('informations/', informations_view),
    path('select-group/', select_group_view),
] 

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)