from django.contrib.auth.models import User
from django.db import models


class Snippet(models.Model):
    name = models.CharField(max_length=200 , default='')
    text = models.TextField(max_length=5000)
    condition = models.CharField(max_length=200 , default='')
    count = models.CharField(max_length=200 , default='')
    send_user = models.CharField(max_length=200 , default='')
    status = models.CharField(max_length=200 , default='Ожидается подтверждение')
    creation_date = models.DateTimeField()
    user = models.ForeignKey(
        to=User, on_delete=models.CASCADE, blank=True, null=False , default=1
    )  # can be empty due to usage of AnonymousUser

class RepairRequest(models.Model):
    snippet = models.ForeignKey(Snippet, on_delete=models.CASCADE, related_name='repair_requests')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField(max_length=1000, verbose_name="Описание проблемы")
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=200, default="Ожидает рассмотрения", verbose_name="Статус заявки")

    def __str__(self):
        return f"Заявка на ремонт #{self.id} для {self.snippet.name}"
    

class Buy(models.Model):
    name = models.TextField(max_length=200, default =" ")
    time_of_create = models.DateTimeField()
    count = models.CharField(max_length=200 , default='')
    send_user = models.CharField(max_length=200 , default='')

    def __str__(self):
        return self.name
