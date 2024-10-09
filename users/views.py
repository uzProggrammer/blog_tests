from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout

from users.models import User


def login_view(request):
    if request.method == 'POST':
        data = request.POST
        username = data.get('username')
        password = data.get('password')
        user = User.objects.filter(username=username)
        if user.exists():
            user = user.first()
            if user.check_password(password):
                login(request, user)
                return HttpResponseRedirect('/')
            else:
                return render(request, 'users/login.html', {'error': 'Parolingiz mos elmadi', 'username': username})
        else:
            return render(request, 'users/login.html', {'error': 'Foydalanuvchi topilmadi', 'username': username})
    return render(request, 'users/login.html')

def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/login/')

def register_view(request):
    if request.method == 'POST':
        data = request.POST
        username = data.get('username')
        password = data.get('password')
        full_name = data.get('full_name')

        if User.objects.filter(username=username).exists():
            return render(request, 'users/register.html', {'error': 'Bu foydalanuvchi allaqachon ro\'yxatdan o\'tgan', 'username': username, 'full_name': full_name})
        else:
            user = User.objects.create(username=username, full_name=full_name)
            user.set_password(password)
            user.save()
            login(request, user)
            return HttpResponseRedirect('/')
    return render(request, 'users/register.html')