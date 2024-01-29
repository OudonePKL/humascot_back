import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from chat.models import RoomModel, MessageModel
from store.models import StoreModel
from users.models import UserModel


class ChatConsumer(AsyncWebsocketConsumer):
    # websocket 연결
    async def connect(self):
        self.store_id = self.scope["url_route"]["kwargs"]["store_id"]
        self.user_id = self.scope["url_route"]["kwargs"]["user_id"]
        self.room_group_name = f"chat_{self.store_id}_{self.user_id}"

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

        # 채팅방에 들어왔을 때 기존 메시지 내역을 가져와서 전송하는 부분
        messages = await self.get_room_messages(self.store_id, self.user_id)
        if messages:
            await self.send(text_data=json.dumps({
                'messages': [message for message in messages]
            }))

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        store_id = text_data_json.get('store_id')
        user_id = text_data_json.get('user_id')
        is_seller = text_data_json.get('is_seller')
        room = await self.get_or_create_room(store_id, user_id)
        create_message = await self.create_message(room, message, user_id, is_seller)
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "chat.message", "message": message, "user": create_message.caller, "is_seller": is_seller}
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]
        user = event["user"]
        is_seller = event['is_seller']
        name = await self.get_username(user, is_seller)
        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message, "caller": user, 'name': name}))

    @database_sync_to_async
    def get_username(self, user_id, is_seller):
        if is_seller:
            return StoreModel.objects.filter(seller_id=user_id).first().name
        else:
            return UserModel.objects.get(id=user_id).nickname

    @database_sync_to_async
    def get_or_create_room(self, store_id, user_id):
        return RoomModel.objects.get_or_create(store_id=store_id, user_id=user_id)[0]

    @database_sync_to_async
    def create_message(self, room, message, user_id, is_seller):
        if is_seller:
            return MessageModel.objects.create(room=room, message=message, caller=room.store.seller.id)
        else:
            return MessageModel.objects.create(room=room, message=message, caller=user_id)

    @database_sync_to_async
    def get_room_messages(self, store_id, user_id):
        try:
            room = RoomModel.objects.filter(store_id=store_id, user_id=user_id)
            if room.exists():
                messages = room.first().messagemodel_set.all()
                room = room.first()
                data = []
                for message in messages:
                    if str(room.store.seller.id) == str(message.caller):
                        name = room.store.name
                    else:
                        name = room.user.nickname
                    message_data = {
                        'id': message.id,
                        'message': message.message,
                        'caller': message.caller,
                        'name': name,
                        'created_at': message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    }
                    data.append(message_data)
                return data
        except Exception as e:
            print(str(e))
            return []  # 채팅방이 존재하지 않으면 빈 리스트를 반환
