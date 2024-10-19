import datetime
import json
from django.http import HttpRequest
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAdminUser, AllowAny
from admin_api.models import AdminLog
from quizes.models import DTM, DtmResult, Question, Quiz, Result, Variant
from quizes.templatetags.get_results import get_ball, get_trues
from users import admin
from users.models import Group, User
from .serializers import DTMResultSerializer, DTMSerializer, DTMWithQuizsSerializer, GroupForDTMSerializer, QuizSerializer, TestSerializer
from django.db.models import Q
from django.utils import timezone
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404, render

@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_quizes(request: HttpRequest):
    search = request.GET.get('search', '')
    quizes = DTM.objects.filter(Q(title__icontains=search))

    paginator = PageNumberPagination()
    paginator.page_size = 10
    quizes_paginated = paginator.paginate_queryset(quizes, request)

    test_data = DTMSerializer(quizes_paginated, many=True).data

    pages_count = list(range(1, quizes.count() // paginator.page_size + (quizes.count() % paginator.page_size > 0)+1))
    return Response({'status': 'ok', 'data': test_data, 'pages_count':pages_count})

@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_blog_test(request: HttpRequest, pk: int):
    quiz = get_object_or_404(DTM, pk=pk)
    data = DTMWithQuizsSerializer(quiz).data
    return Response({'status': 'ok', 'data': data})

@api_view(['POST'])
@permission_classes([IsAdminUser])
def edit_blog_test(request: HttpRequest, pk: int):
    quiz = get_object_or_404(DTM, pk=pk)
    data = json.loads(request.body)
    if 'title' not in data or 'countinuis_time' not in data or 'start_date' not in data:
        return render(request, '404.html', status=404)
    quiz.title = data['title']
    quiz.countinuis_time = data['countinuis_time'] # H:M:S
    quiz.start_date = data['start_date']
    quiz.group = Group.objects.get(id=data['group']) if data['group'] else None

    quiz.end_date = datetime.datetime.strptime(quiz.start_date, '%Y-%m-%d') + timezone.timedelta(days=1)

    quiz.save()
    data = DTMWithQuizsSerializer(quiz).data
    return Response({'status': 'ok', 'data': data})

@api_view(['POST'])
@permission_classes([IsAdminUser])
def delete_question(request: HttpRequest, pk: int):
    question = get_object_or_404(Question, pk=pk)
    question.delete()
    return Response({'status': 'ok'})
    
@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_results(request: HttpRequest, pk:int):
    quiz = get_object_or_404(DTM, pk=pk)
    results = DtmResult.objects.all().order_by('place')
    print(request.GET)
    similars_persent = []
    if 'similar_to' in request.GET:
        s = request.GET.get('similar_to')
        if not str(s).isdigit():
            pass
        else:
            s = quiz.results.filter(id=s)
            if s.exists():
                s = s.first()
                similars = s.similar_variants(test=quiz)
                results = similars[0]
                similars_persent = similars[1]
    paginator = PageNumberPagination()
    paginator.page_size = 15
    results_paginated = paginator.paginate_queryset(results, request)

    data = DTMResultSerializer(results_paginated, many=True).data
    data1 = DTMSerializer(quiz).data

    pages_count = list(range(1, results.count() // paginator.page_size + (results.count() % paginator.page_size > 0)+1))
    return Response({"status":'ok', 'data':data,'dtm':data1, 'pages_count':pages_count, 'similars_persent':similars_persent})    


@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_result(request: HttpRequest, pk:int, pk1:int):
    quiz = get_object_or_404(DTM, pk=pk)
    result = get_object_or_404(DtmResult, pk=pk1)

    data = DTMResultSerializer(result).data
    data1 = DTMSerializer(quiz).data

    trues = []
    balls = []
    for question in quiz.quizs.all():
        trues.append(get_trues(result, question))
        balls.append(get_ball(result, question))
    return Response({"status":'ok', 'data':data,'dtm':data1, "trues":trues, 'balls':balls, "total_ball":sum(balls)})

@api_view(['POST'])
@permission_classes([IsAdminUser])
def edit_question(request: HttpRequest, pk: int, pk1: int):
    question = get_object_or_404(Question, pk=pk1)
    try:
        data = json.loads(request.body)
    except:
        return Response({'status': 'error', 'data': 'Ma\'lumot xato to\'ldirilgan!'})
    serializer = TestSerializer(question, data=data)
    if serializer.is_valid():
        serializer.save()
        return Response({'status': 'ok', 'data': serializer.data})
    return Response({'status': 'error', 'data': 'Ma\'lumot xato to\'ldirilgan!'})

@api_view(['POST'])
@permission_classes([IsAdminUser])
def add_question(request: HttpRequest, pk: int, pk1:int):
    quiz = get_object_or_404(DTM, pk=pk)
    try:
        data: dict = json.loads(request.body)
    except:
        return Response({'status': 'error', 'data': 'Ma\'lumot xato to\'ldirilgan!'})
    fan = get_object_or_404(Quiz, id=pk1)
    print(data)
    if 'text' not in data or 'ball' not in data or 'variants' not in data:
        return Response({'status': 'error', 'data': 'Ma\'lumot xato to\'ldirilgan!'})
    question = Question.objects.create(text=data['text'], ball=data['ball'], quiz=fan)
    for variant in data['variants']:
        Variant.objects.create(text=variant["text"], question=question, is_correct=variant["is_correct"], quiz=fan)
    return Response({'status': 'ok', 'data': 'Savol qo\'shildi!'})

@api_view(['POST'])
@permission_classes([IsAdminUser])
def edit_quiz(request: HttpRequest, pk: int, pk1:int):
    quiz = get_object_or_404(DTM, pk=pk)
    try:
        data: dict = json.loads(request.body)
    except:
        return Response({'status': 'error', 'data': 'Ma\'lumot xato to\'ldirilgan!'})
    if 'title' not in data:
        return Response({'status': 'error', 'data': 'Ma\'lumot xato to\'ldirilgan!'})
    test = get_object_or_404(Quiz, id=pk1)
    test.title = data['title']
    test.save()
    return Response({'status': 'ok', 'data': 'Savol o\'zgartirildi!'})

@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_quiz(request: HttpRequest, pk: int):
    quiz = get_object_or_404(DTM, pk=pk)
    try:
        data: dict = json.loads(request.body)
    except:
        return Response({'status': 'error', 'data': 'Ma\'lumot xato to\'ldirilgan!'})
    if 'title' not in data:
        return Response({'status': 'error', 'data': 'Ma\'lumot xato to\'ldirilgan!'})
    test = Quiz.objects.create(title=data['title'], countinuis_time="02:00:00", scince=data['title'], description="....")
    quiz.quizs.add(test)
    quiz.save()
    return Response({'status': 'ok', 'data': 'Savol qo\'shildi!'})

@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_groups(request: HttpRequest):
    groups = Group.objects.all()
    data = GroupForDTMSerializer(groups, many=True).data
    return Response({'status': 'ok', 'data': data})

@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_dtm(request: HttpRequest):
    try:
        data: dict = json.loads(request.body)
    except:
        return Response({'status': 'error', 'data': 'Ma\'lumot xato to\'ldirilgan!'})
    if 'title' not in data or 'countinuis_time' not in data or 'start_date' not in data or 'group' not in data:
        return Response({'status': 'error', 'data': 'Ma\'lumot xato to\'ldirilgan!'})
    group = get_object_or_404(Group, id=data['group'])
    dtm = DTM.objects.create(title=data['title'], countinuis_time=data['countinuis_time'], start_date=data['start_date'], group=group)
    dtm.start_date = datetime.datetime.fromisoformat(dtm.start_date)
    dtm.end_date = dtm.start_date + timezone.timedelta(days=1)
    dtm.save()
    return Response({'status': 'ok', 'data': 'Test qo\'shildi!', 'id':dtm.id})


@api_view(['POST'])
@permission_classes([IsAdminUser])
def change_results_api(request: HttpRequest, pk: int,):
    quiz = get_object_or_404(DTM, pk=pk)
    try:
        data = json.loads(request.body)
    except:
        return Response({'status':'error', 'message': "Ma'lumotlar to'g'ri kiritilmagan!"})
    if 'is_cheater' not in data or 'selecteds' not in data or 'remove_cheater' not in data:
        return Response({'status':'error', 'message': "Ma'lumotlar to'lliq kiritilmagan!"})
    print(type(data['selecteds']))
    for i in data['selecteds']:
        r = DtmResult.objects.filter(id=i)
        if r.exists():
            r=r.first()
            r.is_cheater = False if data['remove_cheater']==True else data['is_cheater']
            r.save()
    return Response({'status':'ok', 'message':'Barcha belgilangan natijalar o\'zgartirildi!'})

@api_view(['POST'])
@permission_classes([IsAdminUser])
def delete_results_api(request: HttpRequest, pk: int,):
    quiz = get_object_or_404(DTM, pk=pk)
    try:
        data = json.loads(request.body)
    except:
        return Response({'status':'error', 'message': "Ma'lumotlar to'g'ri kiritilmagan!"})
    
    for i in data:
        r = DtmResult.objects.filter(id=i)
        if r.exists():
            r.delete()
    return Response({'status':'ok', 'message':'Barcha belgilangan natijalar o\'chirildi!'})