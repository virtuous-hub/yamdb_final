from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from reviews.constants import (LENGHT_NAME, LENGHT_SLUG, MAX_VALUE, MIN_VALUE,
                               SYMBOLS_IN_TITLE)
from users.models import User


class Category(models.Model):
    name = models.CharField('Название', max_length=LENGHT_NAME)
    slug = models.SlugField(
        max_length=LENGHT_SLUG,
        unique=True
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Категория'

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField('Название', max_length=LENGHT_NAME)
    slug = models.SlugField(
        max_length=LENGHT_SLUG,
        unique=True
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Жанр'

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField('Название', max_length=LENGHT_NAME)
    description = models.TextField('Описание')
    year = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MaxValueValidator(timezone.now().year)],
        verbose_name="Год выпуска")

    genre = models.ManyToManyField(
        Genre,
        through='GenreTitle',
        related_name='titles')

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=True,
        null=True)
    number_of_reviews = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['name']
        verbose_name = 'Произведение'

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    title = models.ForeignKey(
        Title,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name='Произведение'
    )
    genre = models.ForeignKey(
        Genre,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name='Жанр'
    )


class Review(models.Model):
    title = models.ForeignKey(Title,
                              on_delete=models.CASCADE,
                              related_name='reviews')
    text = models.TextField()
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='reviews')
    score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(MIN_VALUE),
                    MaxValueValidator(MAX_VALUE)],
        verbose_name='Рейтинг',
        help_text='Присвойте рейтинг от 1 до 10')
    pub_date = models.DateTimeField('Дата добавления',
                                    auto_now_add=True,
                                    db_index=True)

    class Meta:
        ordering = ['-pub_date']
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_title_author'
            )
        ]

    def __str__(self):
        return self.text[:SYMBOLS_IN_TITLE]


class Comment(models.Model):
    review = models.ForeignKey(Review,
                               on_delete=models.CASCADE,
                               related_name='comments')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='comments')
    text = models.TextField()
    pub_date = models.DateTimeField('Дата добавления',
                                    auto_now_add=True,
                                    db_index=True)

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.text[:SYMBOLS_IN_TITLE]
