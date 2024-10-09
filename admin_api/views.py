import json
from django.http import HttpRequest
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAdminUser, AllowAny
from admin_api.models import AdminLog
from quizes.models import Question, Quiz, Result, Variant
from users import admin
from users.models import User
from .serializers import QuizSerializer, ResultSerializer, TestSerializer, UserSerializer, AdminLogUserSerializer
from django.db.models import Q
from django.utils import timezone
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404

@api_view(['POST'])
@permission_classes([AllowAny])
def login_api(request: HttpRequest):
    data = json.loads(request.body)
    if 'username' not in data or 'password' not in data:
        return Response({'status':"error", 'error':"Iltimos barcha qatorlarni to'ldirganingizga ishonch hosil qiling!"})
    user = User.objects.filter(username=data['username'])
    if not user.exists():
        return Response({'status':"error", 'error':"Ushbu foydalanuvchi topilmadi!"})
    user = user.first()
    if not user.check_password(data['password']):
        return Response({'status':"error", 'error':"Parol mos emas!"})
    token, _ = Token.objects.get_or_create(user=user)
    user_serializer = UserSerializer(user)
    return Response({'status':"ok", 'token':token.key, 'user':user_serializer.data})


@api_view(['GET'])
@permission_classes([IsAdminUser])
def row_stats_api(request: HttpRequest):
    data = {
        "users":{
            'count': User.objects.count(),
            'percent': round(User.objects.filter(date_joined__month=timezone.now().month).count()/User.objects.count()*100, 2)
        },
        'tests': {
            'count': Quiz.objects.count(),
            'percent': round(Quiz.objects.filter(created_at__month=timezone.now().month).count()/Quiz.objects.count()*100, 2)
        }
    }
    return Response({'status':"ok", 'data':data})

@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_logs_api(request: HttpRequest):
    logs = AdminLog.objects.all().order_by('-id')[:10]
    logs_data = AdminLogUserSerializer(logs, many=True).data
    return Response({'status':"ok", 'data':logs_data})


@api_view(['GET'])
@permission_classes([IsAdminUser])
def all_tests_api(request: HttpRequest):
    search = request.GET.get('search', '')
    tests = Quiz.objects.filter(Q(title__icontains=search)|Q(description__icontains=search)).order_by('-id')

    paginator = PageNumberPagination()
    paginator.page_size = 10
    paginated_tests = paginator.paginate_queryset(tests, request)
    pages_count = list(range(1, tests.count() // paginator.page_size + (tests.count() % paginator.page_size > 0)+1))
    tests_data = QuizSerializer(paginated_tests, many=True).data
    return Response({'status': "ok", 'data':tests_data, 'pages_count':pages_count})


@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_test_api(request: HttpRequest, pk: int):
    test = get_object_or_404(Quiz, pk=pk)
    test_data = QuizSerializer(test).data
    questions = test.questions.all()
    questions_data = TestSerializer(questions, many=True).data
    return Response({'status': "ok", 'data':test_data,"questions_data":questions_data})


@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_test_api(request: HttpRequest, id: int):
    quiz = get_object_or_404(Quiz, pk=id)
    data = json.loads(request.body)
    if 'text' not in data or '1' not in data or '2' not in data or '3' not in data or '4' not in data or 'correct' not in data or 'ball' not in data:
        return Response({'status':"error", 'error':"Iltimos barcha qatorlarni to'ldirganingizga ishonch hosil qiling!"})
    question = Question.objects.create(
        quiz=quiz,
        text=data['text'],
        ball=data['ball'],
    )
    variant1 = Variant.objects.create(text=data['1'], is_correct=data['correct'] == 1, question=question, quiz=quiz)
    variant2 = Variant.objects.create(text=data['2'], is_correct=data['correct'] == 2, question=question, quiz=quiz)
    variant3 = Variant.objects.create(text=data['3'], is_correct=data['correct'] == 3, question=question, quiz=quiz)
    variant4 = Variant.objects.create(text=data['4'], is_correct=data['correct'] == 4, question=question, quiz=quiz)
    return Response({'status': "ok"})

@api_view(['POST'])
@permission_classes([IsAdminUser])
def delete_test_api(request: HttpRequest, id: int):
    quiz = get_object_or_404(Quiz, pk=id)
    data = json.loads(request.body)
    if 'id' not in data:
        return Response({'status':"error", 'error':"Iltimos barcha qatorlarni to'ldirganingizga ishonch hosil qiling!"})
    question = get_object_or_404(Question, pk=data['id'])
    question.delete()
    return Response({'status': "ok"})

@api_view(['POST'])
@permission_classes([IsAdminUser])
def update_test_api(request: HttpRequest, id: int):
    print(request.body)
    quiz = get_object_or_404(Quiz, pk=id)
    data = json.loads(request.body)
    if 'text' not in data or '1' not in data or '2' not in data or '3' not in data or '4' not in data or 'correct' not in data or 'ball' not in data or 'id' not in data:
        return Response({'status':"error", 'error':"Iltimos barcha qatorlarni to'ldirganingizga ishonch hosil qiling!"})
    questtion = Question.objects.filter(quiz=quiz,id=data['id'])
    if not questtion.exists():
        return Response({'status':"error", 'error':"Savol topilmadi!"})
    question = questtion.first()
    question.text = data['text']
    question.ball = data['ball']
    question.save()
    for variant in question.variants.all():
        variant.delete()
    variant1 = Variant.objects.create(text=data['1'], is_correct=data['correct'] == 1, question=question, quiz=quiz)
    variant2 = Variant.objects.create(text=data['2'], is_correct=data['correct'] == 2, question=question, quiz=quiz)
    variant3 = Variant.objects.create(text=data['3'], is_correct=data['correct'] == 3, question=question, quiz=quiz)
    variant4 = Variant.objects.create(text=data['4'], is_correct=data['correct'] == 4, question=question, quiz=quiz)
    return Response({'status': "ok"})

@api_view(['POST'])
@permission_classes([IsAdminUser])
def update_quiz_api(request: HttpRequest, id: int):
    quiz = get_object_or_404(Quiz, pk=id)
    data = json.loads(request.body)
    if 'title' not in data or 'countinuis_time' not in data or 'is_public' not in data or 'scince' not in data:
        return Response({'status':"error", 'error':"Iltimos barcha qatorlarni to'ldirganingizga ishonch hosil qiling!"})
    quiz.title = data['title']
    quiz.countinuis_time = data['countinuis_time']
    quiz.is_public = data['is_public']
    quiz.scince = data['scince']
    quiz.save()
    admin_log = AdminLog.objects.create(
        user=request.user,
        action=f"{quiz.title} tahrirlandi.",
        href=f'/tests/{quiz.id}',
        type='update'
    )
    return Response({'status': "ok"})

@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_quiz_api(request: HttpRequest):
    data = json.loads(request.body)
    if 'title' not in data or 'continues_time' not in data or 'scince' not in data:
        return Response({'status':"error", 'error':"Iltimos barcha qatorlarni to'ldirganingizga ishonch hosil qiling!"})
    quiz = Quiz.objects.create(
        title=data['title'],
        countinuis_time=data['continues_time'],
        scince=data['scince'],
    )
    admin_log = AdminLog.objects.create(
        user=request.user,
        action=f"{quiz.title} yaratildi.",
        href=f'/tests/{quiz.id}',
        type='create'
    )
    return Response({'status': "ok", 'id': quiz.id})

@api_view(['GET'])
@permission_classes([IsAdminUser])
def results_api(request: HttpRequest, pk: int):
    quiz = get_object_or_404(Quiz, pk=pk)
    results = quiz.results.all()
    results_data = ResultSerializer(results, many=True).data
    return Response({'status': "ok", 'data':results_data})

@api_view(['GET'])
@permission_classes([IsAdminUser])
def result_api(request: HttpRequest, pk: int, pk1:int):
    quiz = get_object_or_404(Quiz, pk=pk)
    result = get_object_or_404(Result, quiz=quiz, pk=pk1)
    result_data = ResultSerializer(result).data
    return Response({'status': "ok", 'data':result_data})