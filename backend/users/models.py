from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    first_name = models.CharField(max_length=150, verbose_name='Имя', blank=False)
    last_name = models.CharField(max_length=150, verbose_name='Фамилия', blank=False)
    email = models.EmailField(max_length=254, verbose_name='Email', blank=False, unique=True)

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f'{self.username}'
