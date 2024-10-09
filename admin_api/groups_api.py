import json
from re import search
from django.http import HttpRequest
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAdminUser, AllowAny
from admin_api.models import AdminLog
from quizes.models import DTM, Question, Quiz, Result, Variant
from users import admin
from users.models import Group, User
from .serializers import DTMSerializer, GroupSerializer, GroupSerializerWithOutStudents, QuizSerializer, ResultSerializer, TestSerializer, UserSerializer, AdminLogUserSerializer, UserSerializerWithGroup
from django.db.models import Q
from django.utils import timezone
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404


@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_groups_api(request: HttpRequest):
    search = request.GET.get('search', '')
    groups = Group.objects.filter(Q(name__icontains=search) | Q(description__icontains=search))

    paginator = PageNumberPagination()
    paginator.page_size = 10
    groups_paginated = paginator.paginate_queryset(groups, request)

    group_data = GroupSerializer(groups_paginated, many=True).data

    pages_count = list(range(1, groups.count() // paginator.page_size + (groups.count() % paginator.page_size > 0)+1))
    return Response({'status': 'ok', 'data': group_data, 'pages_count':pages_count})

@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_group_api(request: HttpRequest, group_id: int):
    group = get_object_or_404(Group, id=group_id)
    group_data = GroupSerializer(group).data
    return Response({'status': 'ok', 'data': group_data})

@api_view(['GET', 'POST'])
@permission_classes([IsAdminUser])
def add_student_to_group_api(request: HttpRequest, group_id: int):
    group = get_object_or_404(Group, id=group_id)
    if request.method == 'POST':
        data = json.loads(request.body)
        if 'data' not in data:
            return Response({'status': 'error','message': 'No data provided'})
        for student_id in data['data']:
            student = User.objects.filter(id=student_id)
            if not student.exists():
                return Response({'status': 'error','message': f'User with id {student_id} does not exist'})
            group.students.add(student[0])
        group.save()
        return Response({'status': 'ok'})
    else:
        search = request.GET.get('search', '')
        users = User.objects.exclude(guruhlar__id=group_id).filter(Q(username__icontains=search) | Q(full_name__icontains=search) | Q(email__icontains=search))

        paginator = PageNumberPagination()
        paginator.page_size = 20
        users_paginated = paginator.paginate_queryset(users, request)

        user_data = UserSerializerWithGroup(users_paginated, many=True).data
        group_data = GroupSerializerWithOutStudents(group).data

        pages_count = list(range(1, users.count() // paginator.page_size + (users.count() % paginator.page_size > 0)+1))
        return Response({'status': 'ok', 'data': user_data, 'group_data': group_data, 'pages_count':pages_count})
    
@api_view(['POST'])
@permission_classes([IsAdminUser])
def remove_student_from_group_api(request: HttpRequest, group_id: int):
    group = get_object_or_404(Group, id=group_id)
    data = json.loads(request.body)
    if 'data' not in data:
        return Response({'status': 'error','message': 'No data provided'})
    for student_id in data['data']:
        student = User.objects.filter(id=student_id)
        if not student.exists():
            return Response({'status': 'error','message': f'User with id {student_id} does not exist'})
        group.students.remove(student[0])
    group.save()
    return Response({'status': 'ok'})

@api_view(["POST"])
@permission_classes([IsAdminUser])
def create_group_api(request: HttpRequest):
    data = json.loads(request.body)
    if 'name' not in data or 'description' not in data:
        return Response({'status': 'error','message': 'Name and description are required fields'})
    group = Group(name=data['name'], description=data['description'])
    group.save()
    return Response({'status': 'ok', 'data': GroupSerializer(group).data})

@api_view(["GET"])
@permission_classes([IsAdminUser])
def get_dtms(request: HttpRequest, id:int):
    group = get_object_or_404(Group, id=id)
    dtm_ist = DTM.objects.filter(group=group)
    data = DTMSerializer(dtm_ist, many=True).data
    return Response({'status': 'ok', 'data': data})