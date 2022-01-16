from djoser.serializers import UserCreateSerializer


class UserRegistrationSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'password')
