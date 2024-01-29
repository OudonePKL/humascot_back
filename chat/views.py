from datetime import timedelta

from django.db import models
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from chat.models import RoomModel
from chat.serializers import ChatSerializer
from store import serializers as st
from store.models import StoreModel, GoodsModel
from users.models import UserModel
import base64
import json


def get_user_id_from_token(access_token):
    # JWT 토큰의 페이로드 부분을 디코드
    payload_part = access_token.split('.')[1]
    payload_part += '=' * (-len(payload_part) % 4)
    # base64 디코드를 시도
    decoded_payload = base64.urlsafe_b64decode(payload_part)
    # JSON 로드를 통해 디코드된 페이로드를 파싱
    payload_data = json.loads(decoded_payload)
    return payload_data.get('user_id')


def chat_list_render(request):
    return render(request, "chat/room-list.html")


def chatroom_render(request, store_id):
    return render(request, "chat/room.html")


class RoomView(APIView):
    def get(self, request, store_id):
        context = {"error": "로그인 후 사용해주세요"}
        return render(request, "chat/room.html", context)


class ChatListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, goods_id=None):
        try:
            user_id = request.user.id
        except:
            return Response({"message": "로그인 후 사용해주세요"}, status=status.HTTP_400_BAD_REQUEST)
        if not goods_id:
            shop = StoreModel.objects.filter(seller_id=user_id)
            # 현재 시간에서 12시간을 뺀 시간 구하기
            twelve_hours_ago = timezone.now() - timedelta(hours=12)
            if shop:
                chat_list = RoomModel.objects.filter(
                    (Q(user_id=user_id) | Q(store_id=shop.first().id)) &
                    Q(created_at__gte=twelve_hours_ago)
                )[::-1]
            else:
                chat_list = RoomModel.objects.filter(
                    Q(user_id=user_id) &
                    Q(created_at__gte=twelve_hours_ago)
                )[::-1]
            serializer = ChatSerializer(chat_list, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            store = get_object_or_404(GoodsModel, id=goods_id).store
            data = {
                'store_name': store.name,
                'user': request.user.id,
                'store_id': store.id,
                'user_name': request.user.nickname,
                'user_profile': request.user.profile_image.url if request.user.profile_image else False,
                'store_image': store.seller.profile_image.url if store.seller.profile_image else False
            }
            return Response(data, status=status.HTTP_200_OK)
