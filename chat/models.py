from django.db import models
from users.models import UserModel
from store.models import StoreModel


class RoomModel(models.Model):
    class Meta:
        db_table = "room"
        verbose_name_plural = "1. 채팅방 목록"

    store = models.ForeignKey(
        StoreModel, on_delete=models.CASCADE, verbose_name="스토어", null=True, blank=True
    )
    user = models.ForeignKey(
        UserModel, on_delete=models.CASCADE, verbose_name="유저", null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)


class MessageModel(models.Model):
    class Meta:
        verbose_name_plural = "2. 메세지 내역"

    # category = (("seller", "seller"), ("user", "user"))
    room = models.ForeignKey(RoomModel, on_delete=models.CASCADE, verbose_name="채팅방")
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    caller = models.CharField(max_length=100, verbose_name="발신자")  # 1=상점, 2=유저

    def __str__(self):
        return str(self.room.id)

    def last_30_messages(self, room_id):
        return MessageModel.objects.filter(room_id=room_id).order_by('created_at')[:30]
