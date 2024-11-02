import json
import os
import re
from django.http import HttpRequest
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAdminUser, AllowAny
from admin_api.docx_complie import to_dict_question
from admin_api.models import AdminLog
from quizes.models import Question, Quiz, Result, Variant
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
def create_questions_with_docx(request: HttpRequest, pk: int):
    quiz = get_object_or_404(Quiz, pk=pk)
    if 'file' not in request.FILES:
        return Response({'status':"error", 'error':"Iltimos faylni tanlang!"})
    file = request.FILES['file']
    if not file.name.endswith('.docx') and not file.content_type.endswith('.doc'):
        return Response({'status':"error", 'error':"Fayl formati noto'g'ri!"})
    try:
        from docx import Document
    except ImportError:
        return Response({'status':"error", 'error':"Docx moduli topilmadi!"})
    quiz.docx_file = file
    quiz.save()
    try:
        data = to_dict_question(quiz.docx_file.path)
    except:
        return Response({'status':"error", 'error':"Iltimos testlarni shablonga moslashtirilganiga ishonch hosil qiling!"})
    i=0
    if data:
        quiz.questions.all().delete()
    for question in data[0]:
        tozalangan_matn = re.sub(r'^\d+\.', '', question['question'])
        question_obj = Question.objects.create(
            quiz=quiz,
            text=tozalangan_matn,
            ball=float(data[2][i])
        )
        j = 'A'
        for variant in question['answers']:
            Variant.objects.create(
                text=variant,
                is_correct=data[1][i]==j,
                question=question_obj,
                quiz=quiz,
                
            )
            j = chr(ord(j) + 1)
        i+=1

    os.remove(quiz.docx_file.path)
    quiz.docx_file = None
    quiz.save()
    return Response({'status': "ok"})


@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_questions_with_pdf(request: HttpRequest, pk: int):
    quiz = get_object_or_404(Quiz, pk=pk)
    if 'file' not in request.FILES:
        return Response({'status':"error", 'error':"Iltimos faylni tanlang!"})
    file = request.FILES['file']
    if not file.name.endswith('.pdf'):
        return Response({'status':"error", 'error':"Fayl formati noto'g'ri!"})
    try:
        from admin_api.pdf_complie import html_to_json
    except ImportError:
        return Response({'status':"error", 'error':"PDF moduli topilmadi!"})
    quiz.docx_file = file
    quiz.save()
    try:
        data = html_to_json(quiz.docx_file.path)
    except Exception as e:
        print(e)
        return Response({'status':"error", 'error':"Iltimos testlarni shablonga moslashtirilganiga ishonch hosil qiling!"})
    i=0
    if data:
        quiz.questions.all().delete()
    for tttt in data:
        test = Question.objects.create(
            quiz=quiz,
            text=tttt['test'],
            ball=2
        )
        v = "A"
        for variant in tttt['variants']:
            varaint1 = Variant.objects.create(question=test, text=variant, quiz=quiz, is_correct=v==tttt['true_answer'])
            v = chr(ord(v) + 1)
    os.remove(quiz.docx_file.path)
    quiz.docx_file = None
    quiz.save()
    return Response({'status': "ok"})

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
    paginator.page_size = 10
    paginated_tests = paginator.paginate_queryset(results, request)
    pages_count = list(range(1, results.count() // paginator.page_size + (results.count() % paginator.page_size > 0)+1))

    results_data = ResultSerializer(paginated_tests, many=True).data
    return Response({'status': "ok", 'data':results_data, "pages_count":pages_count, "similars_persent":similars_persent})

@api_view(['GET'])
@permission_classes([IsAdminUser])
def result_api(request: HttpRequest, pk: int, pk1:int):
    quiz = get_object_or_404(Quiz, pk=pk)
    result = get_object_or_404(Result, quiz=quiz, pk=pk1)
    result_data = ResultSerializer(result).data
    return Response({'status': "ok", 'data':result_data})

@api_view(['POST'])
@permission_classes([IsAdminUser])
def delete_results_api(request: HttpRequest, pk: int,):
    quiz = get_object_or_404(Quiz, pk=pk)
    try:
        data = json.loads(request.body)
    except:
        return Response({'status':'error', 'message': "Ma'lumotlar to'g'ri kiritilmagan!"})
    
    for i in data:
        r = Result.objects.filter(id=i)
        if r.exists():
            r.delete()
    return Response({'status':'ok', 'message':'Barcha belgilangan natijalar o\'chirildi!'})

@api_view(['POST'])
@permission_classes([IsAdminUser])
def change_results_api(request: HttpRequest, pk: int,):
    quiz = get_object_or_404(Quiz, pk=pk)
    try:
        data = json.loads(request.body)
    except:
        return Response({'status':'error', 'message': "Ma'lumotlar to'g'ri kiritilmagan!"})
    if 'is_cheater' not in data or 'selecteds' not in data or 'remove_cheater' not in data:
        return Response({'status':'error', 'message': "Ma'lumotlar to'lliq kiritilmagan!"})
    for i in data['selecteds']:
        r = Result.objects.filter(id=i)
        if r.exists():
            r=r.first()
            r.is_cheater = False if data['remove_cheater']==True else data['is_cheater']
            r.save()
    return Response({'status':'ok', 'message':'Barcha belgilangan natijalar o\'zgartirildi!'})