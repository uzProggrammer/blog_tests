from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.contrib.auth import authenticate, login, logout

from quizes.models import DtmResult, Result
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


def profile_view(request, username):
    user = get_object_or_404(User, username=username)
    if user == request.user and request.method == 'POST':
        if 'email' not in request.POST and 'date_brith' not in request.POST and 'jins' not in request.POST and 'full_name' not in request.POST:
            return render(request, 'users/profile.html', {'profile': user, 'error': 'Ma\'lumotlar to\'liq to\'ldirilmagan'})
        user.email = request.POST.get('email')
        user.date_brith = request.POST.get('date_brith')
        user.jins = request.POST.get('jins')
        user.full_name = request.POST.get('full_name')
        user.save()
        return HttpResponseRedirect('/profile/' + username + '/')
    
    natijalar = Result.objects.filter(user=user)
    dtm_results = DtmResult.objects.filter(user=user)
    return render(request, 'users/profile.html', {'profile': user, 'results': natijalar, 'dtm_results': dtm_results})

def pofile_image_update(requset, username):
    user = get_object_or_404(User, username=username)
    if requset.method == 'POST':
        if 'image' not in requset.FILES:
            return HttpResponseRedirect('/profile/' + username + '/')
        user.image = requset.FILES.get('image')
        user.save()
        return HttpResponseRedirect('/profile/' + username + '/')
    return HttpResponseRedirect('/profile/' + username + '/')