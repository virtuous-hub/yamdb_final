from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from api.validation import username_is_valid
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователя"""
    email = serializers.CharField(required=True, max_length=254,
                                  validators=(
                                      UniqueValidator(
                                          queryset=User.objects.all()),
                                  ),
                                  )
    username = serializers.CharField(required=True,
                                     max_length=150,
                                     validators=[
                                         username_is_valid,
                                         UniqueValidator(
                                             queryset=User.objects.all())]
                                     )

    class Meta:
        model = User
        fields = ('username', 'email',
                  'first_name', 'last_name',
                  'bio', 'role')

    def validate_username(self, username):
        if not username_is_valid(username):
            raise serializers.ValidationError(
                "Недопустимые символы"
            )
        return username


class CreateUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        validators=(
            username_is_valid,
            UniqueValidator(queryset=User.objects.all(), ),
        ),
        max_length=150,
        required=True
    )
    email = serializers.EmailField(
        validators=(
            UniqueValidator(queryset=User.objects.all()),
        ),
        max_length=254,
        required=True
    )

    class Meta:
        model = User
        fields = ('username', 'email')

    def validate_username(self, username):
        if not username_is_valid(username):
            raise serializers.ValidationError(
                "Недопустимые символы"
            )
        if username == 'me':
            raise serializers.ValidationError(
                "Нельзя использовать имя пользователя - me"
            )
        return username
