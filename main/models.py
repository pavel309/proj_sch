from django.contrib.auth.models import User
from django.db import models


class Snippet(models.Model):
    name = models.CharField(max_length=200 , default='')
    text = models.TextField(max_length=5000)
    condition = models.CharField(max_length=200 , default='')
    count = models.CharField(max_length=200 , default='')
    send_user = models.CharField(max_length=200 , default='')
    creation_date = models.DateTimeField()
    user = models.ForeignKey(
        to=User, on_delete=models.CASCADE, blank=True, null=True
    )  # can be empty due to usage of AnonymousUser
