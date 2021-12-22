from rest_framework.response import Response
from rest_framework import serializers, viewsets, status
from users.models import CustomUser
from .serializers import CustomUserSerializer
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.decorators import action


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def get_permissions(self):
        if self.action in ['create', 'list']:
            return (AllowAny(),)
        return super().get_permissions()

    def retrieve(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        if id == 'me':
            user = request.user
        else:
            user = self.get_object()
        serializer = self.get_serializer(user)
        return Response(serializer.data)


    # @action(detail=False, url_path='me')
    # def request_user_info(self, request):
    #     users = CustomUser.objects.all()[:2]
    #     serializer = self.get_serializer(users, many=True)
    #     return Response(serializer.data)