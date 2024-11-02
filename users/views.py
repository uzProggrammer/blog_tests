from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.contrib.auth import authenticate, login, logout

from quizes.models import DtmResult, Feedback, Result
from users.models import ChatWithAdmin, Group, MessageForAdmin, User

from django.views.decorators.csrf import csrf_exempt

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
        email = data.get('email')
        if not username or not password or not email:
            return render(request, 'users/register.html', {'error': 'Ma\'lumotlar to\'liq to\'ldirilmagan', 'username': username,  'email':email})
        if User.objects.filter(username=username).exists():
            return render(request, 'users/register.html', {'error': 'Bu foydalanuvchi allaqachon ro\'yxatdan o\'tgan', 'username': username,  'email':email})
        else:
            user = User.objects.create(username=username, email=email)
            user.set_password(password)
            user.save()
            login(request, user)
            return HttpResponseRedirect('/informations/')
    return render(request, 'users/register.html')

def informations_view(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login/')
    if request.method == 'POST':
        data = request.FILES
        data1 = request.POST
        if 'image' not in data or 'full_name' not in data1 or 'date_brith' not in data1 or 'jins' not in data1 or  'full_name' not in data1:
            return render(request, 'users/ulashish.html', {'error': 'Ma\'lumotlar to\'liq to\'ldirilmagan', 'full_name': data1.get('full_name'), 'date_brith': data1.get('date_brith'), 'jins': data1.get('jins')})
        user = request.user
        image = data.get('image')
        full_name = data1.get('full_name')
        date_brith = data1.get('date_brith')
        jins = data1.get('jins')
        full_name = data1.get('full_name')
        user.image = image
        user.full_name = full_name
        user.date_brith = date_brith
        user.jins = jins
        user.save()
        return HttpResponseRedirect('/select-group/')
    return render(request, 'users/informations.html')

def select_group_view(request):
    user = request.user
    if not user.is_authenticated:
        return HttpResponseRedirect('/login/')
    if request.method == 'POST':
        data = request.POST
        group = data.get('group')
        group = get_object_or_404(Group, id=group)
        group.students.add(user)
        group.save()
        return HttpResponseRedirect('/profile/' + user.username + '/')
    groups = Group.objects.all()
    return render(request, 'users/select_group.html', {'groups': groups, 'user': user})

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


@csrf_exempt
def send_message_admin(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login/')
    if request.method == 'POST':
        chat, created = ChatWithAdmin.objects.get_or_create(user=request.user)
        data = request.POST
        message = data.get('message')
        message = MessageForAdmin.objects.create(message=message, user=request.user)
        chat.messages.add(message)
        chat.created_at = message.created_at
        chat.last_message = message.message
        chat.save()
        data = {
            "user":{
                'image': request.user.image.url if request.user.image else '',
            },
            'message': message.message,
            'date': message.created_at.strftime('%H:%M'),
            "id":message.id,
            'user_message_id': -message.id,
        }
        return JsonResponse(data)
    return HttpResponseRedirect('/')

def read_all_messages(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login/')
    messages = MessageForAdmin.objects.filter(is_read=False, user1=request.user)
    for message in messages:
        message.is_read = True
        message.save()
    return HttpResponseRedirect('/')

def my_feedbacks(request):
    feedbacks = Feedback.objects.filter(user=request.user)
    return render(request, 'users/my_feedbacks.html', {'feedbacks': feedbacks})