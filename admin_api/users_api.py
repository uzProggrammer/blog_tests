import json
from django.http import HttpRequest
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAdminUser, AllowAny
from admin_api.models import AdminLog
from quizes.models import DtmResult, Question, Quiz, Result, Variant
from users import admin
from users.models import User
from .serializers import DTMResultSerializer, QuizSerializer, ResultSerializer, TestSerializer, UserSerializer, AdminLogUserSerializer
from django.db.models import Q
from django.utils import timezone
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404

@api_view(['GET'])
@permission_classes([IsAdminUser])
def all_users_api(request: HttpRequest):
    search = request.GET.get('search', '')
    users = User.objects.filter(Q(username__icontains=search) | Q(email__icontains=search) | Q(full_name__icontains=search))
    paginator = PageNumberPagination()
    paginator.page_size = 10
    page_obj = paginator.paginate_queryset(users, request)
    users_data = UserSerializer(page_obj, many=True).data
    pages_count = list(range(1, users.count() // paginator.page_size + (users.count() % paginator.page_size > 0)+1))
    return Response({'status':'ok', 'data':users_data, 'pages_count':pages_count})

@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_user_api(request: HttpRequest, username: str):
    user = get_object_or_404(User, username=username)
    user_data = UserSerializer(user).data

    paginator = PageNumberPagination()
    paginator.page_size = 10
    results = Result.objects.filter(user=user).order_by('-id')
    page_obj = paginator.paginate_queryset(results, request)

    results_data = ResultSerializer(page_obj, many=True).data
    user_data['results'] = results_data
    pages_count = list(range(1, results.count() // paginator.page_size + (results.count() % paginator.page_size > 0)+1))
    return Response({'status':'ok', 'data':user_data, 'pages_count':pages_count})

@api_view(['POST'])
@permission_classes([IsAdminUser])
def update_user_api(request: HttpRequest, username: str):
    user = get_object_or_404(User, username=username)
    data = json.loads(request.body)
    if 'username' not in data or 'email' not in data or 'full_name' not in data or 'date_brith' not in data or 'jins' not in data or 'is_staff' not in data:
        return Response({'status':'error','message':'Ma\'lumotlarni to\'liq kiriting!'})
    user.username = data['username']
    user.email = data['email']
    user.full_name = data['full_name']
    user.date_brith = data['date_brith']
    user.jins = data['jins']
    user.is_staff = data['is_staff']
    user.save()
    user_data = UserSerializer(user).data
    return Response({'status':'ok', 'username':user.username, 'data':user_data})


@api_view(['POST'])
@permission_classes([IsAdminUser])
def update_password_api(request: HttpRequest, username: str):
    user = get_object_or_404(User, username=username)
    data = json.loads(request.body)
    if 'password' not in data:
        return Response({'status':'error','message':'Ma\'lumotlarni to\'liq kiriting!'})
    user.set_password(data['password'])
    Token.objects.filter(user=user).delete()
    user.save()
    return Response({'status':'ok', 'username':user.username})

@api_view(['POST'])
@permission_classes([IsAdminUser])
def delete_user_api(request: HttpRequest, username: str):
    user = get_object_or_404(User, username=username)
    data = json.loads(request.body)
    if 'password' not in data:
        return Response({'status':'error','message':'Ma\'lumotlarni to\'liq kiriting!'})
    if not user.check_password(data['password']):
        return Response({'status':'error','message':'Xato parol kiritdingiz'})
    user.delete()
    return Response({'status':'ok', 'username':user.username})


    return Response({'status':'ok'})

@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_user_dtm_results(request: HttpRequest, username: str):
    user = get_object_or_404(User, username=username)
    results = DtmResult.objects.all()

    results_data = DTMResultSerializer(results, many=True).data
    return Response({'status':"ok", 'data':results_data})