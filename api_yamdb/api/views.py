from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Avg
from django.shortcuts import get_object_or_404

from http import HTTPStatus
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.filters import SearchFilter

from api.mixins import CategoryGenreViewSet
from api.permissions import IsAdminUser, AuthorOrStaff, ReadOnly
from api.serializers import TokenSerializer
from api.filters import TitleFilter
from api.serializers import (
    CategorySerializer,
    GenreSerializer,
    TitleReadSerializer,
    TitleSerializer,
    ReviewSerializer,
    CommentSerilizer,
    TokenSerializer,
)
from reviews.models import Category, Genre, Title, Review, Comment
from users.serializers import UserSerializer, CreateUserSerializer
from users.models import User


class GenreViewSet(CategoryGenreViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    lookup_field = 'slug'


class CategoryViewSet(CategoryGenreViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')).order_by('name')
    permission_classes = [ReadOnly | IsAdminUser]
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()

    def get_queryset(self):
        return super().get_queryset().filter(
            title_id=self.kwargs.get('title_id'))

    def get_permissions(self):
        if self.action == 'create':
            return (IsAuthenticated(),)
        elif self.action == 'list' or self.action == 'retrieve':
            return (AllowAny(),)
        else:
            return (AuthorOrStaff(),)

    def perform_create(self, serializer):
        title = get_object_or_404(
            Title,
            pk=self.kwargs['title_id']
        )
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerilizer
    queryset = Comment.objects.all()

    def get_queryset(self):
        return super().get_queryset().filter(
            review_id=self.kwargs.get('review_id'))

    def get_permissions(self):
        if self.request.method == 'GET':
            return (AllowAny(),)
        elif self.request.method == 'POST':
            return (IsAuthenticated(),)
        elif self.request.method == 'PATCH' or self.request.method == 'DELETE':
            return (AuthorOrStaff(),)

    def perform_create(self, serializer):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id)
        serializer.save(review=review, author=self.request.user)


class APIGetToken(APIView):
    def post(self):
        serializer = TokenSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user = get_object_or_404(username=data['username'])
        confirmation_code = data['confirmation_code']

        if default_token_generator.check_token(user, confirmation_code):
            token = RefreshToken.for_user(user).access_token
            return Response(
                {'token': str(token)},
                status=status.HTTP_201_CREATED
            )
        return Response(
            {'confirmation_code': 'Неверный код подтверждения!'},
            status=status.HTTP_400_BAD_REQUEST
        )


class SignUp(CreateAPIView):
    serializer_class = CreateUserSerializer

    def create(self, request, *args, **kwargs):
        username = request.data.get('username')
        email = request.data.get('email')
        if User.objects.filter(username=username, email=email).exists():
            send_confirmation_code(username, email)
            return Response(request.data, status=status.HTTP_200_OK)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        send_confirmation_code(username, email)
        return Response(serializer.data, status=HTTPStatus.OK)


def send_confirmation_code(username, email):
    user = get_object_or_404(User, email=email, username=username)
    confirmation_code = default_token_generator.make_token(user)
    user.confirmation_code = confirmation_code
    MESSAGE = (
        f'Здравствуйте, {username}!'
        f'Ваш код подтверждения: {user.confirmation_code}'
    )
    send_mail(
        message=MESSAGE,
        subject='Confirmation code',
        recipient_list=[user.email],
        from_email=settings.DEFAULT_FROM_EMAIL,
    )
    user.save()


class Token(CreateAPIView):
    serializer_class = TokenSerializer
    permission_classes = (AllowAny, )

    def create(self, request, *args, **kwargs):
        """Выдает токен."""
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(User,
                                 username=serializer.
                                 validated_data.get('username')
                                 )
        if (user.confirmation_code == serializer.validated_data.get(
                'confirmation_code')):
            return Response(
                {'token': str(AccessToken.for_user(user))},
                status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminUser,)
    filter_backends = (SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'
    http_method_names = ['get', 'post', 'head', 'patch', 'delete']

    @action(
        detail=False,
        permission_classes=(permissions.IsAuthenticated,))
    def me(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @me.mapping.patch
    def me_update(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(role=user.role, partial=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
