import json
from django.http import HttpRequest
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAdminUser
from admin_api.serializers import ChatWithAdminSerializer, FeedbackSerializer, FeedbackWithVariantsSerializer, MessageForAdminSerializer
from quizes.models import Feedback
from users.models import ChatWithAdmin, User, MessageForAdmin
from django.db.models import Q
from django.utils import timezone
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404

@api_view(['GET'])
@permission_classes([IsAdminUser])
def all_messages_api(request: HttpRequest):
    users = ChatWithAdmin.objects.all().order_by('-created_at')
    users_data = ChatWithAdminSerializer(users, many=True).data
    return Response({'status':'ok', 'data':users_data})

@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_chat_api(request: HttpRequest, pk: int):
    chat = get_object_or_404(ChatWithAdmin, pk=pk)
    chat_data = ChatWithAdminSerializer(chat).data
    users = ChatWithAdmin.objects.all().order_by('-created_at')
    users_data = ChatWithAdminSerializer(users, many=True).data
    return Response({'status':'ok', 'data':chat_data, 'all_chats':users_data})

@api_view(["POST"])
@permission_classes([IsAdminUser])
def send_message_api(request: HttpRequest, pk: int):
    try:
        data = json.loads(request.body)
    except:
        return Response({'status':'error','message':'Yuborilgan ma\'lumot to\'g\'ri holatda emas'})
    if 'message' not in data or 'chat_id' not in data:
        return Response({'status':'error','message':'Yuborilgan ma\'lumot to\'lliq emas'})
    chat = get_object_or_404(ChatWithAdmin, id=data.get('chat_id'))
    message = MessageForAdmin.objects.create(user=chat.user, user1=request.user, message=data.get('message'), is_admin_message=True)
    chat.messages.add(message)
    chat.last_message = message.message
    chat.created_at = message.created_at
    chat.save()
    return Response({'status':'ok','message':'Xabar jo\'natildi'})
