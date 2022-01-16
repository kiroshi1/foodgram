from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    first_name = models.CharField(
        max_length=150, verbose_name='First_name')
    last_name = models.CharField(
        max_length=150, verbose_name='Last_name')
    email = models.EmailField(
        max_length=254, verbose_name='Email', unique=True)

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f'{self.username}'
