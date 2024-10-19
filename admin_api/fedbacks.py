import json
from django.http import HttpRequest
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAdminUser
from admin_api.serializers import FeedbackSerializer, FeedbackWithVariantsSerializer
from quizes.models import Feedback
from users.models import User
from django.db.models import Q
from django.utils import timezone
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404

@api_view(['GET'])
@permission_classes([IsAdminUser])
def all_fedbacks_api(request: HttpRequest):
    search = request.GET.get('search', '')
    users = Feedback.objects.filter(Q(user__username__icontains=search) | Q(user__email__icontains=search) | Q(user__full_name__icontains=search)).order_by('-id')
    paginator = PageNumberPagination()
    paginator.page_size = 10
    page_obj = paginator.paginate_queryset(users, request)
    users_data = FeedbackSerializer(page_obj, many=True).data
    pages_count = list(range(1, users.count() // paginator.page_size + (users.count() % paginator.page_size > 0)+1))
    return Response({'status':'ok', 'data':users_data, 'pages_count':pages_count})

@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_fedback_api(request: HttpRequest, id):
    feedback = get_object_or_404(Feedback, id=id)
    data = FeedbackWithVariantsSerializer(feedback).data
    return Response({'status':'ok', "data":data})

@api_view(['POST'])
@permission_classes([IsAdminUser])
def set_is_true_api(request: HttpRequest, id:int):
    feedback = get_object_or_404(Feedback, id=id)
    try:
        data = json.loads(request.body)
    except:
        return Response({'status':'ok', 'message':"Ma\'lumotlar to\'g\'ri kiritilmagan"})
    if 'send_ball' not in data or 'is_true' not in data:
        return Response({'status':'ok', 'message':"Ma\'lumotlar to\'lliq kiritilmagan"})
    if data['is_true']==False and data['send_ball'] == True:
        return Response({'status':'ok', 'message':"Ma\'lumotlar to\'g\'ri kiritilmagan! E'tiroz to'g'ri bo'lmasa e'ritoz egasiga ball berib bo'lmaydi."})
    feedback.is_true = data['is_true']
    feedback.send_ball = data['send_ball']
    feedback.save()
    if feedback.is_true and feedback.send_ball:
        feedback.answer.is_correct = True
        feedback.answer.results.first().score+=feedback.question.ball
        feedback.answer.with_feedback = True
        feedback.answer.save()
    else:
        feedback.answer.is_correct = False
        feedback.save()
        feedback.answer.results.first().score+=feedback.question.ball
        feedback.answer.with_feedback = True
        feedback.answer.save()
    return Response({'status':'ok', 'message': 'E\'tiroz o\'zgartirildi'})